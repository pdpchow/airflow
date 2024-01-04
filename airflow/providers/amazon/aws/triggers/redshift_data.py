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

from typing import Any, AsyncIterator

from airflow.providers.amazon.aws.hooks.redshift_data import RedshiftDataHook
from airflow.triggers.base import BaseTrigger, TriggerEvent


class RedshiftDataTrigger(BaseTrigger):
    """
    RedshiftDataTrigger is fired as deferred class with params to run the task in triggerer.

    :param statement_id: the UUID of the statement
    :param task_id: task ID of the Dag
    :param poll_interval:  polling period in seconds to check for the status
    :param aws_conn_id: AWS connection ID for redshift
    :param region: aws region to use
    """

    def __init__(
        self,
        statement_id: str,
        task_id: str,
        poll_interval: int,
        aws_conn_id: str | None = "aws_default",
        region: str | None = None,
    ):
        super().__init__()
        self.statement_id = statement_id
        self.task_id = task_id
        self.aws_conn_id = aws_conn_id
        self.poll_interval = poll_interval
        self.region = region

    def serialize(self) -> tuple[str, dict[str, Any]]:
        """Serializes RedshiftDataTrigger arguments and classpath."""
        return (
            "airflow.providers.amazon.aws.triggers.redshift_data.RedshiftDataTrigger",
            {
                "statement_id": self.statement_id,
                "task_id": self.task_id,
                "aws_conn_id": self.aws_conn_id,
                "poll_interval": self.poll_interval,
                "region": self.region,
            },
        )

    async def run(self) -> AsyncIterator[TriggerEvent]:
        # hook = RedshiftDataHook(aws_conn_id=self.aws_conn_id, poll_interval=self.poll_interval)
        hook = RedshiftDataHook(aws_conn_id=self.aws_conn_id, region_name=self.region)
        try:
            response = await hook.check_query_is_finished_async(self.statement_id)
            if not response:
                response = {"status": "error", "message": f"{self.task_id} failed"}
            yield TriggerEvent(response)
        except Exception as e:
            yield TriggerEvent({"status": "error", "message": str(e)})
