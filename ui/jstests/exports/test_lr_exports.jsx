define(['QUnit', 'jquery', 'lr_exports', 'react', 'test_utils'],
  function (QUnit, $, Exports, React, TestUtils) {
    'use strict';

    QUnit.module('Test exports', {
      beforeEach: function () {
        TestUtils.setup();
        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo/learning_resource_exports/user/',
          type: 'GET',
          responseText: {
            "count": 1,
            "next": null,
            "previous": null,
            "results": [{"id": 123}]
          }
        });
      },
      afterEach: function () {
        TestUtils.cleanup();
      }
    });

    QUnit.test(
      'Verify exports panel header renders properly',
      function (assert) {
        var container = document.createElement("div");
        Exports.loadExportsHeader(0, container);
        assert.equal(1, $(container).children().size());
        assert.equal("Export", $(container).text().trim());
        Exports.loadExportsHeader(3, container);
        assert.equal(1, $(container).children().size());
        assert.equal("Export (3)", $(container).text().trim());
      }
    );

    QUnit.test("Test resource export panel renders into div",
      function (assert) {
        var container = document.createElement("div");

        assert.equal(0, $(container).find("div").size());
        Exports.loader("repo", "user", function () {
        }, container);
        assert.equal(1, $(container).find("div").size());
      }
    );
  }
);
