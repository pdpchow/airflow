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
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import unittest

from airflow.providers.google.cloud.transfers.vertica_to_gcs import VerticaToGoogleCloudStorageOperator

TABLES = {'vertica_to_gcs_operator', 'vertica_to_gcs_operator_empty'}

TASK_ID = 'test-vertica-to-gcs'
VERTICA_CONN_ID = 'vertica_default'
SQL = 'SELECT * FROM vertica_to_gcs_operator'
BUCKET = 'gs://test'
FILENAME = 'test_{}.ndjson'

ROWS = [('mock_row_content_1', 42), ('mock_row_content_2', 43), ('mock_row_content_3', 44)]
CURSOR_DESCRIPTION = (
    ('some_str', 0, None, None, None, None, None),
    ('some_num', 6, None, None, None, None, None),
)

NDJSON_LINES = [
    b'{"some_num": 42, "some_str": "mock_row_content_1"}\n',
    b'{"some_num": 43, "some_str": "mock_row_content_2"}\n',
    b'{"some_num": 44, "some_str": "mock_row_content_3"}\n',
]
SCHEMA_FILENAME = 'schema_test.json'
SCHEMA_JSON = (
    b'[{"mode": "NULLABLE", "name": "some_str", "type": "STRING"}, '
    b'{"mode": "NULLABLE", "name": "some_num", "type": "INTEGER"}]'
)


def mock_cursor_iterate():
    return iter(ROWS)


class VerticaToGoogleCloudStorageOperatorTest(unittest.TestCase):
    def test_init(self):
        """Test VerticaToGoogleCloudStorageOperator instance is properly initialized."""
        op = VerticaToGoogleCloudStorageOperator(task_id=TASK_ID, sql=SQL, bucket=BUCKET, filename=FILENAME)
        self.assertEqual(op.task_id, TASK_ID)
        self.assertEqual(op.sql, SQL)
        self.assertEqual(op.bucket, BUCKET)
        self.assertEqual(op.filename, FILENAME)

    @mock.patch('airflow.providers.google.cloud.transfers.vertica_to_gcs.VerticaHook')
    @mock.patch('airflow.providers.google.cloud.transfers.sql_to_gcs.GCSHook')
    def test_exec_success(self, gcs_hook_mock_class, vertica_hook_mock_class):
        """Test the execute function in case where the run is successful."""

        vertica_hook_mock = vertica_hook_mock_class.return_value
        vertica_hook_mock.get_conn().cursor().iterate = mock_cursor_iterate
        vertica_hook_mock.get_conn().cursor().description = CURSOR_DESCRIPTION

        op = VerticaToGoogleCloudStorageOperator(
            task_id=TASK_ID, vertica_conn_id=VERTICA_CONN_ID, sql=SQL, bucket=BUCKET, filename=FILENAME
        )

        gcs_hook_mock = gcs_hook_mock_class.return_value

        def _assert_upload(bucket, obj, tmp_filename, mime_type, gzip):
            self.assertEqual(BUCKET, bucket)
            self.assertEqual(FILENAME.format(0), obj)
            self.assertEqual('application/json', mime_type)
            self.assertFalse(gzip)
            with open(tmp_filename, 'rb') as file:
                self.assertEqual(b''.join(NDJSON_LINES), file.read())

        gcs_hook_mock.upload.side_effect = _assert_upload

        op.execute(None)

    @mock.patch('airflow.providers.google.cloud.transfers.vertica_to_gcs.VerticaHook')
    @mock.patch('airflow.providers.google.cloud.transfers.sql_to_gcs.GCSHook')
    def test_file_splitting(self, gcs_hook_mock_class, vertica_hook_mock_class):
        """Test that ndjson is split by approx_max_file_size_bytes param."""

        vertica_hook_mock = vertica_hook_mock_class.return_value
        vertica_hook_mock.get_conn().cursor().iterate = mock_cursor_iterate
        vertica_hook_mock.get_conn().cursor().description = CURSOR_DESCRIPTION

        gcs_hook_mock = gcs_hook_mock_class.return_value
        expected_upload = {
            FILENAME.format(0): b''.join(NDJSON_LINES[:2]),
            FILENAME.format(1): NDJSON_LINES[2],
        }

        def _assert_upload(bucket, obj, tmp_filename, mime_type, gzip):
            self.assertEqual(BUCKET, bucket)
            self.assertEqual('application/json', mime_type)
            self.assertFalse(gzip)
            with open(tmp_filename, 'rb') as file:
                self.assertEqual(expected_upload[obj], file.read())

        gcs_hook_mock.upload.side_effect = _assert_upload

        op = VerticaToGoogleCloudStorageOperator(
            task_id=TASK_ID,
            sql=SQL,
            bucket=BUCKET,
            filename=FILENAME,
            approx_max_file_size_bytes=len(expected_upload[FILENAME.format(0)]),
        )
        op.execute(None)

    @mock.patch('airflow.providers.google.cloud.transfers.vertica_to_gcs.VerticaHook')
    @mock.patch('airflow.providers.google.cloud.transfers.sql_to_gcs.GCSHook')
    def test_schema_file(self, gcs_hook_mock_class, vertica_hook_mock_class):
        """Test writing schema files."""

        vertica_hook_mock = vertica_hook_mock_class.return_value
        vertica_hook_mock.get_conn().cursor().iterate = mock_cursor_iterate
        vertica_hook_mock.get_conn().cursor().description = CURSOR_DESCRIPTION

        gcs_hook_mock = gcs_hook_mock_class.return_value

        def _assert_upload(bucket, obj, tmp_filename, mime_type, gzip):  # pylint: disable=unused-argument
            if obj == SCHEMA_FILENAME:
                with open(tmp_filename, 'rb') as f:
                    self.assertEqual(SCHEMA_JSON, f.read())

        gcs_hook_mock.upload.side_effect = _assert_upload

        op = VerticaToGoogleCloudStorageOperator(
            task_id=TASK_ID, sql=SQL, bucket=BUCKET, filename=FILENAME, schema_filename=SCHEMA_FILENAME
        )
        op.execute(None)

        # once for the file and once for the schema
        self.assertEqual(2, gcs_hook_mock.upload.call_count)
