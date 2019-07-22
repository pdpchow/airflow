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

from typing import Iterable

from airflow.exceptions import AirflowException
from airflow.hooks.base_hook import BaseHook
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults


class SqlSensor(BaseSensorOperator):
    """
    Runs a sql statement repeatedly until a criteria is met. It will keep trying until
    sql returns no rows, or if the first cell is in (0, '0', ''). Optional success
    and failure iterables are matched to the first cell returned. If success
    iterable is defined the sensor will keep retrying until the criteria is met.
    If failure iterable is defined and the criteria is met the sensor will raise AirflowException.
    Failure criteria is evaluated before success criteria. A fail_on_empty boolean can also
    be passed to the sensor in which case it will fail if no rows have been returned

    :param conn_id: The connection to run the sensor against
    :type conn_id: str
    :param sql: The sql to run. To pass, it needs to return at least one cell
        that contains a non-zero / empty string value.
    :type sql: str
    :param parameters: The parameters to render the SQL query with (optional).
    :type parameters: mapping or iterable
    :param success: Success criteria for the sensor
    :type: success: Optional<Iterable>
    :param failure: Failure criteria for the sensor
    :type: failure: Optional<Iterable>
    :param fail_on_empty: Explicitly fail on no rows returned
    :type: fail_on_empty: bool
    """
    template_fields = ('sql',)  # type: Iterable[str]
    template_ext = ('.hql', '.sql',)  # type: Iterable[str]
    ui_color = '#7c7287'

    @apply_defaults
    def __init__(self, conn_id, sql, parameters=None, success=None, failure=None, fail_on_empty=False, *args,
                 **kwargs):
        self.conn_id = conn_id
        self.sql = sql
        self.parameters = parameters
        self.success = success
        self.failure = failure
        self.fail_on_empty = fail_on_empty
        super(SqlSensor, self).__init__(*args, **kwargs)

    def poke(self, context):
        conn = BaseHook.get_connection(self.conn_id)

        allowed_conn_type = {'google_cloud_platform', 'jdbc', 'mssql',
                             'mysql', 'oracle', 'postgres',
                             'presto', 'sqlite', 'vertica'}
        if conn.conn_type not in allowed_conn_type:
            raise AirflowException("The connection type is not supported by SqlSensor. " +
                                   "Supported connection types: {}".format(list(allowed_conn_type)))
        hook = conn.get_hook()

        self.log.info('Poking: %s (with parameters %s)', self.sql, self.parameters)
        records = hook.get_records(self.sql, self.parameters)
        if not records:
            if self.fail_on_empty:
                raise AirflowException("No rows returned, raising as per fail_on_empty flag")
            else:
                return False
        first_cell = records[0][0]
        if self.failure is not None:
            if first_cell in self.failure:
                raise AirflowException(
                    "Failure criteria met. Value {} found in {}".format(first_cell, self.failure))
        if self.success is not None:
            if first_cell in self.success:
                return True
            else:
                return False
        return str(first_cell) not in ('0', '')
