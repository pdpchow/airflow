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

(function(root, factory) {
  if (typeof define === 'function' && define.amd) {
    // AMD.
    define(['expect.js', process.cwd()+'/src/index'], factory);
  } else if (typeof module === 'object' && module.exports) {
    // CommonJS-like environments that support module.exports, like Node.
    factory(require('expect.js'), require(process.cwd()+'/src/index'));
  } else {
    // Browser globals (root is window)
    factory(root.expect, root.AirflowApiStable);
  }
}(this, function(expect, AirflowApiStable) {
  'use strict';

  var instance;

  beforeEach(function() {
    instance = new AirflowApiStable.XCom();
  });

  var getProperty = function(object, getter, property) {
    // Use getter method if present; otherwise, get the property directly.
    if (typeof object[getter] === 'function')
      return object[getter]();
    else
      return object[property];
  }

  var setProperty = function(object, setter, property, value) {
    // Use setter method if present; otherwise, set the property directly.
    if (typeof object[setter] === 'function')
      object[setter](value);
    else
      object[property] = value;
  }

  describe('XCom', function() {
    it('should create an instance of XCom', function() {
      // uncomment below and update the code to test XCom
      //var instane = new AirflowApiStable.XCom();
      //expect(instance).to.be.a(AirflowApiStable.XCom);
    });

    it('should have the property key (base name: "key")', function() {
      // uncomment below and update the code to test the property key
      //var instane = new AirflowApiStable.XCom();
      //expect(instance).to.be();
    });

    it('should have the property timestamp (base name: "timestamp")', function() {
      // uncomment below and update the code to test the property timestamp
      //var instane = new AirflowApiStable.XCom();
      //expect(instance).to.be();
    });

    it('should have the property executionDate (base name: "execution_date")', function() {
      // uncomment below and update the code to test the property executionDate
      //var instane = new AirflowApiStable.XCom();
      //expect(instance).to.be();
    });

    it('should have the property taskId (base name: "task_id")', function() {
      // uncomment below and update the code to test the property taskId
      //var instane = new AirflowApiStable.XCom();
      //expect(instance).to.be();
    });

    it('should have the property dagId (base name: "dag_id")', function() {
      // uncomment below and update the code to test the property dagId
      //var instane = new AirflowApiStable.XCom();
      //expect(instance).to.be();
    });

    it('should have the property value (base name: "value")', function() {
      // uncomment below and update the code to test the property value
      //var instane = new AirflowApiStable.XCom();
      //expect(instance).to.be();
    });

  });

}));
