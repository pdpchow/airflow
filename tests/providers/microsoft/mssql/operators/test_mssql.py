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

import mock
from parameterized import parameterized

from airflow import PY38
from airflow.models import Connection
from airflow.providers.odbc.hooks.odbc import OdbcHook

if PY38:
    MsSqlHook = None
    MsSqlOperator = None
else:
    from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
    from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator


ODBC_CONN = Connection(conn_id='test-odbc', conn_type='odbc', )
PYMSSQL_CONN = Connection(conn_id='test-pymssql', conn_type='anything', )


@unittest.skipIf(PY38, "Mssql package not avaible when Python >= 3.8.")
class TestMsSqlOperator:
    @parameterized.expand([(ODBC_CONN, OdbcHook), (PYMSSQL_CONN, MsSqlHook)])
    @mock.patch('airflow.hooks.base_hook.BaseHook.get_connection')
    def test_get_hook(self, conn, hook_class, get_connection):
        """
        Operator should use odbc hook if conn type is ``odbc`` and pymssql-based hook otherwise.
        """

        get_connection.return_value = conn
        op = MsSqlOperator(task_id='test', sql='', mssql_conn_id=conn.conn_id)
        hook = op.get_hook()
        assert hook.__class__ == hook_class
