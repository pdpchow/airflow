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

import re
from random import randrange
from unittest import mock
from unittest.mock import MagicMock, Mock
import pytest

from airflow.exceptions import AirflowProviderDeprecationWarning
from airflow.models import TaskInstance
from airflow.models.dag import DAG
from airflow.utils import timezone
from airflow.providers.common.sql.hooks.sql import fetch_all_handler
try:
    from airflow.providers.teradata.operators.teradata import TeradataOperator
    from airflow.providers.teradata.hooks.teradata import TeradataHook
except ImportError:
    pytest.skip("Teradata not available", allow_module_level=True)

from airflow import AirflowException

DEFAULT_DATE = timezone.datetime(2015, 1, 1)
TEST_DAG_ID = "unit_test_dag"



class TestTeradataOperator:
    def setup_method(self):
        args = {"owner": "airflow", "start_date": DEFAULT_DATE}
        dag = DAG(TEST_DAG_ID, default_args=args)
        self.dag = dag

    @mock.patch("airflow.providers.common.sql.operators.sql.SQLExecuteQueryOperator.get_db_hook")
    def test_get_hook_from_conn(self, mock_get_db_hook):
        """
        :class:`~.MsSqlOperator` should use the hook returned by :meth:`airflow.models.Connection.get_hook`
        if one is returned.

        This behavior is necessary in order to support usage of :class:`~.OdbcHook` with this operator.

        Specifically we verify here that :meth:`~.MsSqlOperator.get_hook` returns the hook returned from a
        call of ``get_hook`` on the object returned from :meth:`~.BaseHook.get_connection`.
        """
        mock_hook = MagicMock()
        mock_get_db_hook.return_value = mock_hook

        op = TeradataOperator(task_id="test", sql="")
        assert op.get_db_hook() == mock_hook

    @mock.patch(
        "airflow.providers.common.sql.operators.sql.SQLExecuteQueryOperator.get_db_hook", autospec=TeradataHook
    )
    def test_get_hook_default(self, mock_get_db_hook):
        """
        If :meth:`airflow.models.Connection.get_hook` does not return a hook (e.g. because of an invalid
        conn type), then :class:`~.TeradataHook` should be used.
        """
        mock_get_db_hook.return_value.side_effect = Mock(side_effect=AirflowException())

        op = TeradataOperator(task_id="test", sql="")
        assert op.get_db_hook().__class__.__name__ == "TeradataHook"

    @mock.patch("airflow.providers.common.sql.operators.sql.SQLExecuteQueryOperator.get_db_hook")
    def test_execute(self, mock_get_db_hook):
        sql = "SELECT * FROM test_table"
        teradata_conn_id = "teradata_default"
        parameters = {"parameter": "value"}
        autocommit = False
        context = "test_context"
        task_id = "test_task_id"

        
        operator = TeradataOperator(
                sql=sql,
                conn_id=teradata_conn_id,
                parameters=parameters,
                task_id=task_id,
            )
        operator.execute(context=context)
        mock_get_db_hook.return_value.run.assert_called_once_with(
            sql=sql,
            autocommit=autocommit,
            parameters=parameters,
            handler=fetch_all_handler,
            return_last=True,
        )

    @mock.patch("airflow.providers.common.sql.operators.sql.SQLExecuteQueryOperator.get_db_hook")
    def test_teradata_operator_test_multi(self, mock_get_db_hook):
        sql = [
            "CREATE TABLE IF NOT EXISTS test_airflow (dummy VARCHAR(50))",
            "TRUNCATE TABLE test_airflow",
            "INSERT INTO test_airflow VALUES ('X')",
        ]
        teradata_conn_id = "teradata_default"
        parameters = {"parameter": "value"}
        autocommit = False
        context = "test_context"
        task_id = "test_task_id"
        
        operator = TeradataOperator(
                sql=sql,
                conn_id=teradata_conn_id,
                parameters=parameters,
                task_id=task_id,
            )
        operator.execute(context=context)
        mock_get_db_hook.return_value.run.assert_called_once_with(
            sql=sql,
            autocommit=autocommit,
            parameters=parameters,
            handler=fetch_all_handler,
            return_last=True,
        )
