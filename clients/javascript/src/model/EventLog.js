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
 * The EventLog model module.
 * @module model/EventLog
 * @version 1.0.0
 */
class EventLog {
    /**
     * Constructs a new <code>EventLog</code>.
     * @alias module:model/EventLog
     */
    constructor() { 
        
        EventLog.initialize(this);
    }

    /**
     * Initializes the fields of this object.
     * This method is used by the constructors of any subclasses, in order to implement multiple inheritance (mix-ins).
     * Only for internal use.
     */
    static initialize(obj) { 
    }

    /**
     * Constructs a <code>EventLog</code> from a plain JavaScript object, optionally creating a new instance.
     * Copies all relevant properties from <code>data</code> to <code>obj</code> if supplied or a new instance if not.
     * @param {Object} data The plain JavaScript object bearing properties of interest.
     * @param {module:model/EventLog} obj Optional instance to populate.
     * @return {module:model/EventLog} The populated <code>EventLog</code> instance.
     */
    static constructFromObject(data, obj) {
        if (data) {
            obj = obj || new EventLog();

            if (data.hasOwnProperty('event_log_id')) {
                obj['event_log_id'] = ApiClient.convertToType(data['event_log_id'], 'Number');
            }
            if (data.hasOwnProperty('when')) {
                obj['when'] = ApiClient.convertToType(data['when'], 'String');
            }
            if (data.hasOwnProperty('dag_id')) {
                obj['dag_id'] = ApiClient.convertToType(data['dag_id'], 'String');
            }
            if (data.hasOwnProperty('task_id')) {
                obj['task_id'] = ApiClient.convertToType(data['task_id'], 'String');
            }
            if (data.hasOwnProperty('event')) {
                obj['event'] = ApiClient.convertToType(data['event'], 'String');
            }
            if (data.hasOwnProperty('execution_date')) {
                obj['execution_date'] = ApiClient.convertToType(data['execution_date'], 'String');
            }
            if (data.hasOwnProperty('owner')) {
                obj['owner'] = ApiClient.convertToType(data['owner'], 'String');
            }
            if (data.hasOwnProperty('extra')) {
                obj['extra'] = ApiClient.convertToType(data['extra'], 'String');
            }
        }
        return obj;
    }


}

/**
 * @member {Number} event_log_id
 */
EventLog.prototype['event_log_id'] = undefined;

/**
 * @member {String} when
 */
EventLog.prototype['when'] = undefined;

/**
 * @member {String} dag_id
 */
EventLog.prototype['dag_id'] = undefined;

/**
 * @member {String} task_id
 */
EventLog.prototype['task_id'] = undefined;

/**
 * @member {String} event
 */
EventLog.prototype['event'] = undefined;

/**
 * @member {String} execution_date
 */
EventLog.prototype['execution_date'] = undefined;

/**
 * @member {String} owner
 */
EventLog.prototype['owner'] = undefined;

/**
 * @member {String} extra
 */
EventLog.prototype['extra'] = undefined;






export default EventLog;

