define(['QUnit', 'jquery', 'lodash', 'taxonomy_component', 'react',
    'test_utils'],
  function (QUnit, $, _, TaxonomyComponent, React, TestUtils) {
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

    QUnit.module('Test TaxonomyComponent', {
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
          url: "/api/v1/repositories/repo/vocabularies/",
          contentType: "application/json; charset=utf-8",
          responseText: vocabulary,
          dataType: 'json',
          type: "POST"
        });
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
        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo/vocabularies/difficulty/",
          type: "DELETE"
        });
      },
      afterEach: function () {
        TestUtils.cleanup();
      }
    });

    QUnit.test('Assert that add term works in TaxonomyComponent',
      function (assert) {
        assert.ok(TaxonomyComponent, "class object not found");
        var vocabularyWithoutTerms = {
          "id": 2,
          "slug": "difficulty2",
          "name": "difficulty2",
          "description": "easy",
          "vocabulary_type": "f",
          "required": false,
          "weight": 2147483647,
        };

        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };
        var done = assert.async();

        var afterMount = function (component) {
          assert.deepEqual(component.state, {
            vocabularies: [],
            learningResourceTypes: [],
            editVocabId: undefined,
            vocabMessage: undefined,
            termsMessage: undefined
          });
          waitForAjax(2, function () {
            assert.equal(component.state.vocabularies.length, 1);
            assert.equal(component.state.vocabularies[0].terms.length, 2);
            assertAddTermCommon(assert, component);
            // Adding second Vocabulary to make sure term added to correct vocabulary
            component.addOrUpdateVocabulary(vocabularyWithoutTerms);
            component.forceUpdate(function () {
              assert.equal(component.state.vocabularies.length, 2);
              // listing page not asked to update
              assert.equal(refreshCount, 0);
              var inputGroup = React.addons.TestUtils.
                scryRenderedDOMComponentsWithClass(
                component,
                'input-group'
              );
              assert.equal(inputGroup.length, 2);
              var textbox = React.addons.TestUtils.
                findRenderedDOMComponentWithTag(
                inputGroup[0],
                'input'
              );
              assert.equal(component.state.vocabularies[0].terms.length, 2);
              React.addons.TestUtils.Simulate.keyUp(textbox, {key: "Enter"});
              waitForAjax(1, function () {
                assert.equal(component.state.vocabularies[0].terms.length, 3);
                assert.equal(refreshCount, 1);
                done();
              });
            });
          });
        };
        React.addons.TestUtils.renderIntoDocument
        (
          <TaxonomyComponent
            repoSlug="repo"
            renderConfirmationDialog={function() {}}
            refreshFromAPI={refreshFromAPI}
            showTab={function() {}}
            setTabName={function() {}}
            ref={afterMount}
            />
        );
      }
    );
    QUnit.test('Assert that add vocabulary works in TaxonomyComponent',
      function (assert) {
        assert.ok(TaxonomyComponent, "class object not found");
        var vocabularyWithoutTerms = {
          "id": 3,
          "slug": "apple",
          "name": "Apple",
          "description": "fruit",
          "vocabulary_type": "f",
          "required": false,
          "weight": 2147483640,
        };
        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };
        var done = assert.async();
        var afterMount = function (component) {
          assert.deepEqual(component.state, {
            vocabularies: [],
            learningResourceTypes: [],
            editVocabId: undefined,
            vocabMessage: undefined,
            termsMessage: undefined
          });
          waitForAjax(2, function () {
            assert.equal(
              component.state.vocabularies.length,
              1
            );
            assert.equal(
              component.state.learningResourceTypes.length,
              8
            );
            var formNode = React.addons.TestUtils.
              findRenderedDOMComponentWithClass(
              component,
              'form-horizontal'
            );
            // listing page not asked to update
            assert.equal(refreshCount, 0);
            assert.ok(formNode);
            //test form submission
            var inputNodes = React.addons.TestUtils.
              scryRenderedDOMComponentsWithTag(
              formNode,
              'input'
            );
            var buttonNodes = React.addons.TestUtils.
              scryRenderedDOMComponentsWithTag(
              formNode,
              'button'
            );
            var saveButton = buttonNodes[0];
            var inputVocabularyName = inputNodes[0];
            var inputVocabularyDesc = inputNodes[1];
            var checkboxCourse = inputNodes[2];

            React.addons.TestUtils.Simulate.change(
              inputVocabularyName, {target: {value: "TestA"}}
            );
            React.addons.TestUtils.Simulate.change(
              inputVocabularyDesc, {target: {value: "TestA"}}
            );
            React.addons.TestUtils.Simulate.change(
              checkboxCourse,
              {target: {value: 'course', checked: true}}
            );
            TestUtils.replaceMockjax({
              url: "/api/v1/repositories/repo/vocabularies/",
              type: "POST",
              responseText: {
                "id": 2,
                "slug": "test-a",
                "name": "TestA",
                "description": "TestA",
                "vocabulary_type": "m",
                "required": false,
                "weight": 1,
                "terms": []
              }
            });
            React.addons.TestUtils.Simulate.click(saveButton);
            waitForAjax(1, function () {
              assert.equal(
                component.state.vocabularies.length,
                2
              );

              // Assert that the vocabularies are sorted by case insensitive names
              assert.equal(
                component.state.vocabularies[0].vocabulary.name,
                "difficulty"
              );
              assert.equal(
                component.state.vocabularies[1].vocabulary.name,
                "TestA"
              );
              assert.equal(refreshCount, 1);

              component.addOrUpdateVocabulary(vocabularyWithoutTerms);
              component.forceUpdate(function () {
                assert.equal(component.state.vocabularies.length, 3);

                // Assert that the vocabularies are sorted by case insensitive names
                assert.equal(
                  component.state.vocabularies[0].vocabulary.name,
                  "Apple"
                );
                assert.equal(
                  component.state.vocabularies[1].vocabulary.name,
                  "difficulty"
                );
                assert.equal(
                  component.state.vocabularies[2].vocabulary.name,
                  "TestA"
                );

                // If the vocabulary already exists the count should not change.
                component.addOrUpdateVocabulary(vocabularyWithoutTerms);
                component.forceUpdate(function () {
                  assert.equal(component.state.vocabularies.length, 3);
                  done();
                });
              });
            });
          });
        };
        React.addons.TestUtils.renderIntoDocument
        (
          <TaxonomyComponent
            repoSlug="repo"
            renderConfirmationDialog={function() {}}
            refreshFromAPI={refreshFromAPI}
            showTab={function() {}}
            setTabName={function() {}}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that delete vocabulary works in TaxonomyComponent',
      function (assert) {
        assert.ok(TaxonomyComponent, "class object not found");
        var done = assert.async();
        var userSelectedConfirm = 0;
        var showConfirmationDialog = function (options) {
          options.confirmationHandler(true);
          userSelectedConfirm += 1;
        };

        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };

        var afterMount = function (component) {
          waitForAjax(2, function () {
            assert.equal(
              component.state.vocabularies.length,
              1
            );
            var actionButtons = React.addons.TestUtils.
              scryRenderedDOMComponentsWithClass(
              component,
              'delete-vocabulary'
            );
            var deleteVocabularyButton = actionButtons[0];
            React.addons.TestUtils.Simulate.click(deleteVocabularyButton);
            component.forceUpdate(function () {
              waitForAjax(1, function () {
                assert.equal(userSelectedConfirm, 1);
                assert.equal(
                  component.state.vocabularies.length,
                  0
                );
                assert.equal(refreshCount, 1);
                done();
              });
            });
          });
        };
        React.addons.TestUtils.renderIntoDocument
        (
          <TaxonomyComponent
            repoSlug="repo"
            renderConfirmationDialog={showConfirmationDialog}
            refreshFromAPI={refreshFromAPI}
            showTab={function() {}}
            setTabName={function() {}}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that delete vocabulary ajax call' +
      ' fail in TaxonomyComponent',
      function (assert) {
        assert.ok(TaxonomyComponent, "class object not found");
        var done = assert.async();
        var userSelectedConfirm = 0;
        var showConfirmationDialog = function (options) {
          options.confirmationHandler(true);
          userSelectedConfirm += 1;
        };

        TestUtils.replaceMockjax({
          url: "/api/v1/repositories/repo/vocabularies/" +
            vocabulary.slug + "/",
          type: "DELETE",
          status: 400
        });

        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };

        var afterMount = function (component) {
          waitForAjax(2, function () {
            assert.equal(
              component.state.vocabularies.length,
              1
            );
            var actionButtons = React.addons.TestUtils.
              scryRenderedDOMComponentsWithClass(
              component,
              'delete-vocabulary'
            );
            var deleteVocabularyButton = actionButtons[0];
            React.addons.TestUtils.Simulate.click(deleteVocabularyButton);
            waitForAjax(1, function () {
              component.forceUpdate(function () {
                assert.equal(userSelectedConfirm, 1);
                assert.equal(
                  component.state.vocabularies.length,
                  1
                );
                assert.equal(refreshCount, 0);
                done();
              });
            });
          });
        };
        React.addons.TestUtils.renderIntoDocument
        (
          <TaxonomyComponent
            repoSlug="repo"
            renderConfirmationDialog={showConfirmationDialog}
            refreshFromAPI={refreshFromAPI}
            showTab={function() {}}
            setTabName={function() {}}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that edit term works in TaxonomyComponent',
      function (assert) {
        assert.ok(TaxonomyComponent, "class object not found");
        var done = assert.async();
        var term = {
          "id": 1,
          "slug": "easy",
          "label": "TestB",
          "weight": 1
        };

        var listOfVocabularies = {
          "count": 2,
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
            },
            {
              "id": 2,
              "slug": "difficulty2",
              "name": "difficulty2",
              "description": "easy",
              "vocabulary_type": "f",
              "required": false,
              "weight": 2147483647,
              "terms": vocabulary.terms,
              "multi_terms": true
            }
          ]
        };

        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };

        TestUtils.initMockjax({
          url: "/api/v1/repositories/demo/vocabularies/",
          contentType: "application/json; charset=utf-8",
          responseText: listOfVocabularies,
          dataType: 'json',
          type: "GET"
        });

        var afterMount = function (component) {
          assert.equal(component.state.vocabularies.length, 0);
          waitForAjax(2, function () {
            assert.equal(component.state.vocabularies.length, 2);
            var difficultyVocab = _.find(
              component.state.vocabularies, function(vocab) {
                return vocab.vocabulary.name === "difficulty";
              }
            );
            assert.equal(difficultyVocab.terms.length, 2);
            var difficultTerm = _.find(difficultyVocab.terms, function(term) {
              return term.label === 'difficult';
            });
            var updateTermUrl = "/api/v1/repositories/demo/vocabularies/" +
              difficultyVocab.vocabulary.slug + "/terms/" +
              difficultTerm.slug + "/";
            TestUtils.initMockjax({
              url: updateTermUrl,
              responseText: term,
              type: "PATCH"
            });
            var editButtons = React.addons.TestUtils.
              scryRenderedDOMComponentsWithClass(
              component,
              'format-button'
            );
            var editButton = editButtons[0];
            //open edit mode
            React.addons.TestUtils.Simulate.click(editButton);
            component.forceUpdate(function () {
              var saveButtons = React.addons.TestUtils.
                scryRenderedDOMComponentsWithClass(
                component,
                'save-button'
              );
              var saveButton = saveButtons[0];

              var editTermBoxes = React.addons.TestUtils.
                scryRenderedDOMComponentsWithClass(
                component,
                'edit-term-box'
              );
              var editTermBox = editTermBoxes[0];
              //edit term
              React.addons.TestUtils.Simulate.change(
                editTermBox, {target: {value: "TestB"}}
              );
              component.forceUpdate(function () {
                //save term
                assert.equal($(React.findDOMNode(editTermBox)).val(), "TestB");
                React.addons.TestUtils.Simulate.click(saveButton);
                component.forceUpdate(function () {
                  //after saved term using api
                  waitForAjax(1, function () {
                    assert.equal(refreshCount, 1);
                    //assert term update
                    assert.equal(
                      component.state.vocabularies.length,
                      2
                    );
                    var difficultyVocab = _.find(
                      component.state.vocabularies, function(vocab) {
                        return vocab.vocabulary.name === "difficulty";
                      }
                    );
                    assert.equal(
                      difficultyVocab.terms.length,
                      2
                    );
                    assert.ok(
                      _.some(difficultyVocab.terms, function(term) {
                        return term.label === "TestB";
                      })
                    );
                    done();
                  });
                });
              });
            });
          });
        };
        React.addons.TestUtils.renderIntoDocument
        (
          <TaxonomyComponent
            repoSlug="demo"
            refreshFromAPI={refreshFromAPI}
            showTab={function() {}}
            setTabName={function() {}}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that update vocabulary works in TaxonomyComponent',
      function (assert) {
        assert.ok(TaxonomyComponent, "class object not found");
        var vocabularyUpdateResponse = {
          "id": 1,
          "slug": "difficulty",
          "name": "TestA",
          "description": "TestA",
          "vocabulary_type": "f",
          "required": false,
          "weight": 2147483647,
          "learning_resource_types": [
            "course", "chapter"
          ],
          "multi_terms": true,
        };
        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo/vocabularies/" +
          vocabulary.slug + "/",
          contentType: "application/json; charset=utf-8",
          responseText: vocabularyUpdateResponse,
          dataType: 'json',
          type: "PATCH"
        });
        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };

        var done = assert.async();
        var afterMount = function (component) {
          waitForAjax(2, function () {
            assert.equal(
              component.state.vocabularies.length,
              1
            );
            var buttons = React.addons.TestUtils.
              scryRenderedDOMComponentsWithClass(
              component,
              'fa-pencil'
            );
            var editVocabularyButton = buttons[0];
            React.addons.TestUtils.Simulate.click(editVocabularyButton);
            component.forceUpdate(function () {
              var formNode = React.addons.TestUtils.
                findRenderedDOMComponentWithClass(
                component,
                'form-horizontal'
              );
              assert.ok(formNode);
              //test form submission
              var inputNodes = React.addons.TestUtils.
                scryRenderedDOMComponentsWithTag(
                formNode,
                'input'
              );
              var buttonForm = React.addons.TestUtils.
                scryRenderedDOMComponentsWithTag(
                formNode,
                'button'
              );
              var updateButton = buttonForm[0];
              var inputVocabularyName = inputNodes[0];
              var inputVocabularyDesc = inputNodes[1];
              React.addons.TestUtils.Simulate.change(
                inputVocabularyName, {target: {value: "TestA"}}
              );
              component.forceUpdate(function () {
                React.addons.TestUtils.Simulate.change(
                  inputVocabularyDesc, {target: {value: "TestA"}}
                );
                component.forceUpdate(function () {
                  React.addons.TestUtils.Simulate.click(updateButton);
                  component.forceUpdate(function () {
                    waitForAjax(1, function () {
                      assert.equal(
                        component.state.vocabularies.length,
                        1
                      );
                      assert.equal(
                        component.state.vocabularies[0].vocabulary.name,
                        vocabularyUpdateResponse.name
                      );
                      assert.equal(
                        component.state.vocabularies[0].vocabulary.id,
                        vocabularyUpdateResponse.id
                      );
                      assert.equal(
                        component.state.vocabularies[0].vocabulary.description,
                        vocabularyUpdateResponse.description
                      );
                      done();
                    });
                  });
                });
              });
            });
          });
        };
        React.addons.TestUtils.renderIntoDocument
        (
          <TaxonomyComponent
            repoSlug="repo"
            refreshFromAPI={refreshFromAPI}
            showTab={function() {}}
            setTabName={function() {}}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that delete term works in TaxonomyComponent',
      function (assert) {
        assert.ok(TaxonomyComponent, "class object not found");
        var done = assert.async();
        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };

        var renderConfirmationDialog = function (options) {
          options.confirmationHandler(true);
        };

        var afterMount = function (component) {
          assert.equal(component.state.vocabularies.length, 0);
          waitForAjax(2, function () {
            assert.equal(component.state.vocabularies.length, 1);
            var difficultyVocab = _.find(component.state.vocabularies,
              function (vocab) {
                return vocab.vocabulary.name === 'difficulty';
              }
            );
            assert.equal(difficultyVocab.terms.length, 2);
            var difficultTerm = _.find(difficultyVocab.terms, function(term) {
              return term.label === 'difficult';
            });
            var updateTermUrl = "/api/v1/repositories/repo/vocabularies/" +
              difficultyVocab.vocabulary.slug + "/terms/" +
              difficultTerm.slug + "/";
            TestUtils.initMockjax({
              url: updateTermUrl,
              type: "DELETE"
            });
            var deleteButtons = React.addons.TestUtils.
              scryRenderedDOMComponentsWithClass(
              component,
              'revert-button'
            );
            var deleteButton = deleteButtons[0];
            //open edit mode
            React.addons.TestUtils.Simulate.click(deleteButton);
            component.forceUpdate(function () {
              waitForAjax(1, function () {
                assert.equal(refreshCount, 1);
                //assert term update
                assert.equal(component.state.vocabularies.length, 1);
                var difficultyVocab = _.find(component.state.vocabularies,
                  function(vocab) {
                    return vocab.vocabulary.name === 'difficulty';
                  }
                );
                assert.equal(
                  difficultyVocab.terms.length,
                  1
                );
                done();
              });
            });
          });
        };
        React.addons.TestUtils.renderIntoDocument
        (
          <TaxonomyComponent
            repoSlug="repo"
            refreshFromAPI={refreshFromAPI}
            renderConfirmationDialog={renderConfirmationDialog}
            ref={afterMount}
            />
        );
      }
    );

  }
);
