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

import unittest
from unittest import mock

from airflow.providers.jenkins.hooks.jenkins import JenkinsHook


class TestJenkinsHook(unittest.TestCase):

    @mock.patch('airflow.hooks.base_hook.BaseHook.get_connection')
    def test_client_created_default_http(self,
                                               get_connection_mock):
        """ tests `init` method to validate http client creation when all parameters are passed """
        default_connection_id = 'jenkins_default'

        connectionHost = 'http://test.com'
        connectionPort = 8080
        get_connection_mock.return_value = mock. \
            Mock(connection_id=default_connection_id,
                 login='test', password='test', extra='',
                 host=connectionHost, port=connectionPort)

        complete_url = f'http://{connectionHost}:{connectionPort}/'
        hook = JenkinsHook(default_connection_id)
        self.assertIsNotNone(hook.jenkins_server)
        self.assertEqual(hook.jenkins_server.server, complete_url)


    @mock.patch('airflow.hooks.base_hook.BaseHook.get_connection')
    def test_client_created_default_https(self,
                                               get_connection_mock):
        """ tests `init` method to validate https client creation when all
        parameters are passed """
        default_connection_id = 'jenkins_default'

        connectionHost = 'http://test.com'
        connectionPort = 8080
        get_connection_mock.return_value = mock. \
            Mock(connection_id=default_connection_id,
                 login='test', password='test', extra='true',
                 host=connectionHost, port=connectionPort)

        complete_url = f'https://{connectionHost}:{connectionPort}/'
        hook = JenkinsHook(default_connection_id)
        self.assertIsNotNone(hook.jenkins_server)
        self.assertEqual(hook.jenkins_server.server, complete_url)
