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

"""Add is_orphaned to DatasetModel

Revision ID: 290244fb8b83
Revises: 65a852f26899
Create Date: 2022-11-22 00:12:53.432961

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "290244fb8b83"
down_revision = "65a852f26899"
branch_labels = None
depends_on = None
airflow_version = "2.5.0"


def upgrade():
    """Add is_orphaned to DatasetModel"""
    # We pass in sa.sql.False_() for server_default, since that handles the string
    # representation of False for different databases for us
    # https://github.com/miguelgrinberg/Flask-Migrate/issues/265#issuecomment-937057519
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(
            sa.Column("is_orphaned", sa.Boolean, nullable=False, server_default=sa.sql.False_())
        )


def downgrade():
    """Remove is_orphaned from DatasetModel"""
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("is_orphaned")
