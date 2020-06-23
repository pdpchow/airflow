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
 * The ImportError model module.
 * @module model/ImportError
 * @version 1.0.0
 */
class ImportError {
    /**
     * Constructs a new <code>ImportError</code>.
     * @alias module:model/ImportError
     */
    constructor() { 
        
        ImportError.initialize(this);
    }

    /**
     * Initializes the fields of this object.
     * This method is used by the constructors of any subclasses, in order to implement multiple inheritance (mix-ins).
     * Only for internal use.
     */
    static initialize(obj) { 
    }

    /**
     * Constructs a <code>ImportError</code> from a plain JavaScript object, optionally creating a new instance.
     * Copies all relevant properties from <code>data</code> to <code>obj</code> if supplied or a new instance if not.
     * @param {Object} data The plain JavaScript object bearing properties of interest.
     * @param {module:model/ImportError} obj Optional instance to populate.
     * @return {module:model/ImportError} The populated <code>ImportError</code> instance.
     */
    static constructFromObject(data, obj) {
        if (data) {
            obj = obj || new ImportError();

            if (data.hasOwnProperty('import_error_id')) {
                obj['import_error_id'] = ApiClient.convertToType(data['import_error_id'], 'Number');
            }
            if (data.hasOwnProperty('timestamp')) {
                obj['timestamp'] = ApiClient.convertToType(data['timestamp'], 'String');
            }
            if (data.hasOwnProperty('filename')) {
                obj['filename'] = ApiClient.convertToType(data['filename'], 'String');
            }
            if (data.hasOwnProperty('stack_trace')) {
                obj['stack_trace'] = ApiClient.convertToType(data['stack_trace'], 'String');
            }
        }
        return obj;
    }


}

/**
 * @member {Number} import_error_id
 */
ImportError.prototype['import_error_id'] = undefined;

/**
 * @member {String} timestamp
 */
ImportError.prototype['timestamp'] = undefined;

/**
 * @member {String} filename
 */
ImportError.prototype['filename'] = undefined;

/**
 * @member {String} stack_trace
 */
ImportError.prototype['stack_trace'] = undefined;






export default ImportError;

