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
from airflow_client.api.import_error_api import ImportErrorApi  # noqa: E501
from airflow_client.rest import ApiException


class TestImportErrorApi(unittest.TestCase):
    """ImportErrorApi unit test stubs"""

    def setUp(self):
        self.api = airflow_client.api.import_error_api.ImportErrorApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_airflow_api_connexion_endpoints_import_error_endpoint_delete_import_error(self):
        """Test case for airflow_api_connexion_endpoints_import_error_endpoint_delete_import_error

        Delete an import error  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_import_error_endpoint_get_import_error(self):
        """Test case for airflow_api_connexion_endpoints_import_error_endpoint_get_import_error

        Get an import error  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_import_error_endpoint_get_import_errors(self):
        """Test case for airflow_api_connexion_endpoints_import_error_endpoint_get_import_errors

        Get all import errors  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
