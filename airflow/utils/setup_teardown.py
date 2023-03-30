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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from airflow.models.operator import Operator


class SetupTeardownContext:
    """Context manager for setup/teardown XComArg."""

    _context_managed_setup_task: Operator | None = None
    _previous_context_managed_setup_task: list[Operator] = []
    _context_managed_teardown_task: Operator | None = None
    _previous_context_managed_teardown_task: list[Operator] = []
    active: bool = False
    children: list[Operator] = []

    @classmethod
    def push_context_managed_setup_task(cls, task: Operator):
        if cls._context_managed_setup_task:
            cls._previous_context_managed_setup_task.append(cls._context_managed_setup_task)
        cls._context_managed_setup_task = task

    @classmethod
    def push_context_managed_teardown_task(cls, task: Operator):
        if cls._context_managed_teardown_task:
            cls._previous_context_managed_teardown_task.append(cls._context_managed_teardown_task)
        cls._context_managed_teardown_task = task

    @classmethod
    def pop_context_managed_setup_task(cls) -> Operator | None:
        old_setup_task = cls._context_managed_setup_task
        if cls._previous_context_managed_setup_task:
            cls._context_managed_setup_task = cls._previous_context_managed_setup_task.pop()
            if cls._context_managed_setup_task and old_setup_task:
                cls._context_managed_setup_task.set_downstream(old_setup_task)
        else:
            cls._context_managed_setup_task = None
        return old_setup_task

    @classmethod
    def pop_context_managed_teardown_task(cls) -> Operator | None:
        old_teardown_task = cls._context_managed_teardown_task
        if cls._previous_context_managed_teardown_task:
            cls._context_managed_teardown_task = cls._previous_context_managed_teardown_task.pop()
            if cls._context_managed_teardown_task and old_teardown_task:
                cls._context_managed_teardown_task.set_upstream(old_teardown_task)
        else:
            cls._context_managed_teardown_task = None
        return old_teardown_task

    @classmethod
    def get_context_managed_setup_task(cls) -> Operator | None:
        return cls._context_managed_setup_task

    @classmethod
    def get_context_managed_teardown_task(cls) -> Operator | None:
        return cls._context_managed_teardown_task

    @classmethod
    def push_setup_teardown_task(cls, operator):
        if operator._is_teardown:
            SetupTeardownContext.push_context_managed_teardown_task(operator)
            upstream_setup = [task for task in operator.upstream_list if task._is_setup]
            if upstream_setup:
                SetupTeardownContext.push_context_managed_setup_task(upstream_setup[-1])
        elif operator._is_setup:
            SetupTeardownContext.push_context_managed_setup_task(operator)
            downstream_teardown = [task for task in operator.downstream_list if task._is_teardown]
            if downstream_teardown:
                SetupTeardownContext.push_context_managed_teardown_task(downstream_teardown[0])

    @classmethod
    def set_work_task_roots_and_leaves(cls):
        normal_tasks = [task for task in cls.children if not task._is_setup and not task._is_teardown]
        setup_task = cls.get_context_managed_setup_task()
        teardown_task = cls.get_context_managed_teardown_task()
        for child in normal_tasks:
            if not child.downstream_list and teardown_task:
                child.set_downstream(teardown_task)
            if not child.upstream_list and setup_task:
                child.set_upstream(setup_task)
        cls.children = []
