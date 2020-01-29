#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import getpass
from time import sleep
from typing import Optional

from redis import Redis
from sqlalchemy import Column, Index, Integer, String, and_, or_
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.session import make_transient

import airflow
from airflow import models
from airflow.configuration import conf
from airflow.exceptions import AirflowException
from airflow.executors.executor_loader import ExecutorLoader
from airflow.models.base import ID_LEN, Base
from airflow.stats import Stats
from airflow.utils import helpers, timezone
from airflow.utils.dag_processing import SimpleTaskInstance
from airflow.utils.helpers import convert_camel_to_snake
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.net import get_hostname
from airflow.utils.session import create_session, provide_session
from airflow.utils.sqlalchemy import UtcDateTime
from airflow.utils.state import State
from airflow.utils.types import DagRunType


class BaseJob(Base, LoggingMixin):
    """
    Abstract class to be derived for jobs. Jobs are processing items with state
    and duration that aren't task instances. For instance a BackfillJob is
    a collection of task instance runs, but should have its own state, start
    and end time.
    """

    __tablename__ = "job"

    id = Column(Integer, primary_key=True)
    dag_id = Column(String(ID_LEN), )
    state = Column(String(20))
    job_type = Column(String(30))
    start_date = Column(UtcDateTime())
    end_date = Column(UtcDateTime())
    """
    because this can be backed by sqlalchemy or redis, name is underscored so
    users can use get_heartbeat and update_heartbeat
    """
    _legacy_heartbeat = Column('latest_heartbeat', UtcDateTime())
    __table_args__ = (
        Index('job_type_heart', job_type, _legacy_heartbeat),
        Index('idx_job_state_heartbeat', state, _legacy_heartbeat),
    )
    executor_class = Column(String(500))
    hostname = Column(String(500))
    unixname = Column(String(1000))

    __mapper_args__ = {
        'polymorphic_on': job_type,
        'polymorphic_identity': 'BaseJob'
    }

    heartrate = conf.getfloat('scheduler', 'JOB_HEARTBEAT_SEC')
    if conf.getboolean('heartbeat', 'redis_enabled'):
        redis = Redis.from_url(conf.get('heartbeat', 'redis_url'))

    def __init__(
            self,
            executor=None,
            heartrate=None,
            *args,
            **kwargs):
        self.hostname = get_hostname()
        self.executor = executor or ExecutorLoader.get_default_executor()
        self.executor_class = executor.__class__.__name__
        self.start_date = timezone.utcnow()
        self.update_heartbeat(timezone.utcnow())
        if heartrate is not None:
            self.heartrate = heartrate
        self.unixname = getpass.getuser()
        self.max_tis_per_query = conf.getint('scheduler', 'max_tis_per_query')
        super().__init__(*args, **kwargs)

    @classmethod
    @provide_session
    def most_recent_job(cls, session=None) -> Optional['BaseJob']:
        """
        Return the most recent job of this type, if any, based on last
        heartbeat received.

        This method should be called on a subclass (i.e. on SchedulerJob) to
        return jobs of that type.

        :param session: Database session
        :rtype: BaseJob or None
        """
        if conf.getboolean('heartbeat', 'redis_enabled'):
            latest_id = cls.redis.zrange(cls.__name__, -1, -1)
            return latest_id and session.query(cls).get(int(latest_id))
        else:
            return session.query(cls).order_by(cls._legacy_heartbeat.desc()).limit(1).first()

    def is_alive(self, grace_multiplier=2.1):
        """
        Is this job currently alive.

        We define alive as in a state of RUNNING, and having sent a heartbeat
        within a multiple of the heartrate (default of 2.1)

        :param grace_multiplier: multiplier of heartrate to require heart beat
            within
        :type grace_multiplier: number
        :rtype: boolean
        """
        return (
            self.state == State.RUNNING and
            (timezone.utcnow() - self.latest_heartbeat).total_seconds() < self.heartrate * grace_multiplier
        )

    @provide_session
    def kill(self, session=None):
        """
        Handles on_kill callback and updates state in database.
        """
        job = session.query(BaseJob).filter(BaseJob.id == self.id).first()
        job.end_date = timezone.utcnow()
        try:
            self.on_kill()
        except Exception as e:  # pylint: disable=broad-except
            self.log.error('on_kill() method failed: %s', str(e))
        session.merge(job)
        session.commit()
        raise AirflowException("Job shut down externally.")

    def on_kill(self):
        """
        Will be called when an external kill command is received
        """

    def heartbeat_callback(self, session=None):
        """
        Callback that is called during heartbeat. This method should be overwritten.
        """

    def heartbeat(self):
        """
        Heartbeats update the job's entry in the database with a timestamp
        for the latest_heartbeat and allows for the job to be killed
        externally. This allows at the system level to monitor what is
        actually active.

        For instance, an old heartbeat for SchedulerJob would mean something
        is wrong.

        This also allows for any job to be killed externally, regardless
        of who is running it or on which machine it is running.

        Note that if your heart rate is set to 60 seconds and you call this
        method after 10 seconds of processing since the last heartbeat, it
        will sleep 50 seconds to complete the 60 seconds and keep a steady
        heart rate. If you go over 60 seconds before calling it, it won't
        sleep at all.
        """
        try:
            with create_session() as session:
                # This will cause it to load from the db
                session.merge(self)
                previous_heartbeat = self.get_heartbeat()

            if self.state == State.SHUTDOWN:
                self.kill()

            # Figure out how long to sleep for
            sleep_for = 0
            if previous_heartbeat:
                seconds_remaining = self.heartrate - \
                    (timezone.utcnow() - previous_heartbeat) \
                    .total_seconds()
                sleep_for = max(0, seconds_remaining)
            sleep(sleep_for)

            with create_session() as session:
                self.update_heartbeat(session=session)
                self.heartbeat_callback(session=session)
            self.log.debug('[heartbeat]')
        except OperationalError:
            Stats.incr(
                convert_camel_to_snake(self.__class__.__name__) + '_heartbeat_failure', 1,
                1)
            self.log.exception("%s heartbeat got an exception", self.__class__.__name__)

    def run(self):
        """
        Starts the job.
        """
        Stats.incr(self.__class__.__name__.lower() + '_start', 1, 1)
        # Adding an entry in the DB
        with create_session() as session:
            self.state = State.RUNNING
            session.add(self)
            session.commit()
            id_ = self.id
            make_transient(self)
            self.id = id_

            try:
                self._execute()
                # In case of max runs or max duration
                self.state = State.SUCCESS
            except SystemExit:
                # In case of ^C or SIGTERM
                self.state = State.SUCCESS
            except Exception:
                self.state = State.FAILED
                raise
            finally:
                self.end_date = timezone.utcnow()
                session.merge(self)
                session.commit()

        Stats.incr(self.__class__.__name__.lower() + '_end', 1, 1)

    def _execute(self):
        raise NotImplementedError("This method needs to be overridden")

    @provide_session
    def reset_state_for_orphaned_tasks(self, filter_by_dag_run=None, session=None):
        """
        This function checks if there are any tasks in the dagrun (or all)
        that have a scheduled state but are not known by the
        executor. If it finds those it will reset the state to None
        so they will get picked up again.
        The batch option is for performance reasons as the queries are made in
        sequence.

        :param filter_by_dag_run: the dag_run we want to process, None if all
        :type filter_by_dag_run: airflow.models.DagRun
        :return: the TIs reset (in expired SQLAlchemy state)
        :rtype: list[airflow.models.TaskInstance]
        """
        queued_tis = self.executor.queued_tasks
        # also consider running as the state might not have changed in the db yet
        running_tis = self.executor.running

        resettable_states = [State.SCHEDULED, State.QUEUED]
        TI = models.TaskInstance
        DR = models.DagRun
        if filter_by_dag_run is None:
            resettable_tis = (
                session
                .query(TI)
                .join(
                    DR,
                    and_(
                        TI.dag_id == DR.dag_id,
                        TI.execution_date == DR.execution_date))
                .filter(
                    DR.state == State.RUNNING,
                    DR.run_id.notlike(DagRunType.BACKFILL_JOB.value + '%'),
                    TI.state.in_(resettable_states))).all()
        else:
            resettable_tis = filter_by_dag_run.get_task_instances(state=resettable_states,
                                                                  session=session)
        tis_to_reset = []
        # Can't use an update here since it doesn't support joins
        for ti in resettable_tis:
            if ti.key not in queued_tis and ti.key not in running_tis:
                tis_to_reset.append(ti)

        if len(tis_to_reset) == 0:
            return []

        def query(result, items):
            if not items:
                return result

            filter_for_tis = TI.filter_for_tis(items)
            reset_tis = session.query(TI).filter(
                filter_for_tis, TI.state.in_(resettable_states)
            ).with_for_update().all()

            for ti in reset_tis:
                ti.state = State.NONE
                session.merge(ti)

            return result + reset_tis

        reset_tis = helpers.reduce_in_chunks(query,
                                             tis_to_reset,
                                             [],
                                             self.max_tis_per_query)

        task_instance_str = '\n\t'.join(
            [repr(x) for x in reset_tis])
        session.commit()

        self.log.info(
            "Reset the following %s TaskInstances:\n\t%s",
            len(reset_tis), task_instance_str
        )
        return reset_tis

    def update_heartbeat(self, session=None):
        if conf.getboolean('heartbeat', 'redis_enabled'):
            self.redis.zadd(
                self.job_type,
                {str(self.id): str(timezone.utcnow())})
        else:
            # Update last heartbeat time
            session.merge(self)
            self._legacy_heartbeat = timezone.utcnow()
            session.commit()

    def get_heartbeat(self):
        if conf.getboolean('heartbeat', 'redis_enabled'):
            redis_result = self.redis.zscore(self.job_type, str(self.id))
            return redis_result and timezone.parse(redis_result)
        else:
            return self._legacy_heartbeat

    @classmethod
    def get_zombie_running_tis(cls, limit_dttm, session=None):
        def batch_get(acc, items):
            lua_script = '''
                local scores = {}
                while #ARGV > 0 do
                    scores[#scores+1] = redis.call('ZSCORE', KEYS[1], table.remove(ARGV, 1))
                end
                return scores
            '''
            from airflow.jobs import LocalTaskJob
            return acc.update(cls.redis.register_script(lua_script)(LocalTaskJob.__name__, items))

        TI = airflow.models.TaskInstance

        if conf.getboolean('heartbeat', 'redis_enabled'):
            batch_size = conf.getint('heartbeat', 'redis_get_batch_size')
            ti_job = (
                session
                .query(TI, cls)
                .join(cls, TI.job_id == cls.id)
                .filter(TI.state == State.RUNNING)
                .all())
            job_id_to_ti_job = dict([(job.id, (ti, job)) for ti, job in ti_job])
            job_ids = job_id_to_ti_job.keys()
            heartbeats = helpers.reduce_in_chunks(batch_get, job_ids, {}, batch_size)
            zombie_tis = []
            for heartbeat, job_id in zip(heartbeats, job_ids):
                ti, job = job_id_to_ti_job[job_id]
                if (heartbeat and heartbeat < limit_dttm) or job.state != State.RUNNING:
                    zombie_tis.append(SimpleTaskInstance(ti))
            return zombie_tis
        else:
            tis = (
                session
                .query(TI)
                .join(cls, TI.job_id == cls.id)
                .filter(TI.state == State.RUNNING)
                .filter(
                    or_(
                        cls.state != State.RUNNING,
                        cls._legacy_heartbeat < limit_dttm,
                    )
                ).all()
            )
            return [SimpleTaskInstance(ti) for ti in tis]
