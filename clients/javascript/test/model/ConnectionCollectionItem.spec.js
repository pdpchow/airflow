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
    instance = new AirflowApiStable.ConnectionCollectionItem();
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

  describe('ConnectionCollectionItem', function() {
    it('should create an instance of ConnectionCollectionItem', function() {
      // uncomment below and update the code to test ConnectionCollectionItem
      //var instane = new AirflowApiStable.ConnectionCollectionItem();
      //expect(instance).to.be.a(AirflowApiStable.ConnectionCollectionItem);
    });

    it('should have the property connectionId (base name: "connection_id")', function() {
      // uncomment below and update the code to test the property connectionId
      //var instane = new AirflowApiStable.ConnectionCollectionItem();
      //expect(instance).to.be();
    });

    it('should have the property connType (base name: "conn_type")', function() {
      // uncomment below and update the code to test the property connType
      //var instane = new AirflowApiStable.ConnectionCollectionItem();
      //expect(instance).to.be();
    });

    it('should have the property host (base name: "host")', function() {
      // uncomment below and update the code to test the property host
      //var instane = new AirflowApiStable.ConnectionCollectionItem();
      //expect(instance).to.be();
    });

    it('should have the property login (base name: "login")', function() {
      // uncomment below and update the code to test the property login
      //var instane = new AirflowApiStable.ConnectionCollectionItem();
      //expect(instance).to.be();
    });

    it('should have the property schema (base name: "schema")', function() {
      // uncomment below and update the code to test the property schema
      //var instane = new AirflowApiStable.ConnectionCollectionItem();
      //expect(instance).to.be();
    });

    it('should have the property port (base name: "port")', function() {
      // uncomment below and update the code to test the property port
      //var instane = new AirflowApiStable.ConnectionCollectionItem();
      //expect(instance).to.be();
    });

  });

}));
