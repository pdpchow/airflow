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
from airflow_client.api.dag_run_api import DAGRunApi  # noqa: E501
from airflow_client.rest import ApiException


class TestDAGRunApi(unittest.TestCase):
    """DAGRunApi unit test stubs"""

    def setUp(self):
        self.api = airflow_client.api.dag_run_api.DAGRunApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_airflow_api_connexion_endpoints_dag_run_endpoint_delete_dag_run(self):
        """Test case for airflow_api_connexion_endpoints_dag_run_endpoint_delete_dag_run

        Delete a DAG Run  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_dag_run_endpoint_get_dag_run(self):
        """Test case for airflow_api_connexion_endpoints_dag_run_endpoint_get_dag_run

        Get a DAG Run  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_dag_run_endpoint_get_dag_runs(self):
        """Test case for airflow_api_connexion_endpoints_dag_run_endpoint_get_dag_runs

        Get all DAG Runs  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_dag_run_endpoint_get_dag_runs_batch(self):
        """Test case for airflow_api_connexion_endpoints_dag_run_endpoint_get_dag_runs_batch

        Get all DAG Runs from aall DAGs.  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_dag_run_endpoint_patch_dag_run(self):
        """Test case for airflow_api_connexion_endpoints_dag_run_endpoint_patch_dag_run

        Update a DAG Run  # noqa: E501
        """
        pass

    def test_airflow_api_connexion_endpoints_dag_run_endpoint_post_dag_run(self):
        """Test case for airflow_api_connexion_endpoints_dag_run_endpoint_post_dag_run

        Trigger a DAG Run  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
