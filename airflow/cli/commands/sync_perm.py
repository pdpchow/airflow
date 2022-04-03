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
"""Sync permission command"""
import click

from airflow.cli import airflow_cmd


@airflow_cmd.command("sync-perm")
@click.option("--include-dags", is_flag=True, help="If passed, DAG specific permissions will also be synced.")
def sync_perm(include_dags):
    """Update permissions for existing roles and optionally DAGs"""
    from airflow.www.app import cached_app

    appbuilder = cached_app().appbuilder
    print('Updating actions and resources for all existing roles')
    # Add missing permissions for all the Base Views _before_ syncing/creating roles
    appbuilder.add_permissions(update_perms=True)
    appbuilder.sm.sync_roles()
    if include_dags:
        print('Updating permission on all DAG views')
        appbuilder.sm.create_dag_specific_permissions()
