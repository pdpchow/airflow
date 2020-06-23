/**
 * Airflow API (Stable)
 * Apache Airflow management API.
 *
 * The version of the OpenAPI document: 1.0.0
 * Contact: dev@airflow.apache.org
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 *
 */


import ApiClient from "../ApiClient";
import ClearTaskInstance from '../model/ClearTaskInstance';
import DAG from '../model/DAG';
import DAGCollection from '../model/DAGCollection';
import DAGDetail from '../model/DAGDetail';
import Error from '../model/Error';
import InlineResponse2001 from '../model/InlineResponse2001';
import Task from '../model/Task';
import TaskCollection from '../model/TaskCollection';
import TaskInstanceReferenceCollection from '../model/TaskInstanceReferenceCollection';

/**
* DAG service.
* @module api/DAGApi
* @version 1.0.0
*/
export default class DAGApi {

    /**
    * Constructs a new DAGApi. 
    * @alias module:api/DAGApi
    * @class
    * @param {module:ApiClient} [apiClient] Optional API client implementation to use,
    * default to {@link module:ApiClient#instance} if unspecified.
    */
    constructor(apiClient) {
        this.apiClient = apiClient || ApiClient.instance;
    }


    /**
     * Callback function to receive the result of the getDag operation.
     * @callback module:api/DAGApi~getDagCallback
     * @param {String} error Error message, if any.
     * @param {module:model/DAG} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Get basic information about a DAG
     * Presents only information available in database (DAGModel). If you need detailed information, consider using GET /dags/{dag_id}/detail. 
     * @param {String} dagId The DAG ID.
     * @param {module:api/DAGApi~getDagCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/DAG}
     */
    getDag(dagId, callback) {
      let postBody = null;
      // verify the required parameter 'dagId' is set
      if (dagId === undefined || dagId === null) {
        throw new Error("Missing the required parameter 'dagId' when calling getDag");
      }

      let pathParams = {
        'dag_id': dagId
      };
      let queryParams = {
      };
      let headerParams = {
      };
      let formParams = {
      };

      let authNames = [];
      let contentTypes = [];
      let accepts = ['application/json'];
      let returnType = DAG;
      return this.apiClient.callApi(
        '/dags/{dag_id}', 'GET',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }

    /**
     * Callback function to receive the result of the getDagDetails operation.
     * @callback module:api/DAGApi~getDagDetailsCallback
     * @param {String} error Error message, if any.
     * @param {module:model/DAGDetail} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Get a simplified representation of DAG.
     * The response contains many DAG attributes, so the response can be large. If possible, consider using GET /dags/{dag_id}. 
     * @param {String} dagId The DAG ID.
     * @param {module:api/DAGApi~getDagDetailsCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/DAGDetail}
     */
    getDagDetails(dagId, callback) {
      let postBody = null;
      // verify the required parameter 'dagId' is set
      if (dagId === undefined || dagId === null) {
        throw new Error("Missing the required parameter 'dagId' when calling getDagDetails");
      }

      let pathParams = {
        'dag_id': dagId
      };
      let queryParams = {
      };
      let headerParams = {
      };
      let formParams = {
      };

      let authNames = [];
      let contentTypes = [];
      let accepts = ['application/json'];
      let returnType = DAGDetail;
      return this.apiClient.callApi(
        '/dags/{dag_id}/details', 'GET',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }

    /**
     * Callback function to receive the result of the getDagSource operation.
     * @callback module:api/DAGApi~getDagSourceCallback
     * @param {String} error Error message, if any.
     * @param {module:model/InlineResponse2001} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Get source code using file token
     * @param {String} fileToken The key containing the encrypted path to the file. Encryption and decryption take place only on the server. This prevents the client from reading an non-DAG file. This also ensures API extensibility, because the format of encrypted data may change. 
     * @param {module:api/DAGApi~getDagSourceCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/InlineResponse2001}
     */
    getDagSource(fileToken, callback) {
      let postBody = null;
      // verify the required parameter 'fileToken' is set
      if (fileToken === undefined || fileToken === null) {
        throw new Error("Missing the required parameter 'fileToken' when calling getDagSource");
      }

      let pathParams = {
        'file_token': fileToken
      };
      let queryParams = {
      };
      let headerParams = {
      };
      let formParams = {
      };

      let authNames = [];
      let contentTypes = [];
      let accepts = ['application/json'];
      let returnType = InlineResponse2001;
      return this.apiClient.callApi(
        '/dagSources/{file_token}', 'GET',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }

    /**
     * Callback function to receive the result of the getDags operation.
     * @callback module:api/DAGApi~getDagsCallback
     * @param {String} error Error message, if any.
     * @param {module:model/DAGCollection} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Get all DAGs
     * @param {Object} opts Optional parameters
     * @param {Number} opts.limit The numbers of items to return. (default to 100)
     * @param {Number} opts.offset The number of items to skip before starting to collect the result set.
     * @param {module:api/DAGApi~getDagsCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/DAGCollection}
     */
    getDags(opts, callback) {
      opts = opts || {};
      let postBody = null;

      let pathParams = {
      };
      let queryParams = {
        'limit': opts['limit'],
        'offset': opts['offset']
      };
      let headerParams = {
      };
      let formParams = {
      };

      let authNames = [];
      let contentTypes = [];
      let accepts = ['application/json'];
      let returnType = DAGCollection;
      return this.apiClient.callApi(
        '/dags', 'GET',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }

    /**
     * Callback function to receive the result of the getTask operation.
     * @callback module:api/DAGApi~getTaskCallback
     * @param {String} error Error message, if any.
     * @param {module:model/Task} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Get simplified representation of a task.
     * @param {String} dagId The DAG ID.
     * @param {String} taskId The Task ID.
     * @param {module:api/DAGApi~getTaskCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/Task}
     */
    getTask(dagId, taskId, callback) {
      let postBody = null;
      // verify the required parameter 'dagId' is set
      if (dagId === undefined || dagId === null) {
        throw new Error("Missing the required parameter 'dagId' when calling getTask");
      }
      // verify the required parameter 'taskId' is set
      if (taskId === undefined || taskId === null) {
        throw new Error("Missing the required parameter 'taskId' when calling getTask");
      }

      let pathParams = {
        'dag_id': dagId,
        'task_id': taskId
      };
      let queryParams = {
      };
      let headerParams = {
      };
      let formParams = {
      };

      let authNames = [];
      let contentTypes = [];
      let accepts = ['application/json'];
      let returnType = Task;
      return this.apiClient.callApi(
        '/dags/{dag_id}/tasks/{task_id}', 'GET',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }

    /**
     * Callback function to receive the result of the getTasks operation.
     * @callback module:api/DAGApi~getTasksCallback
     * @param {String} error Error message, if any.
     * @param {module:model/TaskCollection} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Get tasks for DAG
     * @param {String} dagId The DAG ID.
     * @param {module:api/DAGApi~getTasksCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/TaskCollection}
     */
    getTasks(dagId, callback) {
      let postBody = null;
      // verify the required parameter 'dagId' is set
      if (dagId === undefined || dagId === null) {
        throw new Error("Missing the required parameter 'dagId' when calling getTasks");
      }

      let pathParams = {
        'dag_id': dagId
      };
      let queryParams = {
      };
      let headerParams = {
      };
      let formParams = {
      };

      let authNames = [];
      let contentTypes = [];
      let accepts = ['application/json'];
      let returnType = TaskCollection;
      return this.apiClient.callApi(
        '/dags/{dag_id}/tasks', 'GET',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }

    /**
     * Callback function to receive the result of the patchDag operation.
     * @callback module:api/DAGApi~patchDagCallback
     * @param {String} error Error message, if any.
     * @param {module:model/DAG} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Update a DAG
     * @param {String} dagId The DAG ID.
     * @param {module:model/DAG} DAG 
     * @param {module:api/DAGApi~patchDagCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/DAG}
     */
    patchDag(dagId, DAG, callback) {
      let postBody = DAG;
      // verify the required parameter 'dagId' is set
      if (dagId === undefined || dagId === null) {
        throw new Error("Missing the required parameter 'dagId' when calling patchDag");
      }
      // verify the required parameter 'DAG' is set
      if (DAG === undefined || DAG === null) {
        throw new Error("Missing the required parameter 'DAG' when calling patchDag");
      }

      let pathParams = {
        'dag_id': dagId
      };
      let queryParams = {
      };
      let headerParams = {
      };
      let formParams = {
      };

      let authNames = [];
      let contentTypes = ['application/json'];
      let accepts = ['application/json'];
      let returnType = DAG;
      return this.apiClient.callApi(
        '/dags/{dag_id}', 'PATCH',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }

    /**
     * Callback function to receive the result of the postClearTaskInstances operation.
     * @callback module:api/DAGApi~postClearTaskInstancesCallback
     * @param {String} error Error message, if any.
     * @param {module:model/TaskInstanceReferenceCollection} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Clears a set of task instances associated with the DAG for a specified date range.
     * @param {String} dagId The DAG ID.
     * @param {module:model/ClearTaskInstance} clearTaskInstance Parameters of action
     * @param {module:api/DAGApi~postClearTaskInstancesCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/TaskInstanceReferenceCollection}
     */
    postClearTaskInstances(dagId, clearTaskInstance, callback) {
      let postBody = clearTaskInstance;
      // verify the required parameter 'dagId' is set
      if (dagId === undefined || dagId === null) {
        throw new Error("Missing the required parameter 'dagId' when calling postClearTaskInstances");
      }
      // verify the required parameter 'clearTaskInstance' is set
      if (clearTaskInstance === undefined || clearTaskInstance === null) {
        throw new Error("Missing the required parameter 'clearTaskInstance' when calling postClearTaskInstances");
      }

      let pathParams = {
        'dag_id': dagId
      };
      let queryParams = {
      };
      let headerParams = {
      };
      let formParams = {
      };

      let authNames = [];
      let contentTypes = ['application/json'];
      let accepts = ['application/json'];
      let returnType = TaskInstanceReferenceCollection;
      return this.apiClient.callApi(
        '/dags/{dag_id}/clearTaskInstances', 'POST',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }


}
