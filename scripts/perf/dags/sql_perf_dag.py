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

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

default_args = {
    "owner": "Airflow",
    "depends_on_past": False,
    "start_date": datetime(year=2020, month=1, day=13),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

_FIRST_LEVEL_TASKS = 10
_SECOND_LEVEL_TASKS = 10
DAG_ID = f"big_dag_{_FIRST_LEVEL_TASKS}-{_SECOND_LEVEL_TASKS}"

dag = DAG(
    DAG_ID,
    default_args=default_args,
    catchup=True,
    schedule_interval=timedelta(minutes=1),
    is_paused_upon_creation=False,
)


def print_context(ds, ti, **kwargs):
    print("Running %s %s", ti.task_id, ti.execution_date)
    return "Whatever you return gets printed in the logs"


def generate_parallel_tasks(name_prefix, num_of_tasks, deps):
    tasks = []
    for t_id in range(num_of_tasks):
        run_this = PythonOperator(
            task_id="%s_%s" % (name_prefix, t_id),
            python_callable=print_context,
            dag=dag,
        )
        run_this.set_upstream(deps)
        tasks.append(run_this)
    return tasks


zero_level_tasks = generate_parallel_tasks("l0", 1, [])
first_level_tasks = generate_parallel_tasks("l1", _FIRST_LEVEL_TASKS, zero_level_tasks)
second_level_tasks = generate_parallel_tasks(
    "l2", _SECOND_LEVEL_TASKS, first_level_tasks
)
