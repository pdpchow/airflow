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
import DAG from './DAG';
import TaskExtraLinks from './TaskExtraLinks';
import TimeDelta from './TimeDelta';
import TriggerRule from './TriggerRule';
import WeightRule from './WeightRule';

/**
 * The Task model module.
 * @module model/Task
 * @version 1.0.0
 */
class Task {
    /**
     * Constructs a new <code>Task</code>.
     * @alias module:model/Task
     */
    constructor() { 
        
        Task.initialize(this);
    }

    /**
     * Initializes the fields of this object.
     * This method is used by the constructors of any subclasses, in order to implement multiple inheritance (mix-ins).
     * Only for internal use.
     */
    static initialize(obj) { 
    }

    /**
     * Constructs a <code>Task</code> from a plain JavaScript object, optionally creating a new instance.
     * Copies all relevant properties from <code>data</code> to <code>obj</code> if supplied or a new instance if not.
     * @param {Object} data The plain JavaScript object bearing properties of interest.
     * @param {module:model/Task} obj Optional instance to populate.
     * @return {module:model/Task} The populated <code>Task</code> instance.
     */
    static constructFromObject(data, obj) {
        if (data) {
            obj = obj || new Task();

            if (data.hasOwnProperty('class_ref')) {
                obj['class_ref'] = ClassReference.constructFromObject(data['class_ref']);
            }
            if (data.hasOwnProperty('task_id')) {
                obj['task_id'] = ApiClient.convertToType(data['task_id'], 'String');
            }
            if (data.hasOwnProperty('owner')) {
                obj['owner'] = ApiClient.convertToType(data['owner'], 'String');
            }
            if (data.hasOwnProperty('start_date')) {
                obj['start_date'] = ApiClient.convertToType(data['start_date'], 'Date');
            }
            if (data.hasOwnProperty('end_date')) {
                obj['end_date'] = ApiClient.convertToType(data['end_date'], 'Date');
            }
            if (data.hasOwnProperty('trigger_rule')) {
                obj['trigger_rule'] = TriggerRule.constructFromObject(data['trigger_rule']);
            }
            if (data.hasOwnProperty('extra_links')) {
                obj['extra_links'] = ApiClient.convertToType(data['extra_links'], [TaskExtraLinks]);
            }
            if (data.hasOwnProperty('depends_on_past')) {
                obj['depends_on_past'] = ApiClient.convertToType(data['depends_on_past'], 'Boolean');
            }
            if (data.hasOwnProperty('wait_for_downstream')) {
                obj['wait_for_downstream'] = ApiClient.convertToType(data['wait_for_downstream'], 'Boolean');
            }
            if (data.hasOwnProperty('retries')) {
                obj['retries'] = ApiClient.convertToType(data['retries'], 'Number');
            }
            if (data.hasOwnProperty('queue')) {
                obj['queue'] = ApiClient.convertToType(data['queue'], 'String');
            }
            if (data.hasOwnProperty('pool')) {
                obj['pool'] = ApiClient.convertToType(data['pool'], 'String');
            }
            if (data.hasOwnProperty('pool_slots')) {
                obj['pool_slots'] = ApiClient.convertToType(data['pool_slots'], 'Number');
            }
            if (data.hasOwnProperty('execution_timeout')) {
                obj['execution_timeout'] = TimeDelta.constructFromObject(data['execution_timeout']);
            }
            if (data.hasOwnProperty('retry_delay')) {
                obj['retry_delay'] = TimeDelta.constructFromObject(data['retry_delay']);
            }
            if (data.hasOwnProperty('retry_exponential_backoff')) {
                obj['retry_exponential_backoff'] = ApiClient.convertToType(data['retry_exponential_backoff'], 'Boolean');
            }
            if (data.hasOwnProperty('priority_weight')) {
                obj['priority_weight'] = ApiClient.convertToType(data['priority_weight'], 'Number');
            }
            if (data.hasOwnProperty('weight_rule')) {
                obj['weight_rule'] = WeightRule.constructFromObject(data['weight_rule']);
            }
            if (data.hasOwnProperty('ui_color')) {
                obj['ui_color'] = ApiClient.convertToType(data['ui_color'], 'String');
            }
            if (data.hasOwnProperty('ui_fgcolor')) {
                obj['ui_fgcolor'] = ApiClient.convertToType(data['ui_fgcolor'], 'String');
            }
            if (data.hasOwnProperty('template_fields')) {
                obj['template_fields'] = ApiClient.convertToType(data['template_fields'], ['String']);
            }
            if (data.hasOwnProperty('sub_dag')) {
                obj['sub_dag'] = DAG.constructFromObject(data['sub_dag']);
            }
            if (data.hasOwnProperty('downstream_task_ids')) {
                obj['downstream_task_ids'] = ApiClient.convertToType(data['downstream_task_ids'], ['String']);
            }
        }
        return obj;
    }


}

/**
 * @member {module:model/ClassReference} class_ref
 */
Task.prototype['class_ref'] = undefined;

/**
 * @member {String} task_id
 */
Task.prototype['task_id'] = undefined;

/**
 * @member {String} owner
 */
Task.prototype['owner'] = undefined;

/**
 * @member {Date} start_date
 */
Task.prototype['start_date'] = undefined;

/**
 * @member {Date} end_date
 */
Task.prototype['end_date'] = undefined;

/**
 * @member {module:model/TriggerRule} trigger_rule
 */
Task.prototype['trigger_rule'] = undefined;

/**
 * @member {Array.<module:model/TaskExtraLinks>} extra_links
 */
Task.prototype['extra_links'] = undefined;

/**
 * @member {Boolean} depends_on_past
 */
Task.prototype['depends_on_past'] = undefined;

/**
 * @member {Boolean} wait_for_downstream
 */
Task.prototype['wait_for_downstream'] = undefined;

/**
 * @member {Number} retries
 */
Task.prototype['retries'] = undefined;

/**
 * @member {String} queue
 */
Task.prototype['queue'] = undefined;

/**
 * @member {String} pool
 */
Task.prototype['pool'] = undefined;

/**
 * @member {Number} pool_slots
 */
Task.prototype['pool_slots'] = undefined;

/**
 * @member {module:model/TimeDelta} execution_timeout
 */
Task.prototype['execution_timeout'] = undefined;

/**
 * @member {module:model/TimeDelta} retry_delay
 */
Task.prototype['retry_delay'] = undefined;

/**
 * @member {Boolean} retry_exponential_backoff
 */
Task.prototype['retry_exponential_backoff'] = undefined;

/**
 * @member {Number} priority_weight
 */
Task.prototype['priority_weight'] = undefined;

/**
 * @member {module:model/WeightRule} weight_rule
 */
Task.prototype['weight_rule'] = undefined;

/**
 * @member {String} ui_color
 */
Task.prototype['ui_color'] = undefined;

/**
 * @member {String} ui_fgcolor
 */
Task.prototype['ui_fgcolor'] = undefined;

/**
 * @member {Array.<String>} template_fields
 */
Task.prototype['template_fields'] = undefined;

/**
 * @member {module:model/DAG} sub_dag
 */
Task.prototype['sub_dag'] = undefined;

/**
 * @member {Array.<String>} downstream_task_ids
 */
Task.prototype['downstream_task_ids'] = undefined;






export default Task;

