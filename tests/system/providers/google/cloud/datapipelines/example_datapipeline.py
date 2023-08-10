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

"""
Example Airflow DAG for testing Google DataPipelines Create Data Pipeline Operator.
"""
from __future__ import annotations

import os
from datetime import datetime

from airflow import models
from airflow.providers.google.cloud.operators.datapipeline import (
    RunDataPipelineOperator,
)

DAG_ID = "google-datapipeline"
DATA_PIPELINE_NAME = os.environ.get("DATA_PIPELINE_NAME", "example-datapipeline")
GCP_PROJECT_ID = os.environ.get("SYSTEM_TESTS_GCP_PROJECT", "example-project")

with models.DAG(
    DAG_ID,
    schedule="@once",
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example", "datapipeline"],
) as dag:
    # [START howto_operator_run_data_pipeline]
    run_data_pipeline = RunDataPipelineOperator(
        task_id="run_data_pipeline", data_pipeline_name=DATA_PIPELINE_NAME, project_id=GCP_PROJECT_ID
    )
    # [END howto_operator_run_data_pipeline]
    run_data_pipeline


from tests.system.utils import get_test_run  # noqa: E402

# Needed to run the example DAG with pytest (see: tests/system/README.md#run_via_pytest)
test_run = get_test_run(dag)
