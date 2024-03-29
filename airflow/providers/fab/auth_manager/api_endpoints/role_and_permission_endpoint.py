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

from http import HTTPStatus
from typing import TYPE_CHECKING, cast

from connexion import NoContent
from flask import request
from marshmallow import ValidationError
from sqlalchemy import asc, desc, func, select

from airflow.api_connexion.exceptions import AlreadyExists, BadRequest, NotFound
from airflow.api_connexion.parameters import check_limit, format_parameters
from airflow.api_connexion.schemas.role_and_permission_schema import (
    ActionCollection,
    RoleCollection,
    action_collection_schema,
    role_collection_schema,
    role_schema,
)
from airflow.api_connexion.security import requires_access_custom_view
from airflow.providers.fab.auth_manager.models import Action, Role
from airflow.providers.fab.auth_manager.security_manager.override import FabAirflowSecurityManagerOverride
from airflow.security import permissions
from airflow.www.extensions.init_auth_manager import get_auth_manager

if TYPE_CHECKING:
    from airflow.api_connexion.types import APIResponse, UpdateMask


def _check_action_and_resource(sm: FabAirflowSecurityManagerOverride, perms: list[tuple[str, str]]) -> None:
    """
    Check if the action or resource exists and otherwise raise 400.

    This function is intended for use in the REST API because it raises an HTTP error 400
    """
    for action, resource in perms:
        if not sm.get_action(action):
            raise BadRequest(detail=f"The specified action: {action!r} was not found")
        if not sm.get_resource(resource):
            raise BadRequest(detail=f"The specified resource: {resource!r} was not found")


@requires_access_custom_view("GET", permissions.RESOURCE_ROLE)
def get_role(*, role_name: str) -> APIResponse:
    """Get role."""
    security_manager = cast(FabAirflowSecurityManagerOverride, get_auth_manager().security_manager)
    role = security_manager.find_role(name=role_name)
    if not role:
        raise NotFound(title="Role not found", detail=f"Role with name {role_name!r} was not found")
    return role_schema.dump(role)


@requires_access_custom_view("GET", permissions.RESOURCE_ROLE)
@format_parameters({"limit": check_limit})
def get_roles(*, order_by: str = "name", limit: int, offset: int | None = None) -> APIResponse:
    """Get roles."""
    security_manager = cast(FabAirflowSecurityManagerOverride, get_auth_manager().security_manager)
    session = security_manager.get_session
    total_entries = session.scalars(select(func.count(Role.id))).one()
    direction = desc if order_by.startswith("-") else asc
    to_replace = {"role_id": "id"}
    order_param = order_by.strip("-")
    order_param = to_replace.get(order_param, order_param)
    allowed_sort_attrs = ["role_id", "name"]
    if order_by not in allowed_sort_attrs:
        raise BadRequest(
            detail=f"Ordering with '{order_by}' is disallowed or "
            f"the attribute does not exist on the model"
        )

    query = select(Role)
    roles = (
        session.scalars(query.order_by(direction(getattr(Role, order_param))).offset(offset).limit(limit))
        .unique()
        .all()
    )

    return role_collection_schema.dump(RoleCollection(roles=roles, total_entries=total_entries))


@requires_access_custom_view("GET", permissions.RESOURCE_ACTION)
@format_parameters({"limit": check_limit})
def get_permissions(*, limit: int, offset: int | None = None) -> APIResponse:
    """Get permissions."""
    security_manager = cast(FabAirflowSecurityManagerOverride, get_auth_manager().security_manager)
    session = security_manager.get_session
    total_entries = session.scalars(select(func.count(Action.id))).one()
    query = select(Action)
    actions = session.scalars(query.offset(offset).limit(limit)).all()
    return action_collection_schema.dump(ActionCollection(actions=actions, total_entries=total_entries))


@requires_access_custom_view("DELETE", permissions.RESOURCE_ROLE)
def delete_role(*, role_name: str) -> APIResponse:
    """Delete a role."""
    security_manager = cast(FabAirflowSecurityManagerOverride, get_auth_manager().security_manager)

    role = security_manager.find_role(name=role_name)
    if not role:
        raise NotFound(title="Role not found", detail=f"Role with name {role_name!r} was not found")
    security_manager.delete_role(role_name=role_name)
    return NoContent, HTTPStatus.NO_CONTENT


@requires_access_custom_view("PUT", permissions.RESOURCE_ROLE)
def patch_role(*, role_name: str, update_mask: UpdateMask = None) -> APIResponse:
    """Update a role."""
    security_manager = cast(FabAirflowSecurityManagerOverride, get_auth_manager().security_manager)
    body = request.json
    try:
        data = role_schema.load(body)
    except ValidationError as err:
        raise BadRequest(detail=str(err.messages))
    role = security_manager.find_role(name=role_name)
    if not role:
        raise NotFound(title="Role not found", detail=f"Role with name {role_name!r} was not found")
    if update_mask:
        update_mask = [i.strip() for i in update_mask]
        data_ = {}
        for field in update_mask:
            if field in data and field != "permissions":
                data_[field] = data[field]
            elif field == "actions":
                data_["permissions"] = data["permissions"]
            else:
                raise BadRequest(detail=f"'{field}' in update_mask is unknown")
        data = data_
    if "permissions" in data:
        perms = [(item["action"]["name"], item["resource"]["name"]) for item in data["permissions"] if item]
        _check_action_and_resource(security_manager, perms)
        security_manager.bulk_sync_roles([{"role": role_name, "perms": perms}])
    new_name = data.get("name")
    if new_name is not None and new_name != role.name:
        security_manager.update_role(role_id=role.id, name=new_name)
    return role_schema.dump(role)


@requires_access_custom_view("POST", permissions.RESOURCE_ROLE)
def post_role() -> APIResponse:
    """Create a new role."""
    security_manager = cast(FabAirflowSecurityManagerOverride, get_auth_manager().security_manager)
    body = request.json
    try:
        data = role_schema.load(body)
    except ValidationError as err:
        raise BadRequest(detail=str(err.messages))
    role = security_manager.find_role(name=data["name"])
    if not role:
        perms = [(item["action"]["name"], item["resource"]["name"]) for item in data["permissions"] if item]
        _check_action_and_resource(security_manager, perms)
        security_manager.bulk_sync_roles([{"role": data["name"], "perms": perms}])
        return role_schema.dump(role)
    detail = f"Role with name {role.name!r} already exists; please update with the PATCH endpoint"
    raise AlreadyExists(detail=detail)
