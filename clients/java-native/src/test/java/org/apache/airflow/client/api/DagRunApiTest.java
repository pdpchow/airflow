/*
 * Airflow API (Stable)
 * Apache Airflow management API.
 *
 * The version of the OpenAPI document: 1.0.0
 * Contact: dev@airflow.apache.org
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


package org.apache.airflow.client.api;

import org.apache.airflow.client.ApiException;
import org.openapitools.client.model.DAGRun;
import org.openapitools.client.model.DAGRunCollection;
import org.openapitools.client.model.Error;
import org.openapitools.client.model.ListDagRunsForm;
import java.time.OffsetDateTime;
import org.junit.Test;
import org.junit.Ignore;
import org.junit.Assert;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * API tests for DagRunApi
 */
public class DagRunApiTest {

    private final DagRunApi api = new DagRunApi();

    /**
     * Delete a DAG Run
     *
     * @throws ApiException
     *          if the Api call fails
     */
    @Test
    public void airflowApiConnexionEndpointsDagRunEndpointDeleteDagRunTest() throws ApiException {
        //
        //String dagId = null;
        //
        //String dagRunId = null;
        //
        //api.airflowApiConnexionEndpointsDagRunEndpointDeleteDagRun(dagId, dagRunId);

        // TODO: test validations
    }
    /**
     * Get a DAG Run
     *
     * @throws ApiException
     *          if the Api call fails
     */
    @Test
    public void airflowApiConnexionEndpointsDagRunEndpointGetDagRunTest() throws ApiException {
        //
        //String dagId = null;
        //
        //String dagRunId = null;
        //
        //DAGRun response = api.airflowApiConnexionEndpointsDagRunEndpointGetDagRun(dagId, dagRunId);

        // TODO: test validations
    }
    /**
     * Get all DAG Runs
     *
     * This endpoint allows specifying &#x60;~&#x60; as the dag_id to retrieve DAG Runs for all DAGs. 
     *
     * @throws ApiException
     *          if the Api call fails
     */
    @Test
    public void airflowApiConnexionEndpointsDagRunEndpointGetDagRunsTest() throws ApiException {
        //
        //String dagId = null;
        //
        //Integer limit = null;
        //
        //Integer offset = null;
        //
        //OffsetDateTime executionDateGte = null;
        //
        //OffsetDateTime executionDateLte = null;
        //
        //OffsetDateTime startDateGte = null;
        //
        //OffsetDateTime startDateLte = null;
        //
        //OffsetDateTime endDateGte = null;
        //
        //OffsetDateTime endDateLte = null;
        //
        //DAGRunCollection response = api.airflowApiConnexionEndpointsDagRunEndpointGetDagRuns(dagId, limit, offset, executionDateGte, executionDateLte, startDateGte, startDateLte, endDateGte, endDateLte);

        // TODO: test validations
    }
    /**
     * Get all DAG Runs from aall DAGs.
     *
     * This endpoint is a POST to allow filtering across a large number of DAG IDs, where as a GET it would run in to maximum HTTP request URL lengthlimits 
     *
     * @throws ApiException
     *          if the Api call fails
     */
    @Test
    public void airflowApiConnexionEndpointsDagRunEndpointGetDagRunsBatchTest() throws ApiException {
        //
        //ListDagRunsForm listDagRunsForm = null;
        //
        //DAGRunCollection response = api.airflowApiConnexionEndpointsDagRunEndpointGetDagRunsBatch(listDagRunsForm);

        // TODO: test validations
    }
    /**
     * Update a DAG Run
     *
     * @throws ApiException
     *          if the Api call fails
     */
    @Test
    public void airflowApiConnexionEndpointsDagRunEndpointPatchDagRunTest() throws ApiException {
        //
        //String dagId = null;
        //
        //String dagRunId = null;
        //
        //DAGRun daGRun = null;
        //
        //List<String> updateMask = null;
        //
        //DAGRun response = api.airflowApiConnexionEndpointsDagRunEndpointPatchDagRun(dagId, dagRunId, daGRun, updateMask);

        // TODO: test validations
    }
    /**
     * Trigger a DAG Run
     *
     * @throws ApiException
     *          if the Api call fails
     */
    @Test
    public void airflowApiConnexionEndpointsDagRunEndpointPostDagRunTest() throws ApiException {
        //
        //String dagId = null;
        //
        //String dagRunId = null;
        //
        //DAGRun daGRun = null;
        //
        //DAGRun response = api.airflowApiConnexionEndpointsDagRunEndpointPostDagRun(dagId, dagRunId, daGRun);

        // TODO: test validations
    }
}
