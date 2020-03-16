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

"""Increase connection.extra field size

Revision ID: 7ba99d720ac4
Revises: 852ae6c715af
Create Date: 2020-03-15 20:27:55.013805

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7ba99d720ac4'
down_revision = '852ae6c715af'
branch_labels = None
depends_on = None


def upgrade():
    # commands auto generated by Alembic - please adjust! ###
    op.alter_column('connection', 'extra',
                    existing_type=sa.VARCHAR(length=5000),
                    type_=sa.String(length=10000),
                    existing_nullable=False)
    # end Alembic commands ###


def downgrade():
    # commands auto generated by Alembic - please adjust! ###
    op.alter_column('connection', 'extra',
                    existing_type=sa.String(length=10000),
                    type_=sa.VARCHAR(length=5000),
                    existing_nullable=False)
    # end Alembic commands ###
