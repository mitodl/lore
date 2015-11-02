define(["QUnit", "react", "test_utils", "jquery", "lodash",
    "learning_resources"],
  function (QUnit, React, TestUtils, $, _, LearningResources) {
    'use strict';

    var waitForAjax = TestUtils.waitForAjax;
    var TermSelect = LearningResources.TermSelect;

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
    var termResponseMedium = {
      "id": 5,
      "slug": "medium",
      "label": "medium",
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
    var selectedVocabulary = vocabularyResponseDifficulty;
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
    var vocabulariesResponseFirst = {
      "count": 1,
      "next": "/api/v1/repositories/repo/vocabularies/?type_name=course&page=2",
      "previous": null,
      "results": [vocabularyResponseDifficulty]
    };
    var vocabulariesResponseSecond = {
      "count": 1,
      "next": null,
      "previous": "/api/v1/repositories/repo/vocabularies/?type_name=course",
      "results": [vocabularyResponsePrereq]
    };

    QUnit.module('Test term select', {
      beforeEach: function () {
        TestUtils.setup();

        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo/learning_resources/1/',
          type: 'GET',
          responseText: learningResourceResponse
        });
        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo/learning_resources/' +
          '1/?remove_content_xml=true',
          type: 'GET',
          responseText: learningResourceResponseMinusContentXml
        });
        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo/learning_resources/1/',
          type: 'PATCH',
          responseText: learningResourceResponse
        });
        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo/vocabularies/?type_name=course',
          type: 'GET',
          responseText: vocabulariesResponseFirst
        });
        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo/vocabularies/' +
            '?type_name=course&page=2',
          type: 'GET',
          responseText: vocabulariesResponseSecond
        });
        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo/vocabularies/difficulty/terms/',
          type: 'POST',
          responseText: termResponseMedium
        });
      },
      afterEach: function () {
        TestUtils.cleanup();
      }
    });

    QUnit.test(
      'Assert that TermSelect renders properly',
      function (assert) {
        var done = assert.async();

        var vocab = $.extend({}, selectedVocabulary);
        var appendTermSelectedVocabulary = function (term) {
          vocab.terms = vocab.terms.concat(term);
        };

        var loadedState;
        var setLoadedState = function (loaded) {
          loadedState = loaded;
        };

        var afterMount = function (component) {
          var $node = $(React.findDOMNode(component));

          var $termSelect = $node.find("select");
          assert.equal($termSelect.size(), 1);

          var $options = $termSelect.find("option");
          var values = _.map($options, function (option) {
            return $(option).val();
          });
          assert.deepEqual(values, ["easy", "hard"]);
          // Add a term via free tagging

          $termSelect
            .append($('<option />', {value: 'medium'}))
            .val(["hard", "easy", "medium"])
            .trigger('change');

          component.forceUpdate(function () {
            assert.equal(loadedState, false);
            waitForAjax(1, function () {
              assert.equal(loadedState, true);
              // term successfully added
              assert.equal(vocab.terms.length, 3);
              done();
            });
          });
        };

        React.addons.TestUtils.renderIntoDocument(
          <TermSelect
            setValues={function() {}}
            appendTermSelectedVocabulary={appendTermSelectedVocabulary}
            repoSlug="repo"
            setLoadedState={setLoadedState}
            reportMessage={function() {}}
            vocabs={vocabulariesAndTerms}
            selectedVocabulary={selectedVocabulary}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test(
      'Assert that TermSelect handles failure to add term gracefully',
      function (assert) {
        var done = assert.async();

        TestUtils.replaceMockjax({
          url: '/api/v1/repositories/repo/vocabularies/difficulty/terms/',
          type: 'POST',
          responseText: termResponseMedium,
          status: 400
        });

        var vocab = $.extend({}, selectedVocabulary);
        var appendTermSelectedVocabulary = function (term) {
          vocab.terms = vocab.terms.concat(term);
        };

        var loadedState;
        var setLoadedState = function (loaded) {
          loadedState = loaded;
        };

        var message;
        var reportMessage = function (m) {
          message = m;
        };

        var afterMount = function (component) {
          var $node = $(React.findDOMNode(component));

          var $termSelect = $node.find("select");
          assert.equal($termSelect.size(), 1);

          var $options = $termSelect.find("option");
          var values = _.map($options, function (option) {
            return $(option).val();
          });
          assert.deepEqual(values, ["easy", "hard"]);
          // Add a term via free tagging

          $termSelect
            .append($('<option />', {value: 'medium'}))
            .val(["hard", "easy", "medium"])
            .trigger('change');

          component.forceUpdate(function () {
            assert.equal(loadedState, false);
            waitForAjax(1, function () {
              assert.equal(loadedState, true);

              // Didn't change
              assert.equal(vocab.terms.length, 2);
              assert.deepEqual(
                message,
                {error: 'Error occurred while adding new term "medium".'}
              );
              done();
            });
          });
        };

        React.addons.TestUtils.renderIntoDocument(
          <TermSelect
            setValues={function() {}}
            appendTermSelectedVocabulary={appendTermSelectedVocabulary}
            repoSlug="repo"
            setLoadedState={setLoadedState}
            reportMessage={reportMessage}
            vocabs={vocabulariesAndTerms}
            selectedVocabulary={selectedVocabulary}
            ref={afterMount}
            />
        );
      }
    );
  }
);
