define(["QUnit", "react", "test_utils", "jquery", "learning_resources"],
  function (QUnit, React, TestUtils, $, LearningResources) {
    'use strict';

    var TermList = LearningResources.TermList;

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
    var termResponseEasy = {
      "id": 1,
      "slug": "easy",
      "label": "easy",
      "weight": 1
    };
    var termResponseHard = {
      "id": 2,
      "slug": "hard",
      "label": "hard",
      "weight": 1
    };
    var preReqTermsResponseReq = {
      "id": 3,
      "slug": "required",
      "label": "required",
      "weight": 1
    };
    var preReqTermsResponseNotReq = {
      "id": 4,
      "slug": "notrequired",
      "label": "notrequired",
      "weight": 1
    };
    var vocabularyResponsePrereq = {
      "id": 1,
      "slug": "prerequisite",
      "name": "prerequisite",
      "description": "Prerequisite",
      "vocabulary_type": "m",
      "required": false,
      "weight": 2147483647,
      "terms": [preReqTermsResponseReq, preReqTermsResponseNotReq],
      "multi_terms": true
    };
    var vocabularyResponseDifficulty = {
      "id": 2,
      "slug": "difficulty",
      "name": "difficulty",
      "description": "Difficulty",
      "vocabulary_type": "f",
      "required": false,
      "weight": 2147483647,
      "terms": [termResponseEasy, termResponseHard],
      "multi_terms": true
    };
    var vocabulariesAndTerms = [
      {
        "terms": [preReqTermsResponseReq, preReqTermsResponseNotReq],
        "selectedTerms": [preReqTermsResponseReq, preReqTermsResponseNotReq],
        'vocabulary': vocabularyResponsePrereq,
      },
      {
        "terms": [termResponseEasy, termResponseHard],
        "selectedTerms": [termResponseEasy, termResponseHard],
        'vocabulary': vocabularyResponseDifficulty,
      }
    ];

    QUnit.module('Test term list', {
      beforeEach: function () {
        TestUtils.setup();
      },
      afterEach: function () {
        TestUtils.cleanup();
      }
    });

    QUnit.test(
      'Assert that TermList renders properly',
      function (assert) {
        var done = assert.async();
        var afterMount = function (component) {
          var $node = $(React.findDOMNode(component));
          var $termList = $node.find("ul");
          assert.equal($termList.size(), 1);
          done();
        };

        React.addons.TestUtils.renderIntoDocument(
          <TermList
            vocabs={vocabulariesAndTerms}
            ref={afterMount}
            />
        );
      }
    );
  }
);
