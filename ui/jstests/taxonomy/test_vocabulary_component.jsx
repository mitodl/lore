define(['QUnit', 'jquery', 'lodash', 'manage_taxonomies', 'react',
    'test_utils'],
  function (QUnit, $, _, ManageTaxonomies, React, TestUtils) {
    'use strict';

    var VocabularyComponent = ManageTaxonomies.VocabularyComponent;
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

    QUnit.module('Test VocabularyComponent', {
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

    QUnit.test('Assert that VocabularyComponent renders properly',
      function (assert) {
        assert.ok(VocabularyComponent, "class object not found");
        var done = assert.async();

        var showConfirmationDialog = function (options) {
          options.confirmationHandler(true);
        };

        var addTermCalled = 0;
        var deleteVocabularyCalled = 0;
        var editVocabularyButton;
        var editVocabularyCalled = 0;

        var addTerm = function () {
          addTermCalled += 1;
        };
        var deleteVocabulary = function () {
          deleteVocabularyCalled += 1;
        };

        var editVocabulary = function () {
          editVocabularyCalled += 1;
        };

        var reportMessage = function () {
        };

        var loadedState;
        var setLoadedState = function (loaded) {
          loadedState = loaded;
        };

        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };
        var afterMount = function (component) {
          var node = React.findDOMNode(component);

          // check vocab title
          var $vocabLinks = $(node).find(".vocab-title");
          assert.equal($vocabLinks.length, 1);
          assert.equal($vocabLinks[0].innerHTML, vocabulary.name);

          // assert collapse id and href
          assert.equal(
            $(node).find(".panel-collapse.collapse.in").attr("id"),
            "collapse-vocab-" + vocabulary.id
          );
          assert.equal(
            $(node).find("a.accordion-toggle").attr("href"),
            "#collapse-vocab-" + vocabulary.id
          );

          //test items
          var devItems = React.addons.TestUtils.
            findRenderedDOMComponentWithClass(
            component,
            'panel-body'
          );
          var buttons = React.addons.TestUtils.
            scryRenderedDOMComponentsWithClass(
            component,
            'fa-pencil'
          );
          editVocabularyButton = buttons[0];
          var itemList = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
            devItems,
            'li'
          );
          assert.equal(itemList.length, 3);

          var actionButtons = React.addons.TestUtils.
            scryRenderedDOMComponentsWithClass(
            component,
            'delete-vocabulary'
          );

          assert.equal(refreshCount, 0);
          var deleteVocabularyButton = actionButtons[0];
          React.addons.TestUtils.Simulate.click(deleteVocabularyButton);
          component.forceUpdate(function () {
            waitForAjax(1, function () {
              // listing page asked to refresh
              assert.equal(refreshCount, 1);

              assert.equal(deleteVocabularyCalled, 1);
              //test enter text in input text
              var inputNode = React.addons.TestUtils.
                findRenderedDOMComponentWithTag(
                component,
                'input'
              );
              React.addons.TestUtils.Simulate.change(
                inputNode,
                {target: {value: 'test12'}}
              );
              component.forceUpdate(function () {
                node = React.findDOMNode(component);
                var textbox = $(node).find("input")[0];
                assert.equal(
                  'test12',
                  component.state.newTermLabel
                );
                React.addons.TestUtils.Simulate.keyUp(textbox, {key: "x"});
                component.forceUpdate(function () {
                  assert.equal(addTermCalled, 0);

                  React.addons.TestUtils.Simulate.click(editVocabularyButton);
                  component.forceUpdate(function () {
                    assert.equal(editVocabularyCalled, 1);
                    node = React.findDOMNode(component);
                    var textbox = $(node).find("input")[0];
                    assert.equal(
                      'test12',
                      component.state.newTermLabel
                    );
                    React.addons.TestUtils.Simulate.keyUp(
                      textbox, {key: "Enter"}
                    );
                    assert.equal(loadedState, false);
                    waitForAjax(1, function () {
                      assert.equal(loadedState, true);
                      assert.equal(addTermCalled, 1);
                      done();
                    });
                  });
                });
              });
            });
          });
        };
        React.addons.TestUtils.
          renderIntoDocument(
          <VocabularyComponent
            editVocabulary={editVocabulary}
            vocabulary={vocabulary}
            terms={vocabulary.terms}
            reportMessage={reportMessage}
            deleteVocabulary={deleteVocabulary}
            renderConfirmationDialog={showConfirmationDialog}
            addTerm={addTerm}
            repoSlug="repo"
            refreshFromAPI={refreshFromAPI}
            setLoadedState={setLoadedState}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that ajax fail VocabularyComponent',
      function (assert) {
        var done = assert.async();
        var vocabulary = {
          "id": 2,
          "slug": "easy",
          "name": "easy",
          "description": "easy",
          "vocabulary_type": "m",
          "required": false,
          "weight": 2147483647,
          "terms": []
        };
        var addTermCalled = 0;
        var message;
        var addTerm = function () {
          addTermCalled += 1;
        };
        var reportMessage = function (msg) {
          message = msg;
        };

        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };

        var loadedState;
        var setLoadedState = function (loaded) {
          loadedState = loaded;
        };

        var afterMount = function (component) {
          // wait for calls to populate form
          var node = React.findDOMNode(component);
          var textbox = $(node).find("input")[0];
          React.addons.TestUtils.Simulate.keyUp(textbox, {key: "Enter"});
          assert.equal(loadedState, false);
          waitForAjax(1, function () {
            assert.equal(loadedState, true);
            assert.equal(addTermCalled, 0);
            // refreshFromAPI was never called
            assert.equal(refreshCount, 0);
            // Error is caused by a 400 status code
            assert.deepEqual(
              message,
              {error: "Error occurred while adding new term."}
            );
            done();
          });
        };
        React.addons.TestUtils.
          renderIntoDocument(
          <VocabularyComponent
            vocabulary={vocabulary}
            terms={vocabulary.terms}
            reportMessage={reportMessage}
            addTerm={addTerm}
            repoSlug="repo"
            refreshFromAPI={refreshFromAPI}
            setLoadedState={setLoadedState}
            ref={afterMount}
            />
        );
      }
    );

  }
);
