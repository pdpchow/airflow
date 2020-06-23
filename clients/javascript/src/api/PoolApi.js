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
import Error from '../model/Error';
import Pool from '../model/Pool';
import PoolCollection from '../model/PoolCollection';

/**
* Pool service.
* @module api/PoolApi
* @version 1.0.0
*/
export default class PoolApi {

    /**
    * Constructs a new PoolApi. 
    * @alias module:api/PoolApi
    * @class
    * @param {module:ApiClient} [apiClient] Optional API client implementation to use,
    * default to {@link module:ApiClient#instance} if unspecified.
    */
    constructor(apiClient) {
        this.apiClient = apiClient || ApiClient.instance;
    }


    /**
     * Callback function to receive the result of the deletePool operation.
     * @callback module:api/PoolApi~deletePoolCallback
     * @param {String} error Error message, if any.
     * @param data This operation does not return a value.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Delete a pool
     * @param {String} poolName The Pool name.
     * @param {module:api/PoolApi~deletePoolCallback} callback The callback function, accepting three arguments: error, data, response
     */
    deletePool(poolName, callback) {
      let postBody = null;
      // verify the required parameter 'poolName' is set
      if (poolName === undefined || poolName === null) {
        throw new Error("Missing the required parameter 'poolName' when calling deletePool");
      }

      let pathParams = {
        'pool_name': poolName
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
      let returnType = null;
      return this.apiClient.callApi(
        '/pools/{pool_name}', 'DELETE',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }

    /**
     * Callback function to receive the result of the getPool operation.
     * @callback module:api/PoolApi~getPoolCallback
     * @param {String} error Error message, if any.
     * @param {module:model/Pool} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Get a pool
     * @param {String} poolName The Pool name.
     * @param {module:api/PoolApi~getPoolCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/Pool}
     */
    getPool(poolName, callback) {
      let postBody = null;
      // verify the required parameter 'poolName' is set
      if (poolName === undefined || poolName === null) {
        throw new Error("Missing the required parameter 'poolName' when calling getPool");
      }

      let pathParams = {
        'pool_name': poolName
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
      let returnType = Pool;
      return this.apiClient.callApi(
        '/pools/{pool_name}', 'GET',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }

    /**
     * Callback function to receive the result of the getPools operation.
     * @callback module:api/PoolApi~getPoolsCallback
     * @param {String} error Error message, if any.
     * @param {module:model/PoolCollection} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Get all pools
     * @param {Object} opts Optional parameters
     * @param {Number} opts.limit The numbers of items to return. (default to 100)
     * @param {Number} opts.offset The number of items to skip before starting to collect the result set.
     * @param {module:api/PoolApi~getPoolsCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/PoolCollection}
     */
    getPools(opts, callback) {
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
      let returnType = PoolCollection;
      return this.apiClient.callApi(
        '/pools', 'GET',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }

    /**
     * Callback function to receive the result of the patchPool operation.
     * @callback module:api/PoolApi~patchPoolCallback
     * @param {String} error Error message, if any.
     * @param {module:model/Pool} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Update a pool
     * @param {String} poolName The Pool name.
     * @param {module:model/Pool} pool 
     * @param {Object} opts Optional parameters
     * @param {Array.<String>} opts.updateMask The fields to update on the connection (connection, pool etc). If absent or empty, all modifiable fields are updated. A comma-separated list of fully qualified names of fields. 
     * @param {module:api/PoolApi~patchPoolCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/Pool}
     */
    patchPool(poolName, pool, opts, callback) {
      opts = opts || {};
      let postBody = pool;
      // verify the required parameter 'poolName' is set
      if (poolName === undefined || poolName === null) {
        throw new Error("Missing the required parameter 'poolName' when calling patchPool");
      }
      // verify the required parameter 'pool' is set
      if (pool === undefined || pool === null) {
        throw new Error("Missing the required parameter 'pool' when calling patchPool");
      }

      let pathParams = {
        'pool_name': poolName
      };
      let queryParams = {
        'update_mask': this.apiClient.buildCollectionParam(opts['updateMask'], 'csv')
      };
      let headerParams = {
      };
      let formParams = {
      };

      let authNames = [];
      let contentTypes = ['application/json'];
      let accepts = ['application/json'];
      let returnType = Pool;
      return this.apiClient.callApi(
        '/pools/{pool_name}', 'PATCH',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }

    /**
     * Callback function to receive the result of the postPool operation.
     * @callback module:api/PoolApi~postPoolCallback
     * @param {String} error Error message, if any.
     * @param {module:model/Pool} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * Create a pool
     * @param {module:model/Pool} pool 
     * @param {module:api/PoolApi~postPoolCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/Pool}
     */
    postPool(pool, callback) {
      let postBody = pool;
      // verify the required parameter 'pool' is set
      if (pool === undefined || pool === null) {
        throw new Error("Missing the required parameter 'pool' when calling postPool");
      }

      let pathParams = {
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
      let returnType = Pool;
      return this.apiClient.callApi(
        '/pools', 'POST',
        pathParams, queryParams, headerParams, formParams, postBody,
        authNames, contentTypes, accepts, returnType, null, callback
      );
    }


}
