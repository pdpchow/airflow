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
import SLAMiss from './SLAMiss';

/**
 * The SLAMissCollection model module.
 * @module model/SLAMissCollection
 * @version 1.0.0
 */
class SLAMissCollection {
    /**
     * Constructs a new <code>SLAMissCollection</code>.
     * @alias module:model/SLAMissCollection
     */
    constructor() { 
        
        SLAMissCollection.initialize(this);
    }

    /**
     * Initializes the fields of this object.
     * This method is used by the constructors of any subclasses, in order to implement multiple inheritance (mix-ins).
     * Only for internal use.
     */
    static initialize(obj) { 
    }

    /**
     * Constructs a <code>SLAMissCollection</code> from a plain JavaScript object, optionally creating a new instance.
     * Copies all relevant properties from <code>data</code> to <code>obj</code> if supplied or a new instance if not.
     * @param {Object} data The plain JavaScript object bearing properties of interest.
     * @param {module:model/SLAMissCollection} obj Optional instance to populate.
     * @return {module:model/SLAMissCollection} The populated <code>SLAMissCollection</code> instance.
     */
    static constructFromObject(data, obj) {
        if (data) {
            obj = obj || new SLAMissCollection();

            if (data.hasOwnProperty('sla_misses')) {
                obj['sla_misses'] = ApiClient.convertToType(data['sla_misses'], [SLAMiss]);
            }
        }
        return obj;
    }


}

/**
 * @member {Array.<module:model/SLAMiss>} sla_misses
 */
SLAMissCollection.prototype['sla_misses'] = undefined;






export default SLAMissCollection;

