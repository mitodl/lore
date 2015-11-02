define(['QUnit', 'jquery', 'utils', 'test_utils', 'react'],
  function(QUnit, $, Utils, TestUtils, React) {
  'use strict';

  var ICheckbox = Utils.ICheckbox;

  QUnit.module("Test ICheckbox class", {
    beforeEach: function() {
      TestUtils.setup();
    },
    afterEach: function() {
      TestUtils.cleanup();
    }
  });

  QUnit.test("Test that ICheckbox callback works", function(assert) {
    var done = assert.async();

    var lastChange = null;
    var count = 0;
    var onChange = function(e) {
      lastChange = e;
      count++;
    };

    var afterMount = function(component) {
      var node = React.findDOMNode(component);
      assert.equal(lastChange, null);
      assert.equal(count, 0);

      $(node).find("ins").click();
      assert.equal(lastChange.target.checked, true);
      assert.equal(count, 1);

      done();
    };

    React.addons.TestUtils.renderIntoDocument(
      <ICheckbox value="value" checked={false}
                 onChange={onChange}
                 ref={afterMount} />
    );
  });

  QUnit.test("Test that props are rendered as expected", function(assert) {
    var doneTrue = assert.async();
    var doneFalse = assert.async();

    var assertCheckedUI = function(node, checked) {
      var $ins = $(node).find("ins");
      assert.equal($ins.length, 1);
      var $input = $(node).find("input");
      assert.equal($input.length, 1);

      // Assert that actual checkbox is checked.
      assert.equal($input[0].checked, checked);
      // Assert that it looks checked from the outside.
      var numChecked = $(node).find(".checked").length;
      if (checked) {
        assert.equal(numChecked, 1);
      } else {
        assert.equal(numChecked, 0);
      }
    };

    var afterMountTrue = function(component) {
      var node = React.findDOMNode(component);
      assertCheckedUI(node, true);
      doneTrue();
    };

    var afterMountFalse = function(component) {
      var node = React.findDOMNode(component);
      assertCheckedUI(node, false);
      doneFalse();
    };

    React.addons.TestUtils.renderIntoDocument(
      <ICheckbox value="value" checked={true}
                 ref={afterMountTrue} />
    );
    React.addons.TestUtils.renderIntoDocument(
      <ICheckbox value="value" checked={false}
                 ref={afterMountFalse} />
    );
  });

  QUnit.test("Test default", function(assert) {
    var afterMount = function(component) {
      var node = React.findDOMNode(component);
      var numChecked = $(node).find(".checked").length;
      assert.equal(numChecked, 0);
    };

    React.addons.TestUtils.renderIntoDocument(
      <ICheckbox ref={afterMount} />
    );
  });
});
