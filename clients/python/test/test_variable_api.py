# coding: utf-8

"""
    Airflow API (Stable)

    Apache Airflow management API.  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Contact: dev@airflow.apache.org
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import airflow_client
from airflow_client.api.variable_api import VariableApi  # noqa: E501
from airflow_client.rest import ApiException


class TestVariableApi(unittest.TestCase):
    """VariableApi unit test stubs"""

    def setUp(self):
        self.api = airflow_client.api.variable_api.VariableApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_airflow_api_connexion_endpoints_variable_endpoint_delete_variable(self):
        """Test case for airflow_api_connexion_endpoints_variable_endpoint_delete_variable

        Delete variable  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_variable_endpoint_get_variable(self):
        """Test case for airflow_api_connexion_endpoints_variable_endpoint_get_variable

        Get a variable by key  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_variable_endpoint_get_variables(self):
        """Test case for airflow_api_connexion_endpoints_variable_endpoint_get_variables

        Get all variables  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_variable_endpoint_patch_variable(self):
        """Test case for airflow_api_connexion_endpoints_variable_endpoint_patch_variable

        Update a variable by key  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_variable_endpoint_post_variables(self):
        """Test case for airflow_api_connexion_endpoints_variable_endpoint_post_variables

        Create a variable  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
