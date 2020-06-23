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
import ClassReference from './ClassReference';

/**
 * The TaskExtraLinks model module.
 * @module model/TaskExtraLinks
 * @version 1.0.0
 */
class TaskExtraLinks {
    /**
     * Constructs a new <code>TaskExtraLinks</code>.
     * @alias module:model/TaskExtraLinks
     */
    constructor() { 
        
        TaskExtraLinks.initialize(this);
    }

    /**
     * Initializes the fields of this object.
     * This method is used by the constructors of any subclasses, in order to implement multiple inheritance (mix-ins).
     * Only for internal use.
     */
    static initialize(obj) { 
    }

    /**
     * Constructs a <code>TaskExtraLinks</code> from a plain JavaScript object, optionally creating a new instance.
     * Copies all relevant properties from <code>data</code> to <code>obj</code> if supplied or a new instance if not.
     * @param {Object} data The plain JavaScript object bearing properties of interest.
     * @param {module:model/TaskExtraLinks} obj Optional instance to populate.
     * @return {module:model/TaskExtraLinks} The populated <code>TaskExtraLinks</code> instance.
     */
    static constructFromObject(data, obj) {
        if (data) {
            obj = obj || new TaskExtraLinks();

            if (data.hasOwnProperty('class_ref')) {
                obj['class_ref'] = ClassReference.constructFromObject(data['class_ref']);
            }
        }
        return obj;
    }


}

/**
 * @member {module:model/ClassReference} class_ref
 */
TaskExtraLinks.prototype['class_ref'] = undefined;






export default TaskExtraLinks;

