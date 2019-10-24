# -*- coding: utf-8 -*-
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

import unittest
from datetime import timedelta
from unittest.mock import MagicMock, patch

from airflow import DAG
from airflow.models import TaskInstance
from airflow.providers.aws.operators.emr import (
    EmrAddStepsOperator, EmrCreateJobFlowOperator, EmrTerminateJobFlowOperator,
)
from airflow.utils import timezone

DEFAULT_DATE = timezone.datetime(2017, 1, 1)


class TestEmrAddStepsOperator(unittest.TestCase):
    # When
    _config = [{
        'Name': 'test_step',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                '/usr/lib/spark/bin/run-example',
                '{{ macros.ds_add(ds, -1) }}',
                '{{ ds }}'
            ]
        }
    }]

    def setUp(self):
        args = {
            'owner': 'airflow',
            'start_date': DEFAULT_DATE
        }

        # Mock out the emr_client (moto has incorrect response)
        self.emr_client_mock = MagicMock()
        self.operator = EmrAddStepsOperator(
            task_id='test_task',
            job_flow_id='j-8989898989',
            aws_conn_id='aws_default',
            steps=self._config,
            dag=DAG('test_dag_id', default_args=args)
        )

    def test_init(self):
        self.assertEqual(self.operator.job_flow_id, 'j-8989898989')
        self.assertEqual(self.operator.aws_conn_id, 'aws_default')

    def test_render_template(self):
        ti = TaskInstance(self.operator, DEFAULT_DATE)
        ti.render_templates()

        expected_args = [{
            'Name': 'test_step',
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': [
                    '/usr/lib/spark/bin/run-example',
                    (DEFAULT_DATE - timedelta(days=1)).strftime("%Y-%m-%d"),
                    DEFAULT_DATE.strftime("%Y-%m-%d"),
                ]
            }
        }]

        self.assertListEqual(self.operator.steps, expected_args)

    def test_execute_returns_step_id(self):
        add_steps_success_return = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            },
            'StepIds': ['s-2LH3R5GW3A53T']
        }
        self.emr_client_mock.add_job_flow_steps.return_value = add_steps_success_return

        # Mock out the emr_client creator
        emr_session_mock = MagicMock()
        emr_session_mock.client.return_value = self.emr_client_mock
        self.boto3_session_mock = MagicMock(return_value=emr_session_mock)

        with patch('boto3.session.Session', self.boto3_session_mock):
            self.assertEqual(self.operator.execute(None), ['s-2LH3R5GW3A53T'])


class TestEmrCreateJobFlowOperator(unittest.TestCase):
    # When
    _config = {
        'Name': 'test_job_flow',
        'ReleaseLabel': '5.11.0',
        'Steps': [{
            'Name': 'test_step',
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': [
                    '/usr/lib/spark/bin/run-example',
                    '{{ macros.ds_add(ds, -1) }}',
                    '{{ ds }}'
                ]
            }
        }]
    }

    def setUp(self):
        args = {
            'owner': 'airflow',
            'start_date': DEFAULT_DATE
        }

        # Mock out the emr_client (moto has incorrect response)
        self.emr_client_mock = MagicMock()
        self.operator = EmrCreateJobFlowOperator(
            task_id='test_task',
            aws_conn_id='aws_default',
            emr_conn_id='emr_default',
            job_flow_overrides=self._config,
            region_name='ap-southeast-2',
            dag=DAG('test_dag_id', default_args=args)
        )

    def test_init(self):
        self.assertEqual(self.operator.aws_conn_id, 'aws_default')
        self.assertEqual(self.operator.emr_conn_id, 'emr_default')
        self.assertEqual(self.operator.region_name, 'ap-southeast-2')

    def test_render_template(self):
        ti = TaskInstance(self.operator, DEFAULT_DATE)
        ti.render_templates()

        expected_args = {
            'Name': 'test_job_flow',
            'ReleaseLabel': '5.11.0',
            'Steps': [{
                'Name': 'test_step',
                'ActionOnFailure': 'CONTINUE',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': [
                        '/usr/lib/spark/bin/run-example',
                        (DEFAULT_DATE - timedelta(days=1)).strftime("%Y-%m-%d"),
                        DEFAULT_DATE.strftime("%Y-%m-%d"),
                    ]
                }
            }]
        }

        self.assertDictEqual(self.operator.job_flow_overrides, expected_args)

    def test_execute_returns_job_id(self):
        run_job_flow_success_return = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            },
            'JobFlowId': 'j-8989898989'
        }
        self.emr_client_mock.run_job_flow.return_value = run_job_flow_success_return

        # Mock out the emr_client creator
        emr_session_mock = MagicMock()
        emr_session_mock.client.return_value = self.emr_client_mock
        self.boto3_session_mock = MagicMock(return_value=emr_session_mock)

        with patch('boto3.session.Session', self.boto3_session_mock):
            self.assertEqual(self.operator.execute(None), 'j-8989898989')


class TestEmrTerminateJobFlowOperator(unittest.TestCase):
    def setUp(self):
        # Mock out the emr_client (moto has incorrect response)
        mock_emr_client = MagicMock()

        terminate_success_return = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            }
        }
        mock_emr_client.terminate_job_flows.return_value = terminate_success_return

        mock_emr_session = MagicMock()
        mock_emr_session.client.return_value = mock_emr_client

        # Mock out the emr_client creator
        self.boto3_session_mock = MagicMock(return_value=mock_emr_session)

    def test_execute_terminates_the_job_flow_and_does_not_error(self):
        with patch('boto3.session.Session', self.boto3_session_mock):
            operator = EmrTerminateJobFlowOperator(
                task_id='test_task',
                job_flow_id='j-8989898989',
                aws_conn_id='aws_default'
            )

            operator.execute(None)


if __name__ == '__main__':
    unittest.main()
