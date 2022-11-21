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
from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Iterator, NamedTuple

from sqlalchemy import func

from airflow.ti_deps.dep_context import DepContext
from airflow.ti_deps.deps.base_ti_dep import BaseTIDep, TIDepStatus
from airflow.utils.state import TaskInstanceState
from airflow.utils.trigger_rule import TriggerRule as TR

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from airflow.models.taskinstance import TaskInstance


class _UpstreamTIStates(NamedTuple):
    """States of the upstream tis for a specific ti.

    This is used to determine whether the specific ti can run in this iteration.
    """

    success: int
    skipped: int
    failed: int
    upstream_failed: int
    removed: int
    done: int

    @classmethod
    def calculate(cls, ti: TaskInstance, finished_tis: list[TaskInstance]) -> _UpstreamTIStates:
        """Calculate states for a task instance.

        :param ti: the ti that we want to calculate deps for
        :param finished_tis: all the finished tasks of the dag_run
        """
        task = ti.task
        counter = Counter(ti.state for ti in finished_tis if ti.task_id in task.upstream_task_ids)
        return _UpstreamTIStates(
            counter.get(TaskInstanceState.SUCCESS, 0),
            counter.get(TaskInstanceState.SKIPPED, 0),
            counter.get(TaskInstanceState.FAILED, 0),
            counter.get(TaskInstanceState.UPSTREAM_FAILED, 0),
            counter.get(TaskInstanceState.REMOVED, 0),
            sum(counter.values()),
        )


