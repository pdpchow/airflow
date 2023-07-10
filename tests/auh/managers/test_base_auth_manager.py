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

import pytest

from airflow.auth.managers.base_auth_manager import BaseAuthManager


@pytest.fixture
def auth_manager():
    class EmptyAuthManager(BaseAuthManager):
        def get_user_name(self) -> str:
            raise NotImplementedError()

    return EmptyAuthManager()


class TestBaseAuthManager:
    def test_get_security_manager_override_class_return_class(self, auth_manager):
        assert type(auth_manager.get_security_manager_override_class()) is type
