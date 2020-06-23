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
from airflow_client.api.x_com_api import XComApi  # noqa: E501
from airflow_client.rest import ApiException


class TestXComApi(unittest.TestCase):
    """XComApi unit test stubs"""

    def setUp(self):
        self.api = airflow_client.api.x_com_api.XComApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_airflow_api_connexion_endpoints_xcom_endpoint_delete_xcom_entry(self):
        """Test case for airflow_api_connexion_endpoints_xcom_endpoint_delete_xcom_entry

        Delete an XCom entry  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_xcom_endpoint_get_xcom_entries(self):
        """Test case for airflow_api_connexion_endpoints_xcom_endpoint_get_xcom_entries

        Get all XCom entries  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_xcom_endpoint_get_xcom_entry(self):
        """Test case for airflow_api_connexion_endpoints_xcom_endpoint_get_xcom_entry

        Get an XCom entry  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_xcom_endpoint_patch_xcom_entry(self):
        """Test case for airflow_api_connexion_endpoints_xcom_endpoint_patch_xcom_entry

        Update an XCom entry  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_xcom_endpoint_post_xcom_entries(self):
        """Test case for airflow_api_connexion_endpoints_xcom_endpoint_post_xcom_entries

        Create an XCom entry  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
