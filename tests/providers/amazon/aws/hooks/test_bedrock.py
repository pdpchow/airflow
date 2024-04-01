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

from unittest import mock

import pytest
from botocore.exceptions import ClientError

from airflow.providers.amazon.aws.hooks.bedrock import BedrockHook, BedrockRuntimeHook

JOB_NAME = "testJobName"
EXPECTED_STATUS = "InProgress"


@pytest.fixture
def mock_conn():
    with mock.patch.object(BedrockHook, "conn") as _conn:
        _conn.get_model_customization_job.return_value = {"jobName": JOB_NAME, "status": EXPECTED_STATUS}
        yield _conn


class TestBedrockHook:
    def setup_method(self):
        self.hook = BedrockHook()

        self.validation_exception_error = ClientError(
            error_response={"Error": {"Code": "ValidationException", "Message": ""}},
            operation_name="GetModelCustomizationJob",
        )

        self.unexpected_exception = ClientError(
            error_response={"Error": {"Code": "ExpiredTokenException", "Message": ""}},
            operation_name="GetModelCustomizationJob",
        )

    def test_conn_returns_a_boto3_connection(self):
        assert self.hook.conn is not None
        assert self.hook.conn.meta.service_model.service_name == "bedrock"

    def test_get_customize_model_job_state(self, mock_conn):
        response = self.hook.get_customize_model_job_state(JOB_NAME)

        mock_conn.get_model_customization_job.assert_called_once_with(jobIdentifier=JOB_NAME)
        assert response == EXPECTED_STATUS

    def test_job_name_exists_positive(self, mock_conn):
        response = self.hook.job_name_exists(JOB_NAME)

        mock_conn.get_model_customization_job.assert_called_once_with(jobIdentifier=JOB_NAME)
        assert response is True

    def test_job_name_exists_negative(self, mock_conn):
        invalid_job_name = "invalid_job_name"
        mock_conn.get_model_customization_job.side_effect = self.validation_exception_error

        response = self.hook.job_name_exists(invalid_job_name)

        mock_conn.get_model_customization_job.assert_called_once_with(jobIdentifier=invalid_job_name)
        assert response is False

    def test_job_name_exists_unexpected_exception(self, mock_conn):
        mock_conn.get_model_customization_job.side_effect = self.unexpected_exception

        with pytest.raises(ClientError):
            self.hook.job_name_exists(JOB_NAME)

        mock_conn.get_model_customization_job.assert_called_once_with(jobIdentifier=JOB_NAME)
from airflow.providers.amazon.aws.hooks.bedrock import BedrockRuntimeHook


class TestBedrockRuntimeHook:
    def test_conn_returns_a_boto3_connection(self):
        hook = BedrockRuntimeHook()

        assert hook.conn is not None
        assert hook.conn.meta.service_model.service_name == "bedrock-runtime"
