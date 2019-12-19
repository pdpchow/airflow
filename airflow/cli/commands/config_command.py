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
"""Config sub-commands"""
from airflow.configuration import conf
from airflow.models import Connection, Variable
from airflow.utils import cli as cli_utils, db


def show_config(args):
    """Show current application configuration"""
    config = conf.as_dict(display_sensitive=True, raw=True)

    for section_key, parameters in sorted(config.items()):
        print(f"[{section_key}]")
        for parameter_key, value in sorted(parameters.items()):
            print(f"{parameter_key}={value}")
        print()


@cli_utils.action_logging
def rotate_fernet_key(args):
    """Rotates all encrypted connection credentials and variables"""
    with db.create_session() as session:
        for conn in session.query(Connection).filter(
                Connection.is_encrypted | Connection.is_extra_encrypted):
            conn.rotate_fernet_key()
        for var in session.query(Variable).filter(Variable.is_encrypted):
            var.rotate_fernet_key()
