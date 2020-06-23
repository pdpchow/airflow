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
 * The SLAMiss model module.
 * @module model/SLAMiss
 * @version 1.0.0
 */
class SLAMiss {
    /**
     * Constructs a new <code>SLAMiss</code>.
     * @alias module:model/SLAMiss
     */
    constructor() { 
        
        SLAMiss.initialize(this);
    }

    /**
     * Initializes the fields of this object.
     * This method is used by the constructors of any subclasses, in order to implement multiple inheritance (mix-ins).
     * Only for internal use.
     */
    static initialize(obj) { 
    }

    /**
     * Constructs a <code>SLAMiss</code> from a plain JavaScript object, optionally creating a new instance.
     * Copies all relevant properties from <code>data</code> to <code>obj</code> if supplied or a new instance if not.
     * @param {Object} data The plain JavaScript object bearing properties of interest.
     * @param {module:model/SLAMiss} obj Optional instance to populate.
     * @return {module:model/SLAMiss} The populated <code>SLAMiss</code> instance.
     */
    static constructFromObject(data, obj) {
        if (data) {
            obj = obj || new SLAMiss();

            if (data.hasOwnProperty('task_id')) {
                obj['task_id'] = ApiClient.convertToType(data['task_id'], 'String');
            }
            if (data.hasOwnProperty('dag_id')) {
                obj['dag_id'] = ApiClient.convertToType(data['dag_id'], 'String');
            }
            if (data.hasOwnProperty('execution_date')) {
                obj['execution_date'] = ApiClient.convertToType(data['execution_date'], 'String');
            }
            if (data.hasOwnProperty('email_sent')) {
                obj['email_sent'] = ApiClient.convertToType(data['email_sent'], 'Boolean');
            }
            if (data.hasOwnProperty('timestamp')) {
                obj['timestamp'] = ApiClient.convertToType(data['timestamp'], 'String');
            }
            if (data.hasOwnProperty('description')) {
                obj['description'] = ApiClient.convertToType(data['description'], 'String');
            }
            if (data.hasOwnProperty('notification_sent')) {
                obj['notification_sent'] = ApiClient.convertToType(data['notification_sent'], 'Boolean');
            }
        }
        return obj;
    }


}

/**
 * @member {String} task_id
 */
SLAMiss.prototype['task_id'] = undefined;

/**
 * @member {String} dag_id
 */
SLAMiss.prototype['dag_id'] = undefined;

/**
 * @member {String} execution_date
 */
SLAMiss.prototype['execution_date'] = undefined;

/**
 * @member {Boolean} email_sent
 */
SLAMiss.prototype['email_sent'] = undefined;

/**
 * @member {String} timestamp
 */
SLAMiss.prototype['timestamp'] = undefined;

/**
 * @member {String} description
 */
SLAMiss.prototype['description'] = undefined;

/**
 * @member {Boolean} notification_sent
 */
SLAMiss.prototype['notification_sent'] = undefined;






export default SLAMiss;

