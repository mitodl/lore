define(['QUnit', 'jquery', 'lodash', 'manage_taxonomies', 'react',
    'test_utils'],
  function (QUnit, $, _, ManageTaxonomies, React, TestUtils) {
    'use strict';

    var waitForAjax = TestUtils.waitForAjax;
    var AddTermsComponent = ManageTaxonomies.AddTermsComponent;

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

    /**
     * Common assertions for Add terms, use in term and taxonomy
     * components tests
     * @param {QUnit.assert} assert - For assertions
     * @param {ReactComponent} component - Root DOM object in react class
     * @return {ReactComponent} devItems - DOM object of class 'panel-body'
     * */
    function assertAddTermCommon(assert, component) {
      // check term title
      var node = React.findDOMNode(component);
      var $vocabTitles = $(node).find(".vocab-title");
      assert.equal($vocabTitles.length, 1);
      assert.equal($vocabTitles[0].innerHTML, vocabulary.name);
      //test items
      var devItems = React.addons.TestUtils.
        findRenderedDOMComponentWithClass(
        component,
        'panel-body'
      );
      var itemList = React.addons.TestUtils.
        scryRenderedDOMComponentsWithTag(
        devItems,
        'li'
      );
      assert.equal(itemList.length, 3);
      return devItems;
    }

    QUnit.module('Test AddTermsComponent', {
      beforeEach: function () {
        var listOfTerms = {
          "count": 2,
          "next": null,
          "previous": null,
          "results": vocabulary.terms
        };
        var term = {
          "id": 9,
          "slug": "test",
          "label": "test",
          "weight": 1
        };
        TestUtils.setup();
        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo/vocabularies/easy/terms/",
          type: "POST",
          status: 400
        });
        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo/vocabularies/difficulty/terms/",
          responseText: term,
          type: "POST"
        });
        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo/vocabularies/difficulty/terms/",
          responseText: listOfTerms,
          type: "GET"
        });
        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo/vocabularies/difficulty/",
          type: "DELETE"
        });
      },
      afterEach: function () {
        TestUtils.cleanup();
      }
    });

    QUnit.test('Assert that AddTermsComponent work properly',
      function (assert) {
        assert.ok(AddTermsComponent, "class object not found");
        var vocabularies = [
          {
            "vocabulary": vocabulary,
            "terms": vocabulary.terms
          }
        ];
        var done = assert.async();
        var addTermCalled = 0;
        var addTerm = function () {
          addTermCalled += 1;
        };

        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };

        var errorMessage;
        var reportMessage = function (message) {
          errorMessage = message;
        };

        var loadedState;
        var setLoadedState = function (loaded) {
          loadedState = loaded;
        };

        var editVocabulary = function () {
        };
        var afterMount = function (component) {
          assert.equal(
            errorMessage,
            undefined
          );
          assertAddTermCommon(assert, component);
          //test error message
          component.reportMessage({
            error: "Error occurred while adding new term."
          });
          component.forceUpdate(function () {
            assert.deepEqual(
              errorMessage,
              {error: 'Error occurred while adding new term.'}
            );
            var inputGroup = React.addons.TestUtils.
              findRenderedDOMComponentWithClass(
              component,
              'input-group'
            );
            var textbox = React.addons.TestUtils.
              findRenderedDOMComponentWithTag(
              inputGroup,
              'input'
            );
            React.addons.TestUtils.Simulate.keyUp(textbox, {key: "Enter"});
            component.forceUpdate(function () {
              assert.equal(loadedState, false);
              waitForAjax(1, function () {
                assert.equal(loadedState, true);
                //test items
                assert.equal(addTermCalled, 1);
                // listing page was asked to update
                assert.equal(refreshCount, 1);
                done();
              });
            });
          });
        };
        React.addons.TestUtils.
          renderIntoDocument(
          <AddTermsComponent
            editVocabulary={editVocabulary}
            vocabularies={vocabularies}
            repoSlug="repo"
            addTerm={addTerm}
            refreshFromAPI={refreshFromAPI}
            reportMessage={reportMessage}
            setLoadedState={setLoadedState}
            ref={afterMount}
            />
        );
      }
    );

  }
);
