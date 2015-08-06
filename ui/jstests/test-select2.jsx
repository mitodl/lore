define(['QUnit', 'jquery', 'utils', 'reactaddons',
  'test_utils'], function(
  QUnit, $, Utils, React, TestUtils) {
    'use strict';

    var Select2 = Utils.Select2;
    var options = [
      {id: 'one', text: 'One'},
      {id: 'two', text: 'Two'},
      {id: 'three', text: 'Three'}
    ];

    QUnit.module('Tests for Select2', {
      beforeEach: function () {
        TestUtils.setup();

      },
      afterEach: function() {
        TestUtils.cleanup();
      }
    });

    QUnit.test('Test Select2 defaults', function(assert) {
      var done = assert.async();
      var afterMount = function(component) {
        var node = React.findDOMNode(component);
        var $select = $(node).find("select");

        assert.equal($select.length, 1);
        assert.equal($select.val(), null);

        done();
      };

      React.addons.TestUtils.renderIntoDocument(
        <Select2 ref={afterMount} />
      );
    });

    QUnit.test('Assert onChange handler', function(assert) {
      var done = assert.async();

      var onChange = function(e) {
        assert.equal(e.target.value, "two");
        done();
      };

      var afterMount = function(component) {
        var select = $(React.findDOMNode(component)).find("select")[0];
        $(select).val('two').trigger('change');
      };

      React.addons.TestUtils.renderIntoDocument(
        <Select2 ref={afterMount}
                 options={options}
                 onChange={onChange} />
      );
    });

    QUnit.test('Assert onChange handler for multi select', function(assert) {
      var done = assert.async();

      var onChange = function(e) {
        assert.equal($(e.target).val(), "two,three");
        done();
      };

      var afterMount = function(component) {
        var select = $(React.findDOMNode(component)).find("select")[0];
        $(select).val(['two', 'three']).trigger('change');
      };

      React.addons.TestUtils.renderIntoDocument(
        <Select2 ref={afterMount}
                 options={options}
                 multiple={true}
                 onChange={onChange} />
      );
    });

    QUnit.test('Assert onChange handler for deselect', function(assert) {
      var done = assert.async();
      var onChange = function(e) {
        assert.equal(e.target.value, "two");
        done();
      };

      var afterMount = function(component) {
        var select = $(React.findDOMNode(component)).find("select")[0];
        $(select).val(['two']).trigger('change');
      };

      React.addons.TestUtils.renderIntoDocument(
        <Select2 ref={afterMount}
                 options={options}
                 multiple={true}
                 values={['one', 'two']}
                 onChange={onChange} />
      );
    });
  }
);
