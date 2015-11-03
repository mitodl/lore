define(['QUnit', 'jquery', 'lodash', 'manage_taxonomies', 'react',
    'test_utils'],
  function (QUnit, $, _, ManageTaxonomies, React, TestUtils) {
    'use strict';

    var waitForAjax = TestUtils.waitForAjax;

    var vocabulary = {
      "id": 1,
      "slug": "difficulty",
      "name": "difficulty",
      "description": "easy",
      "vocabulary_type": "f",
      "required": false,
      "weight": 2147483647,
      "learning_resource_types": [
        "course"
      ],
      "multi_terms": true,
      "terms": [
        {
          "id": 1,
          "slug": "easy",
          "label": "easy",
          "weight": 1
        },
        {
          "id": 2,
          "slug": "difficult",
          "label": "difficult",
          "weight": 1
        }
      ]
    };
    var learningResourceTypesResponse = {
      "count": 8,
      "next": null,
      "previous": null,
      "results": [
        {
          "name": "course"
        },
        {
          "name": "chapter"
        },
        {
          "name": "sequential"
        },
        {
          "name": "vertical"
        },
        {
          "name": "html"
        },
        {
          "name": "video"
        },
        {
          "name": "discussion"
        },
        {
          "name": "problem"
        }
      ]
    };

    QUnit.module('Test manage taxonomies', {
      beforeEach: function () {
        var listOfVocabularies = {
          "count": 1,
          "next": null,
          "previous": null,
          "results": [
            {
              "id": 1,
              "slug": "difficulty",
              "name": "difficulty",
              "description": "easy",
              "vocabulary_type": "f",
              "required": false,
              "weight": 2147483647,
              "terms": vocabulary.terms,
              "multi_terms": true
            }
          ]
        };
        TestUtils.setup();
        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo/vocabularies/",
          contentType: "application/json; charset=utf-8",
          responseText: listOfVocabularies,
          dataType: 'json',
          type: "GET"
        });
        TestUtils.initMockjax({
          url: "/api/v1/learning_resource_types/",
          contentType: "application/json; charset=utf-8",
          responseText: learningResourceTypesResponse,
          dataType: 'json',
          type: "GET"
        });
      },
      afterEach: function () {
        TestUtils.cleanup();
      }
    });

    QUnit.test("Test that ManageTaxonomies.loader renders into div",
      function (assert) {
        var done = assert.async();

        var container = document.createElement("div");
        assert.ok($(container).html().length === 0);
        ManageTaxonomies.loader(
          "repo", container, function () {
          }, function () {
          }, function () {
          },
          function () {
          }
        );
        waitForAjax(2, function () {
          assert.ok($(container).html().length > 0);
          done();
        });
      }
    );
  });
