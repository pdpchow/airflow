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

import freezegun
import pendulum
import pytest

from airflow.models import DagBag
from airflow.operators.empty import EmptyOperator
from airflow.utils.state import DagRunState
from airflow.utils.task_group import TaskGroup
from airflow.utils.types import DagRunType
from tests.test_utils.mock_operators import MockOperator

DAG_ID = 'test'
CURRENT_TIME = pendulum.DateTime(2021, 9, 7)


@pytest.fixture(autouse=True, scope="module")
def examples_dag_bag():
    # Speed up: We don't want example dags for this module
    return DagBag(include_examples=False, read_dags_from_db=True)


@pytest.fixture
def dag_without_runs(dag_maker, app, monkeypatch):
    with monkeypatch.context() as m:
        # Remove global operator links for this test
        m.setattr('airflow.plugins_manager.global_operator_extra_links', [])
        m.setattr('airflow.plugins_manager.operator_extra_links', [])
        m.setattr('airflow.plugins_manager.registered_operator_link_classes', {})

        with dag_maker(dag_id=DAG_ID, serialized=True):
            EmptyOperator(task_id="task1")
            with TaskGroup(group_id='group'):
                MockOperator.partial(task_id='mapped').expand(arg1=['a', 'b', 'c'])

        m.setattr(app, 'dag_bag', dag_maker.dagbag)
        yield dag_maker


@pytest.fixture
def dag_with_runs(dag_without_runs):
    with freezegun.freeze_time(CURRENT_TIME):
        date = dag_without_runs.dag.start_date
        run1 = dag_without_runs.create_dagrun(
            run_id="success", state=DagRunState.SUCCESS, run_type=DagRunType.SCHEDULED, execution_date=date
        )
        run2 = dag_without_runs.create_dagrun(
            run_id="not_run",
            run_type=DagRunType.SCHEDULED,
            execution_date=dag_without_runs.dag.next_dagrun_info(date).logical_date,
        )

        yield run1, run2


def test_no_runs(admin_client, dag_without_runs):
    resp = admin_client.get(f'/object/grid_data?dag_id={DAG_ID}', follow_redirects=True)
    assert resp.status_code == 200, resp.json
    assert resp.json == {
        'dag_runs': [],
        'groups': {
            'children': [
                {
                    'extra_links': [],
                    'id': 'task1',
                    'instances': [],
                    'is_mapped': False,
                    'label': 'task1',
                },
                {
                    'children': [
                        {
                            'extra_links': [],
                            'id': 'group.mapped',
                            'instances': [],
                            'is_mapped': True,
                            'label': 'mapped',
                        }
                    ],
                    'id': 'group',
                    'instances': [],
                    'label': 'group',
                    'tooltip': '',
                },
            ],
            'id': None,
            'instances': [],
            'label': None,
            'tooltip': '',
        },
    }


def test_one_run(admin_client, dag_with_runs):
    resp = admin_client.get(f'/object/grid_data?dag_id={DAG_ID}', follow_redirects=True)
    assert resp.status_code == 200, resp.json
    assert resp.json == {
        'dag_runs': [
            {
                'data_interval_end': '2016-01-02T00:00:00+00:00',
                'data_interval_start': '2016-01-01T00:00:00+00:00',
                'end_date': '2021-09-07T00:00:00+00:00',
                'execution_date': '2016-01-01T00:00:00+00:00',
                'last_scheduling_decision': None,
                'run_id': 'success',
                'run_type': 'scheduled',
                'start_date': '2016-01-01T00:00:00+00:00',
                'state': 'success',
            },
            {
                'data_interval_end': '2016-01-03T00:00:00+00:00',
                'data_interval_start': '2016-01-02T00:00:00+00:00',
                'end_date': None,
                'execution_date': '2016-01-02T00:00:00+00:00',
                'last_scheduling_decision': None,
                'run_id': 'not_run',
                'run_type': 'scheduled',
                'start_date': '2016-01-01T00:00:00+00:00',
                'state': 'running',
            },
        ],
        'groups': {
            'children': [
                {
                    'extra_links': [],
                    'id': 'task1',
                    'instances': [
                        {
                            'end_date': None,
                            'map_index': -1,
                            'run_id': 'success',
                            'start_date': None,
                            'state': None,
                            'task_id': 'task1',
                            'try_number': 1,
                        },
                        {
                            'end_date': None,
                            'map_index': -1,
                            'run_id': 'not_run',
                            'start_date': None,
                            'state': None,
                            'task_id': 'task1',
                            'try_number': 1,
                        },
                    ],
                    'is_mapped': False,
                    'label': 'task1',
                },
                {
                    'children': [
                        {
                            'extra_links': [],
                            'id': 'group.mapped',
                            'instances': [
                                {
                                    'end_date': None,
                                    'mapped_states': [None, None, None],
                                    'run_id': 'success',
                                    'start_date': None,
                                    'state': None,
                                    'task_id': 'group.mapped',
                                    'try_number': 1,
                                },
                                {
                                    'end_date': None,
                                    'mapped_states': [None, None, None],
                                    'run_id': 'not_run',
                                    'start_date': None,
                                    'state': None,
                                    'task_id': 'group.mapped',
                                    'try_number': 1,
                                },
                            ],
                            'is_mapped': True,
                            'label': 'mapped',
                        },
                    ],
                    'id': 'group',
                    'instances': [
                        {
                            'end_date': None,
                            'run_id': 'success',
                            'start_date': None,
                            'state': None,
                            'task_id': 'group',
                        },
                        {
                            'end_date': None,
                            'run_id': 'not_run',
                            'start_date': None,
                            'state': None,
                            'task_id': 'group',
                        },
                    ],
                    'label': 'group',
                    'tooltip': '',
                },
            ],
            'id': None,
            'instances': [
                {'end_date': None, 'run_id': 'success', 'start_date': None, 'state': None, 'task_id': None},
                {'end_date': None, 'run_id': 'not_run', 'start_date': None, 'state': None, 'task_id': None},
            ],
            'label': None,
            'tooltip': '',
        },
    }
