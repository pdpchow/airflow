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
<<<<<<< HEAD
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import select
import subprocess
import time
import uuid

from apiclient.discovery import build

from airflow.contrib.hooks.gcp_api_base_hook import GoogleCloudBaseHook

_log = logging.getLogger(__name__)


class _DataflowJob(object):
    def __init__(self, dataflow, project_number, name):
        self._dataflow = dataflow
        self._project_number = project_number
        self._job_name = name
        self._job_id = None
        self._job = self._get_job()

    def _get_job_id_from_name(self):
        jobs = self._dataflow.projects().jobs().list(
            projectId=self._project_number
        ).execute()
        for job in jobs['jobs']:
            if job['name'] == self._job_name:
                self._job_id = job['id']
                return job
        return None

    def _get_job(self):
        if self._job_id is None:
            job = self._get_job_id_from_name()
        else:
            job = self._dataflow.projects().jobs().get(projectId=self._project_number,
                                                       jobId=self._job_id).execute()
        if 'currentState' in job:
            _log.info('Google Cloud DataFlow job %s is %s', job['name'],
                         job['currentState'])
        else:
            _log.info('Google Cloud DataFlow with job_id %s has name %s', self._job_id,
                         job['name'])
        return job

    def wait_for_done(self):
        while True:
            if 'currentState' in self._job:
                if 'JOB_STATE_DONE' == self._job['currentState']:
                    return True
                elif 'JOB_STATE_FAILED' == self._job['currentState']:
                    raise Exception("Google Cloud Dataflow job {} has failed.".format(
                        self._job['name']))
                elif 'JOB_STATE_CANCELLED' == self._job['currentState']:
                    raise Exception("Google Cloud Dataflow job {} was cancelled.".format(
                        self._job['name']))
                elif 'JOB_STATE_RUNNING' == self._job['currentState']:
                    time.sleep(10)
                else:
                    _log.debug(str(self._job))
                    raise Exception(
                        "Google Cloud Dataflow job {} was unknown state: {}".format(
                            self._job['name'], self._job['currentState']))
            else:
                time.sleep(15)

            self._job = self._get_job()

    def get(self):
        return self._job


class _DataflowJava(object):
    def __init__(self, cmd):
        self._proc = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

    def _line(self, fd):
        if fd == self._proc.stderr.fileno():
            line = self._proc.stderr.readline()
            return line
        if fd == self._proc.stdout.fileno():
            line = self._proc.stdout.readline()
            return line

    @staticmethod
    def _extract_job(line):
        if line is not None:
            if line.startswith("Submitted job: "):
                return line[15:-1]

    def wait_for_done(self):
        reads = [self._proc.stderr.fileno(), self._proc.stdout.fileno()]
        _log.info("Start waiting for DataFlow process to complete.")
        while self._proc.poll() is None:
            ret = select.select(reads, [], [], 5)
            if ret is not None:
                for fd in ret[0]:
                    line = self._line(fd)
                    _log.debug(line[:-1])
            else:
                _log.info("Waiting for DataFlow process to complete.")
        if self._proc.returncode is not 0:
            raise Exception("DataFlow jar failed with return code {}".format(
                self._proc.returncode))


class DataFlowHook(GoogleCloudBaseHook):
    def __init__(self,
                 gcp_conn_id='google_cloud_default',
                 delegate_to=None):
        super(DataFlowHook, self).__init__(gcp_conn_id, delegate_to)

    def get_conn(self):
        """
        Returns a Google Cloud Storage service object.
        """
        http_authorized = self._authorize()
        return build('dataflow', 'v1b3', http=http_authorized)

    def start_java_dataflow(self, task_id, variables, dataflow):
        name = task_id + "-" + str(uuid.uuid1())[:8]
        cmd = self._build_cmd(task_id, variables, dataflow, name)
        _DataflowJava(cmd).wait_for_done()
        _DataflowJob(self.get_conn(), variables['project'], name).wait_for_done()

    def _build_cmd(self, task_id, variables, dataflow, name):
        command = ["java", "-jar",
                   dataflow,
                   "--runner=DataflowPipelineRunner",
                   "--streaming=false",
                   "--jobName=" + name]

        if variables is not None:
            for attr, value in variables.iteritems():
                command.append("--" + attr + "=" + value)

        return command
=======
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""This module is deprecated. Please use `airflow.providers.google.cloud.hooks.dataflow`."""

import warnings

from airflow.providers.google.cloud.hooks.dataflow import DataflowHook

warnings.warn(
    "This module is deprecated. Please use `airflow.providers.google.cloud.hooks.dataflow`.",
    DeprecationWarning, stacklevel=2
)


class DataFlowHook(DataflowHook):
    """
    This class is deprecated. Please use `airflow.providers.google.cloud.hooks.dataflow.DataflowHook`.
    """
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "This class is deprecated. "
            "Please use `airflow.providers.google.cloud.hooks.dataflow.DataflowHook`.",
            DeprecationWarning, stacklevel=2
        )
        super().__init__(*args, **kwargs)
>>>>>>> 0d5ecde61bc080d2c53c9021af252973b497fb7d
