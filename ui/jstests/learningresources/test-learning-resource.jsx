define(
  ['QUnit', 'test_utils', 'jquery', 'react', 'lodash', 'learning_resources',
    'jquery_mockjax'],
  function (QUnit, TestUtils, $, React, _, LearningResources) {
    'use strict';

    var learningResourceResponse = {
      "id": 1,
      "learning_resource_type": "course",
      "static_assets": [],
      "title": "title",
      "materialized_path": "/course",
      "content_xml": "<course />",
      "url_path": "",
      "parent": null,
      "copyright": "",
      "xa_nr_views": 0,
      "xa_nr_attempts": 0,
      "xa_avg_grade": 0.0,
      "xa_histogram_grade": 0.0,
      "terms": ["required"]
    };
    var learningResourceResponseMinusContentXml = $.extend(
      {}, learningResourceResponse);
    delete learningResourceResponseMinusContentXml.content_xml;

    QUnit.module('Test learning resource', {
      beforeEach: function() {
        TestUtils.setup();
        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo/learning_resources/' +
          '1/?remove_content_xml=true',
          type: 'GET',
          responseText: learningResourceResponseMinusContentXml
        });
      },
      afterEach: function() {
        TestUtils.cleanup();
      }
    });

    QUnit.test(
      "LearningResourcePanel.loader should populate its stuff",
      function (assert) {
        var div = document.createElement("div");
        assert.ok($(div).html().length === 0);
        LearningResources.loader("repo", "1", function () {
        }, function () {
        }, div);
        assert.ok($(div).html().length > 0);
      }
    );
  });
