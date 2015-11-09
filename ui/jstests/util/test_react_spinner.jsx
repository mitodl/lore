define(['QUnit', 'jquery', 'react', 'test_utils', 'react_spinner'],
  function (QUnit, $, React, TestUtils, ReactSpinner) {
    "use strict";

    QUnit.module('Test ReactSpinner', {
      beforeEach: function () {
        TestUtils.setup();
      },
      afterEach: function () {
        TestUtils.cleanup();
      }
    });

    QUnit.test('Test turning spinner on', function (assert) {
      var done = assert.async();

      var afterMount = function (component) {
        // Assert that spinner turns on.
        assert.equal(
          $(React.findDOMNode(component)).find(".spinner").size(),
          1
        );
        done();
      };

      React.addons.TestUtils.renderIntoDocument(
        <ReactSpinner ref={afterMount}/>
      );
    });
  }
);
