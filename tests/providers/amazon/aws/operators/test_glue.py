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

import copy
from unittest import mock

import pytest

from airflow.configuration import conf
from airflow.models import DAG, DagRun, TaskInstance
from airflow.providers.amazon.aws.hooks.glue import GlueJobHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.utils import timezone

TASK_ID = "test_glue_operator"
DAG_ID = "test_dag_id"
JOB_NAME = "test_job_name"
DEFAULT_DATE = timezone.datetime(2017, 1, 1)

BASE_LOCATION = "some-bucket/{{ task_instance_key_str }}"
SCRIPT_LOCATION = f"s3://{BASE_LOCATION}/script-location.py"
CREATE_JOB_KWARGS = {
    "GlueVersion": "4.0",
    "Command": {
        "Name": "glueetl",
        "ScriptLocation": SCRIPT_LOCATION,
    },
    "WorkerType": "G.1X",
    "NumberOfWorkers": 2,
}
EXPECTED_BASE_LOCATION = f"some-bucket/{DAG_ID}__{TASK_ID}__20170101"


class TestGlueJobOperator:
    def setup_method(self):
        conf.load_test_config()

    def test_render_template(self):
        args = {"owner": "airflow", "start_date": DEFAULT_DATE}

        dag = DAG(DAG_ID, default_args=args)
        mock_operator = GlueJobOperator(
            task_id=TASK_ID, dag=dag, create_job_kwargs=CREATE_JOB_KWARGS, s3_bucket=BASE_LOCATION
        )

        dag_run = DagRun(dag_id=mock_operator.dag_id, execution_date=DEFAULT_DATE, run_id="test")
        ti = TaskInstance(task=mock_operator)
        ti.dag_run = dag_run
        ti.render_templates()

        expected_rendered_template = copy.deepcopy(CREATE_JOB_KWARGS)
        expected_rendered_template["Command"][
            "ScriptLocation"
        ] = f"s3://{EXPECTED_BASE_LOCATION}/script-location.py"

        assert expected_rendered_template == getattr(mock_operator, "create_job_kwargs")
        assert EXPECTED_BASE_LOCATION == getattr(mock_operator, "s3_bucket")

    @pytest.mark.parametrize(
        "script_location",
        [
            "s3://glue-examples/glue-scripts/sample_aws_glue_job.py",
            "/glue-examples/glue-scripts/sample_aws_glue_job.py",
        ],
    )
    @mock.patch.object(GlueJobHook, "print_job_logs")
    @mock.patch.object(GlueJobHook, "get_job_state")
    @mock.patch.object(GlueJobHook, "initialize_job")
    @mock.patch.object(GlueJobHook, "get_conn")
    @mock.patch.object(S3Hook, "load_file")
    def test_execute_without_failure(
        self,
        mock_load_file,
        mock_get_conn,
        mock_initialize_job,
        mock_get_job_state,
        mock_print_job_logs,
        script_location,
    ):
        glue = GlueJobOperator(
            task_id=TASK_ID,
            job_name=JOB_NAME,
            script_location=script_location,
            aws_conn_id="aws_default",
            region_name="us-west-2",
            s3_bucket="some_bucket",
            iam_role_name="my_test_role",
        )
        mock_initialize_job.return_value = {"JobRunState": "RUNNING", "JobRunId": "11111"}
        mock_get_job_state.return_value = "SUCCEEDED"

        glue.execute({})

        mock_initialize_job.assert_called_once_with({}, {})
        mock_print_job_logs.assert_not_called()
        assert glue.job_name == JOB_NAME

    @mock.patch.object(GlueJobHook, "print_job_logs")
    @mock.patch.object(GlueJobHook, "get_job_state")
    @mock.patch.object(GlueJobHook, "initialize_job")
    @mock.patch.object(GlueJobHook, "get_conn")
    @mock.patch.object(S3Hook, "load_file")
    def test_execute_with_verbose_logging(
        self, mock_load_file, mock_get_conn, mock_initialize_job, mock_get_job_state, mock_print_job_logs
    ):
        job_run_id = "11111"
        glue = GlueJobOperator(
            task_id=TASK_ID,
            job_name=JOB_NAME,
            script_location="s3_uri",
            s3_bucket="bucket_name",
            iam_role_name="role_arn",
            verbose=True,
        )
        mock_initialize_job.return_value = {"JobRunState": "RUNNING", "JobRunId": job_run_id}
        mock_get_job_state.return_value = "SUCCEEDED"

        glue.execute({})

        mock_initialize_job.assert_called_once_with({}, {})
        mock_print_job_logs.assert_called_once_with(
            job_name=JOB_NAME,
            run_id=job_run_id,
            job_failed=False,
            next_token=None,
        )
        assert glue.job_name == JOB_NAME

    @mock.patch.object(GlueJobHook, "print_job_logs")
    @mock.patch.object(GlueJobHook, "job_completion")
    @mock.patch.object(GlueJobHook, "initialize_job")
    @mock.patch.object(GlueJobHook, "get_conn")
    @mock.patch.object(S3Hook, "load_file")
    def test_execute_without_waiting_for_completion(
        self, mock_load_file, mock_get_conn, mock_initialize_job, mock_job_completion, mock_print_job_logs
    ):
        glue = GlueJobOperator(
            task_id=TASK_ID,
            job_name=JOB_NAME,
            script_location="s3://glue-examples/glue-scripts/sample_aws_glue_job.py",
            aws_conn_id="aws_default",
            region_name="us-west-2",
            s3_bucket="some_bucket",
            iam_role_name="my_test_role",
            wait_for_completion=False,
        )
        mock_initialize_job.return_value = {"JobRunState": "RUNNING", "JobRunId": "11111"}

        job_run_id = glue.execute({})

        mock_initialize_job.assert_called_once_with({}, {})
        mock_job_completion.assert_not_called()
        mock_print_job_logs.assert_not_called()
        assert glue.job_name == JOB_NAME
        assert job_run_id == "11111"
