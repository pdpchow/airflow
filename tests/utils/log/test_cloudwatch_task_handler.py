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
from unittest import mock
from unittest.mock import call
from watchtower import CloudWatchLogHandler

from airflow.models import DAG, TaskInstance
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.amazon.aws.hooks.logs import AwsLogsHook
from airflow.utils.log.cloudwatch_task_handler import CloudwatchTaskHandler
from airflow.utils.state import State
from airflow.utils.timezone import datetime

try:
    import boto3
    import moto
    from moto import mock_logs
except ImportError:
    mock_logs = None


@unittest.skipIf(mock_logs is None,
                 "Skipping test because moto.mock_logs is not available")
@mock_logs
class TestCloudwatchTaskHandler(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.remote_log_group = 'log_group_name'
        self.region_name = 'us-west-2'
        self.local_log_location = 'local/log/location'
        self.filename_template = '{dag_id}/{task_id}/{execution_date}/{try_number}.log'
        self.cloudwatch_task_handler = CloudwatchTaskHandler(
            self.local_log_location,
            self.remote_log_group,
            self.region_name,
            self.filename_template
        )

        date = datetime(2020, 1, 1)
        dag_id = 'dag_for_testing_file_task_handler'
        task_id = 'task_for_testing_file_log_handler'
        self.dag = DAG(dag_id=dag_id, start_date=date)
        task = DummyOperator(task_id=task_id, dag=self.dag)
        self.ti = TaskInstance(task=task, execution_date=date)
        self.ti.try_number = 1
        self.ti.state = State.RUNNING

        self.remote_log_stream = '{}/{}/{}/{}.log'.format(
            dag_id, task_id, date.isoformat(), self.ti.try_number
        ).replace(':', '_')

        moto.core.moto_api_backend.reset()
        self.conn = boto3.client('logs', region_name=self.region_name)

    def tearDown(self):
        self.cloudwatch_task_handler.handler = None

    def test_hook(self):
        self.assertIsInstance(self.cloudwatch_task_handler.hook, AwsLogsHook)

    def test_hook_raises(self):
        handler = self.cloudwatch_task_handler
        with mock.patch.object(handler.log, 'error') as mock_error:
            with mock.patch("airflow.providers.amazon.aws.hooks.logs.AwsLogsHook") as mock_hook:
                mock_hook.side_effect = Exception('Failed to connect')
                # Initialize the hook
                handler.hook

            mock_error.assert_called_once_with(
                'Could not create an AwsLogsHook with connection id "%s". Please make '
                'sure that airflow[aws] is installed and the Cloudwatch logs connection exists.',
                ''
            )

    def test_handler(self):
        self.cloudwatch_task_handler.set_context(self.ti)
        self.assertIsInstance(self.cloudwatch_task_handler.handler, CloudWatchLogHandler)

    def test_write(self):
        handler = self.cloudwatch_task_handler
        handler.set_context(self.ti)
        messages = [str(i) for i in range(10)]

        with mock.patch("watchtower.CloudWatchLogHandler.emit") as mock_emit:
            [handler.handle(message) for message in messages]
            mock_emit.assert_has_calls([call(message) for message in messages])

    def test_read(self):
        generate_log_events(
            self.conn,
            self.remote_log_group,
            self.remote_log_stream,
            [
                {
                    'timestamp': 20000,
                    'message': 'Second'
                },
                {
                    'timestamp': 10000,
                    'message': 'First'
                },
                {
                    'timestamp': 30000,
                    'message': 'Third'
                },
            ]
        )

        expected = '*** Reading remote log from Cloudwatch log_group: {} log_stream: {}.\nFirst\nSecond\nThird\n'
        self.assertEqual(
            self.cloudwatch_task_handler.read(self.ti),
            ([expected.format(self.remote_log_group, self.remote_log_stream)], [{'end_of_log': True}])
        )

    def test_read_wrong_log_stream(self):
        generate_log_events(
            self.conn,
            self.remote_log_group,
            'alternate_log_stream',
            [
                {
                    'timestamp': 20000,
                    'message': 'Second'
                },
                {
                    'timestamp': 10000,
                    'message': 'First'
                },
                {
                    'timestamp': 30000,
                    'message': 'Third'
                },
            ]
        )

        msg_template = '*** Reading remote log from Cloudwatch log_group: {} log_stream: {}.\n{}\n'
        error_msg = 'Could not read remote logs from log_group: {} log_stream: {}.'.format(
            self.remote_log_group,
            self.remote_log_stream
        )
        self.assertEqual(
            self.cloudwatch_task_handler.read(self.ti),
            ([msg_template.format(self.remote_log_group, self.remote_log_stream, error_msg)], [{'end_of_log': True}])
        )

    def test_read_wrong_log_group(self):
        generate_log_events(
            self.conn,
            'alternate_log_group',
            self.remote_log_stream,
            [
                {
                    'timestamp': 20000,
                    'message': 'Second'
                },
                {
                    'timestamp': 10000,
                    'message': 'First'
                },
                {
                    'timestamp': 30000,
                    'message': 'Third'
                },
            ]
        )

        msg_template = '*** Reading remote log from Cloudwatch log_group: {} log_stream: {}.\n{}\n'
        error_msg = 'Could not read remote logs from log_group: {} log_stream: {}.'.format(
            self.remote_log_group,
            self.remote_log_stream
        )
        self.assertEqual(
            self.cloudwatch_task_handler.read(self.ti),
            ([msg_template.format(self.remote_log_group, self.remote_log_stream, error_msg)], [{'end_of_log': True}])
        )


def generate_log_events(conn, log_group_name, log_stream_name, log_events):
    conn.create_log_group(logGroupName=log_group_name)
    conn.create_log_stream(
        logGroupName=log_group_name,
        logStreamName=log_stream_name
    )
    conn.put_log_events(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
        logEvents=log_events
    )
