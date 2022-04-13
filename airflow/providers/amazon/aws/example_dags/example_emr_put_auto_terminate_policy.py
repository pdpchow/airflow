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
import os
from datetime import datetime

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.providers.amazon.aws.operators.emr import (
    EmrAddStepsOperator,
    EmrCreateJobFlowOperator,
    EmrAutoTerminatePolicyOperator
)
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor

JOB_FLOW_ROLE = os.getenv('EMR_JOB_FLOW_ROLE', 'EMR_EC2_DefaultRole')
SERVICE_ROLE = os.getenv('EMR_SERVICE_ROLE', 'EMR_DefaultRole')

SPARK_STEPS = [
    {
        'Name': 'calculate_pi',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': ['/usr/lib/spark/bin/run-example', 'SparkPi', '10'],
        },
    }
]

JOB_FLOW_OVERRIDES = {
    'Name': 'PiCalc',
    'ReleaseLabel': 'emr-6.4.0',
    'Applications': [{'Name': 'Spark'}],
    'Instances': {
        'InstanceGroups': [
            {
                'Name': 'Primary node',
                'Market': 'ON_DEMAND',
                'InstanceRole': 'MASTER',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 1,
            },
        ],
        'KeepJobFlowAliveWhenNoSteps': True,
        'TerminationProtected': False,
    },
    'JobFlowRole': JOB_FLOW_ROLE,
    'ServiceRole': SERVICE_ROLE,
}


with DAG(
    dag_id='example_emr_put_auto_terminate_policy',
    schedule_interval=None,
    start_date=datetime(2021, 1, 1),
    tags=['example'],
    catchup=False,
) as dag:

    cluster_creator = EmrCreateJobFlowOperator(
        task_id='create_job_flow',
        job_flow_overrides=JOB_FLOW_OVERRIDES,
    )

    # [START howto_operator_emr_auto_terminate_policy]
    put_auto_terminate = EmrAutoTerminatePolicyOperator(
        task_id='put_auto_terminate',
        job_flow_id=cluster_creator.output,
        idle_timeout=300
    )
    # [END howto_operator_emr_terminate_job_flow]

    # [START howto_operator_emr_add_steps]
    step_adder = EmrAddStepsOperator(
        task_id='add_steps',
        job_flow_id=cluster_creator.output,
        steps=SPARK_STEPS,
    )
    # [END howto_operator_emr_add_steps]

    # [START howto_sensor_emr_step_sensor]
    step_checker = EmrStepSensor(
        task_id='watch_step',
        job_flow_id=cluster_creator.output,
        step_id=step_adder.output[0],
    )
    # [END howto_sensor_emr_step_sensor]


    chain(
        cluster_creator,
        put_auto_terminate,
        step_adder,
        step_checker,
    )
