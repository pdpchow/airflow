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
import warnings
from typing import Optional

from airflow.models import BaseOperator
from airflow.providers.tableau.hooks.tableau import TableauHook, TableauJobFinishCode
from airflow.providers.tableau.sensors.tableau_job_status import TableauJobFailedException

warnings.warn(
    """
    Deprecated class for refresh tableau workbooks. please use
    airflow.providers.tableau.operators.tableau.TableauOperator instead
    """,
    DeprecationWarning,
    stacklevel=2,
)


class TableauRefreshWorkbookOperator(BaseOperator):
    """
    Deprecated class for refresh tableau workbooks. please use
    airflow.providers.tableau.operators.tableau.TableauOperator instead

    Refreshes a Tableau Workbook/Extract

    .. seealso:: https://tableau.github.io/server-client-python/docs/api-ref#workbooks

    :param workbook_name: The name of the workbook to refresh.
    :type workbook_name: str
    :param site_id: The id of the site where the workbook belongs to.
    :type site_id: Optional[str]
    :param blocking: Defines if the job waits until the refresh has finished.
        Default: True.
    :type blocking: bool
    :param tableau_conn_id: The :ref:`Tableau Connection id <howto/connection:tableau>`
        containing the credentials to authenticate to the Tableau Server. Default:
        'tableau_default'.
    :type tableau_conn_id: str
    """

    def __init__(
        self,
        *,
        workbook_name: str,
        site_id: Optional[str] = None,
        blocking: bool = True,
        tableau_conn_id: str = 'tableau_default',
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.workbook_name = workbook_name
        self.site_id = site_id
        self.blocking = blocking
        self.tableau_conn_id = tableau_conn_id

    def execute(self, context: dict) -> str:
        """
        Executes the Tableau Extract Refresh and pushes the job id to xcom.

        :param context: The task context during execution.
        :type context: dict
        :return: the id of the job that executes the extract refresh
        :rtype: str
        """
        with TableauHook(self.site_id, self.tableau_conn_id) as tableau_hook:

            job_id = TableauOperator(
                resource='workbooks',
                method='refresh',
                find=self.workbook_name,
                match_with='name',
                site_id=self.site_id,
                tableau_conn_id=self.tableau_conn_id,
                blocking_refresh=self.blocking,
                task_id='refresh_workbook',
                dag=None,
            ).execute(context={})

            return job_id