class TriggerRuleDep(BaseTIDep):
    """
    Determines if a task's upstream tasks are in a state that allows a given task instance
    to run.
    """

    NAME = "Trigger Rule"
    IGNORABLE = True
    IS_TASK_DEP = True

    def _get_dep_statuses(
        self,
        ti: TaskInstance,
        session: Session,
        dep_context: DepContext,
    ) -> Iterator[TIDepStatus]:
        # Checking that all upstream dependencies have succeeded
        if not ti.task.upstream_list:
            yield self._passing_status(reason="The task instance did not have any upstream tasks.")
            return

        if ti.task.trigger_rule == TR.ALWAYS:
            yield self._passing_status(reason="The task had a always trigger rule set.")
            return

        yield from self._evaluate_trigger_rule(ti=ti, dep_context=dep_context, session=session)

    @staticmethod
    def _count_upstreams(ti: TaskInstance, *, session: Session):
        from airflow.models.taskinstance import TaskInstance

        # Optimization: Don't need to hit the database if no upstreams are mapped.
        upstream_task_ids = ti.task.upstream_task_ids
        if ti.task.dag and not any(ti.task.dag.get_task(tid).is_mapped for tid in upstream_task_ids):
            return len(upstream_task_ids)

        # We don't naively count task instances because it is not guaranteed
        # that all upstreams have been created in the database at this point.
        # Instead, we look for already-expanded tasks, and add them to the raw
        # task count without considering mapping.
        mapped_tis_addition = (
            session.query(func.count())
            .filter(
                TaskInstance.dag_id == ti.dag_id,
                TaskInstance.run_id == ti.run_id,
                TaskInstance.task_id.in_(upstream_task_ids),
                TaskInstance.map_index > 0,
            )
            .scalar()
        )
        return len(upstream_task_ids) + mapped_tis_addition

    def _evaluate_trigger_rule(
        self,
        ti: TaskInstance,
        dep_context: DepContext,
        session: Session,
    ) -> Iterator[TIDepStatus]:
        """Evaluate whether ``ti``'s trigger rule was met.

        :param ti: Task instance to evaluate the trigger rule of.
        :param dep_context: The current dependency context.
        :param session: Database session.
        """
        finished_tis = dep_context.ensure_finished_tis(ti.get_dagrun(session), session)
        upstream_states = _UpstreamTIStates.calculate(ti, finished_tis)

        success = upstream_states.success
        skipped = upstream_states.skipped
        failed = upstream_states.failed
        upstream_failed = upstream_states.upstream_failed
        removed = upstream_states.removed
        done = upstream_states.done

        task = ti.task
        trigger_rule = task.trigger_rule
        upstream = self._count_upstreams(ti, session=session)
        upstream_done = done >= upstream

        changed = False
        if dep_context.flag_upstream_failed:
            if trigger_rule == TR.ALL_SUCCESS:
                if upstream_failed or failed:
                    changed = ti.set_state(TaskInstanceState.UPSTREAM_FAILED, session)
                elif skipped:
                    changed = ti.set_state(TaskInstanceState.SKIPPED, session)
                elif removed and success and ti.map_index > -1:
                    if ti.map_index >= success:
                        changed = ti.set_state(TaskInstanceState.REMOVED, session)
            elif trigger_rule == TR.ALL_FAILED:
                if success or skipped:
                    changed = ti.set_state(TaskInstanceState.SKIPPED, session)
            elif trigger_rule == TR.ONE_SUCCESS:
                if upstream_done and done == skipped:
                    # if upstream is done and all are skipped mark as skipped
                    changed = ti.set_state(TaskInstanceState.SKIPPED, session)
                elif upstream_done and success <= 0:
                    # if upstream is done and there are no success mark as upstream failed
                    changed = ti.set_state(TaskInstanceState.UPSTREAM_FAILED, session)
            elif trigger_rule == TR.ONE_FAILED:
                if upstream_done and not (failed or upstream_failed):
                    changed = ti.set_state(TaskInstanceState.SKIPPED, session)
            elif trigger_rule == TR.ONE_DONE:
                if upstream_done and not (failed or success):
                    changed = ti.set_state(TaskInstanceState.SKIPPED, session)
            elif trigger_rule == TR.NONE_FAILED:
                if upstream_failed or failed:
                    changed = ti.set_state(TaskInstanceState.UPSTREAM_FAILED, session)
            elif trigger_rule == TR.NONE_FAILED_MIN_ONE_SUCCESS:
                if upstream_failed or failed:
                    changed = ti.set_state(TaskInstanceState.UPSTREAM_FAILED, session)
                elif skipped == upstream:
                    changed = ti.set_state(TaskInstanceState.SKIPPED, session)
            elif trigger_rule == TR.NONE_SKIPPED:
                if skipped:
                    changed = ti.set_state(TaskInstanceState.SKIPPED, session)
            elif trigger_rule == TR.ALL_SKIPPED:
                if success or failed:
                    changed = ti.set_state(TaskInstanceState.SKIPPED, session)

        if changed:
            dep_context.have_changed_ti_states = True

        if trigger_rule == TR.ONE_SUCCESS:
            if success <= 0:
                yield self._failing_status(
                    reason=(
                        f"Task's trigger rule '{trigger_rule}' requires one upstream task success, "
                        f"but none were found. upstream_states={upstream_states}, "
                        f"upstream_task_ids={task.upstream_task_ids}"
                    )
                )
        elif trigger_rule == TR.ONE_FAILED:
            if not failed and not upstream_failed:
                yield self._failing_status(
                    reason=(
                        f"Task's trigger rule '{trigger_rule}' requires one upstream task failure, "
                        f"but none were found. upstream_states={upstream_states}, "
                        f"upstream_task_ids={task.upstream_task_ids}"
                    )
                )
        elif trigger_rule == TR.ONE_DONE:
            if success + failed <= 0:
                yield self._failing_status(
                    reason=(
                        f"Task's trigger rule '{trigger_rule}'"
                        "requires at least one upstream task failure or success"
                        f"but none were failed or success. upstream_states={upstream_states}, "
                        f"upstream_task_ids={task.upstream_task_ids}"
                    )
                )
        elif trigger_rule == TR.ALL_SUCCESS:
            num_failures = upstream - success
            if ti.map_index > -1:
                num_failures -= removed
            if num_failures > 0:
                yield self._failing_status(
                    reason=(
                        f"Task's trigger rule '{trigger_rule}' requires all upstream tasks to have "
                        f"succeeded, but found {num_failures} non-success(es). "
                        f"upstream_states={upstream_states}, "
                        f"upstream_task_ids={task.upstream_task_ids}"
                    )
                )
        elif trigger_rule == TR.ALL_FAILED:
            num_success = upstream - failed - upstream_failed
            if ti.map_index > -1:
                num_success -= removed
            if num_success > 0:
                yield self._failing_status(
                    reason=(
                        f"Task's trigger rule '{trigger_rule}' requires all upstream tasks to have failed, "
                        f"but found {num_success} non-failure(s). "
                        f"upstream_states={upstream_states}, "
                        f"upstream_task_ids={task.upstream_task_ids}"
                    )
                )
        elif trigger_rule == TR.ALL_DONE:
            if not upstream_done:
                yield self._failing_status(
                    reason=(
                        f"Task's trigger rule '{trigger_rule}' requires all upstream tasks to have "
                        f"completed, but found {upstream_done} task(s) that were not done. "
                        f"upstream_states={upstream_states}, "
                        f"upstream_task_ids={task.upstream_task_ids}"
                    )
                )
        elif trigger_rule == TR.NONE_FAILED:
            num_failures = upstream - success - skipped
            if ti.map_index > -1:
                num_failures -= removed
            if num_failures > 0:
                yield self._failing_status(
                    reason=(
                        f"Task's trigger rule '{trigger_rule}' requires all upstream tasks to have "
                        f"succeeded or been skipped, but found {num_failures} non-success(es). "
                        f"upstream_states={upstream_states}, "
                        f"upstream_task_ids={task.upstream_task_ids}"
                    )
                )
        elif trigger_rule == TR.NONE_FAILED_MIN_ONE_SUCCESS:
            num_failures = upstream - success - skipped
            if ti.map_index > -1:
                num_failures -= removed
            if num_failures > 0:
                yield self._failing_status(
                    reason=(
                        f"Task's trigger rule '{trigger_rule}' requires all upstream tasks to have "
                        f"succeeded or been skipped, but found {num_failures} non-success(es). "
                        f"upstream_states={upstream_states}, "
                        f"upstream_task_ids={task.upstream_task_ids}"
                    )
                )
        elif trigger_rule == TR.NONE_SKIPPED:
            if not upstream_done or (skipped > 0):
                yield self._failing_status(
                    reason=(
                        f"Task's trigger rule '{trigger_rule}' requires all upstream tasks to not have been "
                        f"skipped, but found {skipped} task(s) skipped. "
                        f"upstream_states={upstream_states}, "
                        f"upstream_task_ids={task.upstream_task_ids}"
                    )
                )
        elif trigger_rule == TR.ALL_SKIPPED:
            num_non_skipped = upstream - skipped
            if num_non_skipped > 0:
                yield self._failing_status(
                    reason=(
                        f"Task's trigger rule '{trigger_rule}' requires all upstream tasks to have been "
                        f"skipped, but found {num_non_skipped} task(s) in non skipped state. "
                        f"upstream_states={upstream_states}, "
                        f"upstream_task_ids={task.upstream_task_ids}"
                    )
                )
        else:
            yield self._failing_status(reason=f"No strategy to evaluate trigger rule '{trigger_rule}'.")
