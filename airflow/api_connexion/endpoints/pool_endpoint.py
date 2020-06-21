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
from flask import Response, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from airflow.api_connexion import parameters
from airflow.api_connexion.exceptions import AlreadyExists, BadRequest, NotFound
from airflow.api_connexion.schemas.pool_schema import PoolCollection, pool_collection_schema, pool_schema
from airflow.models.pool import Pool
from airflow.utils.session import provide_session


@provide_session
def delete_pool(pool_name: str, session):
    """
    Delete a pool
    """
    if session.query(Pool).filter(Pool.pool == pool_name).delete() == 0:
        raise NotFound(f"Pool with name:'{pool_name}' not found")
    return Response(status=204)


@provide_session
def get_pool(pool_name, session):
    """
    Get a pool
    """
    obj = session.query(Pool).filter(Pool.pool == pool_name).one_or_none()
    if obj is None:
        raise NotFound(f"Pool with name:'{pool_name}' not found")
    return pool_schema.dump(obj)


@provide_session
def get_pools(session):
    """
    Get all pools
    """
    offset = request.args.get(parameters.page_offset, 0)
    limit = min(int(request.args.get(parameters.page_limit, 100)), 100)

    total_entries = session.query(func.count(Pool.id)).scalar()
    pools = session.query(Pool).order_by(Pool.id).offset(offset).limit(limit).all()
    return pool_collection_schema.dump(
        PoolCollection(pools=pools, total_entries=total_entries)
    ).data


@provide_session
def patch_pool(pool_name, session, update_mask=None):
    """
    Update a pool
    """
    pool = session.query(Pool).filter(Pool.pool == pool_name).first()
    if not pool:
        raise NotFound(f"Pool with name:'{pool_name}' not found")

    patch_body = pool_schema.load(request.json).data
    if update_mask:
        update_mask = [i.strip() for i in update_mask]
        _patch_body = {}
        try:
            update_mask = [
                pool_schema.declared_fields[field].attribute
                if pool_schema.declared_fields[field].attribute
                else field
                for field in update_mask
            ]
        except KeyError as err:
            raise BadRequest(f"Invalid field: {err.args[0]} in update mask")
        _patch_body = {field: patch_body[field] for field in update_mask}
        patch_body = _patch_body

    for key, value in patch_body.items():
        setattr(pool, key, value)
    session.commit()
    return pool_schema.dump(pool)


@provide_session
def post_pool(session):
    """
    Create a pool
    """
    post_body = pool_schema.load(request.json, session=session).data
    pool = Pool(**post_body)
    try:
        session.add(pool)
        session.commit()
        return pool_schema.dump(pool)
    except IntegrityError:
        raise AlreadyExists(f"Pool: {post_body['pool']} already exists")
