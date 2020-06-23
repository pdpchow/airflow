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

import ApiClient from '../ApiClient';

/**
 * The ListTaskInstanceForm model module.
 * @module model/ListTaskInstanceForm
 * @version 1.0.0
 */
class ListTaskInstanceForm {
    /**
     * Constructs a new <code>ListTaskInstanceForm</code>.
     * @alias module:model/ListTaskInstanceForm
     */
    constructor() { 
        
        ListTaskInstanceForm.initialize(this);
    }

    /**
     * Initializes the fields of this object.
     * This method is used by the constructors of any subclasses, in order to implement multiple inheritance (mix-ins).
     * Only for internal use.
     */
    static initialize(obj) { 
    }

    /**
     * Constructs a <code>ListTaskInstanceForm</code> from a plain JavaScript object, optionally creating a new instance.
     * Copies all relevant properties from <code>data</code> to <code>obj</code> if supplied or a new instance if not.
     * @param {Object} data The plain JavaScript object bearing properties of interest.
     * @param {module:model/ListTaskInstanceForm} obj Optional instance to populate.
     * @return {module:model/ListTaskInstanceForm} The populated <code>ListTaskInstanceForm</code> instance.
     */
    static constructFromObject(data, obj) {
        if (data) {
            obj = obj || new ListTaskInstanceForm();

            if (data.hasOwnProperty('dag_ids')) {
                obj['dag_ids'] = ApiClient.convertToType(data['dag_ids'], ['String']);
            }
            if (data.hasOwnProperty('execution_date_gte')) {
                obj['execution_date_gte'] = ApiClient.convertToType(data['execution_date_gte'], 'Date');
            }
            if (data.hasOwnProperty('execution_date_lte')) {
                obj['execution_date_lte'] = ApiClient.convertToType(data['execution_date_lte'], 'Date');
            }
            if (data.hasOwnProperty('start_date_gte')) {
                obj['start_date_gte'] = ApiClient.convertToType(data['start_date_gte'], 'Date');
            }
            if (data.hasOwnProperty('start_date_lte')) {
                obj['start_date_lte'] = ApiClient.convertToType(data['start_date_lte'], 'Date');
            }
            if (data.hasOwnProperty('end_date_gte')) {
                obj['end_date_gte'] = ApiClient.convertToType(data['end_date_gte'], 'Date');
            }
            if (data.hasOwnProperty('end_date_lte')) {
                obj['end_date_lte'] = ApiClient.convertToType(data['end_date_lte'], 'Date');
            }
            if (data.hasOwnProperty('duration_gte')) {
                obj['duration_gte'] = ApiClient.convertToType(data['duration_gte'], 'Number');
            }
            if (data.hasOwnProperty('duration_lte')) {
                obj['duration_lte'] = ApiClient.convertToType(data['duration_lte'], 'Number');
            }
            if (data.hasOwnProperty('State')) {
                obj['State'] = ApiClient.convertToType(data['State'], ['String']);
            }
            if (data.hasOwnProperty('Pool')) {
                obj['Pool'] = ApiClient.convertToType(data['Pool'], ['String']);
            }
            if (data.hasOwnProperty('Queue')) {
                obj['Queue'] = ApiClient.convertToType(data['Queue'], ['String']);
            }
        }
        return obj;
    }


}

/**
 * Return objects with specific DAG IDs. The value can be repeated to retrieve multiple matching values (OR condition).
 * @member {Array.<String>} dag_ids
 */
ListTaskInstanceForm.prototype['dag_ids'] = undefined;

/**
 * Returns objects greater or equal to the specified date. This can be combined with execution_date_lte parameter to receive only the selected period. 
 * @member {Date} execution_date_gte
 */
ListTaskInstanceForm.prototype['execution_date_gte'] = undefined;

/**
 * Returns objects less than or equal to the specified date. This can be combined with execution_date_gte parameter to receive only the selected period. 
 * @member {Date} execution_date_lte
 */
ListTaskInstanceForm.prototype['execution_date_lte'] = undefined;

/**
 * Returns objects greater or equal the specified date. This can be combined with startd_ate_lte parameter to receive only the selected period. 
 * @member {Date} start_date_gte
 */
ListTaskInstanceForm.prototype['start_date_gte'] = undefined;

/**
 * Returns objects less or equal the specified date. This can be combined with start_date_gte parameter to receive only the selected period. 
 * @member {Date} start_date_lte
 */
ListTaskInstanceForm.prototype['start_date_lte'] = undefined;

/**
 * Returns objects greater or equal the specified date. This can be combined with start_date_lte parameter to receive only the selected period. 
 * @member {Date} end_date_gte
 */
ListTaskInstanceForm.prototype['end_date_gte'] = undefined;

/**
 * Returns objects less than or equal to the specified date. This can be combined with start_date_gte parameter to receive only the selected period. 
 * @member {Date} end_date_lte
 */
ListTaskInstanceForm.prototype['end_date_lte'] = undefined;

/**
 * Returns objects greater than or equal to the specified values. This can be combined with duration_lte parameter to receive only the selected period. 
 * @member {Number} duration_gte
 */
ListTaskInstanceForm.prototype['duration_gte'] = undefined;

/**
 * Returns objects less than or equal to the specified values. This can be combined with duration_gte parameter to receive only the selected range. 
 * @member {Number} duration_lte
 */
ListTaskInstanceForm.prototype['duration_lte'] = undefined;

/**
 * The value can be repeated to retrieve multiple matching values (OR condition).
 * @member {Array.<String>} State
 */
ListTaskInstanceForm.prototype['State'] = undefined;

/**
 * The value can be repeated to retrieve multiple matching values (OR condition).
 * @member {Array.<String>} Pool
 */
ListTaskInstanceForm.prototype['Pool'] = undefined;

/**
 * The value can be repeated to retrieve multiple matching values (OR condition).
 * @member {Array.<String>} Queue
 */
ListTaskInstanceForm.prototype['Queue'] = undefined;






export default ListTaskInstanceForm;

