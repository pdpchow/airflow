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
import VariableAllOf from './VariableAllOf';
import VariableCollectionItem from './VariableCollectionItem';

/**
 * The Variable model module.
 * @module model/Variable
 * @version 1.0.0
 */
class Variable {
    /**
     * Constructs a new <code>Variable</code>.
     * @alias module:model/Variable
     * @implements module:model/VariableCollectionItem
     * @implements module:model/VariableAllOf
     */
    constructor() { 
        VariableCollectionItem.initialize(this);VariableAllOf.initialize(this);
        Variable.initialize(this);
    }

    /**
     * Initializes the fields of this object.
     * This method is used by the constructors of any subclasses, in order to implement multiple inheritance (mix-ins).
     * Only for internal use.
     */
    static initialize(obj) { 
    }

    /**
     * Constructs a <code>Variable</code> from a plain JavaScript object, optionally creating a new instance.
     * Copies all relevant properties from <code>data</code> to <code>obj</code> if supplied or a new instance if not.
     * @param {Object} data The plain JavaScript object bearing properties of interest.
     * @param {module:model/Variable} obj Optional instance to populate.
     * @return {module:model/Variable} The populated <code>Variable</code> instance.
     */
    static constructFromObject(data, obj) {
        if (data) {
            obj = obj || new Variable();
            VariableCollectionItem.constructFromObject(data, obj);
            VariableAllOf.constructFromObject(data, obj);

            if (data.hasOwnProperty('key')) {
                obj['key'] = ApiClient.convertToType(data['key'], 'String');
            }
            if (data.hasOwnProperty('value')) {
                obj['value'] = ApiClient.convertToType(data['value'], 'String');
            }
        }
        return obj;
    }


}

/**
 * @member {String} key
 */
Variable.prototype['key'] = undefined;

/**
 * @member {String} value
 */
Variable.prototype['value'] = undefined;


// Implement VariableCollectionItem interface:
/**
 * @member {String} key
 */
VariableCollectionItem.prototype['key'] = undefined;
// Implement VariableAllOf interface:
/**
 * @member {String} value
 */
VariableAllOf.prototype['value'] = undefined;




export default Variable;

