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

"""Add map_index to SlaMiss

Revision ID: c65c10f6c311
Revises: 4eaab2fe6582
Create Date: 2022-03-10 22:39:54.462272

"""

import sqlalchemy as sa
from alembic import op


# # revision identifiers, used by Alembic.
# revision = 'c65c10f6c311'
# down_revision = '4eaab2fe6582'
# branch_labels = None
# depends_on = None
# airflow_version = '2.3.0'

"""
* Add run_id
* Add map_index
* Drop execution_date
* Add slamiss FK
"""
def upgrade():
    """Apply Add map_index to SlaMiss"""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sla_miss', schema=None) as batch_op:
        batch_op.add_column(sa.Column('run_id', sa.String(length=250), nullable=False))
        batch_op.add_column(sa.Column('map_index', sa.Integer(), server_default='-1', nullable=False))
        batch_op.create_foreign_key('sla_miss_ti_fkey', 'task_instance', ['dag_id', 'task_id', 'run_id', 'map_index'], ['dag_id', 'task_id', 'run_id', 'map_index'], ondelete='CASCADE')
        batch_op.drop_column('execution_date')

    # ### end Alembic commands ###


def downgrade():
    """Unapply Add map_index to SlaMiss"""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sla_miss', schema=None) as batch_op:
        batch_op.add_column(sa.Column('execution_date', sa.DATETIME(), nullable=False))
        batch_op.drop_constraint('sla_miss_ti_fkey', type_='foreignkey')
        batch_op.drop_column('map_index')
        batch_op.drop_column('run_id')

    # ### end Alembic commands ###
