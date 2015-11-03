define(['QUnit', 'test_utils', 'react', 'jquery', 'confirmation_dialog'],
  function (QUnit, TestUtils, React, $, ConfirmationDialog) {
    'use strict';

    QUnit.module('Tests for ConfirmationDialog', {
      beforeEach: function () {
        TestUtils.setup();
      },
      afterEach: function() {
        TestUtils.cleanup();
      }
    });

    QUnit.test("Assert that ConfirmationDialog  renders " +
      "proper props",
      function (assert) {
        var container = document.createElement("div");
        assert.equal(0, $(container).find(".modal").size());
        var options = {
          actionButtonName: "Delete",
          actionButtonClass: "btn btn-danger btn-ok",
          title: "Delete ?",
          message: "Are you sure you want to delete vocabulary ?",
          description: "Deleting this vocabulary will remove it from all " +
          "learning resources.",
          confirmationHandler: function () {
          }
        };
        React.render(<ConfirmationDialog {...options} />, container);
        assert.equal(1, $(container).find(".modal").size());
      }
    );
  }
);
