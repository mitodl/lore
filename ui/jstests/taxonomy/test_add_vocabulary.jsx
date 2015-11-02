define(['QUnit', 'jquery', 'lodash', 'manage_taxonomies', 'react',
    'test_utils'],
  function (QUnit, $, _, ManageTaxonomies, React, TestUtils) {
    'use strict';

    var waitForAjax = TestUtils.waitForAjax;
    var AddVocabulary = ManageTaxonomies.AddVocabulary;

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
    var propLearningResourceTypes = _.map(learningResourceTypesResponse.results,
      function (result) {
        return result.name;
      }
    );

    QUnit.module('Test AddVocabulary', {
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
          url: "/api/v1/repositories/repo/vocabularies/difficulty/",
          type: "DELETE"
        });
      },
      afterEach: function () {
        TestUtils.cleanup();
      }
    });

    QUnit.test('Assert that AddVocabulary work properly',
      function (assert) {
        assert.ok(AddVocabulary, "class object not found");
        var saveVocabularyResponse;
        var done = assert.async();
        var editVocabulary = function () {
        };
        var updateParent = function (data) {
          saveVocabularyResponse = data;
        };

        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };
        var afterMount = function (component) {
          assert.deepEqual(component.state, {
            name: '',
            description: '',
            vocabularyType: 'm',
            learningResourceTypes: [],
            multiTerms: false
          });
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
          var buttonNodes = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
            formNode,
            'button'
          );
          var saveButton = buttonNodes[0];
          assert.equal(inputNodes.length, 13);
          var inputVocabularyName = inputNodes[0];
          var inputVocabularyDesc = inputNodes[1];
          var radioTagStyle = inputNodes[11];
          var checkMultiTerms = inputNodes[12];

          React.addons.TestUtils.Simulate.change(
            inputVocabularyName, {target: {value: "TestA"}}
          );
          React.addons.TestUtils.Simulate.change(
            inputVocabularyDesc, {target: {value: "TestA"}}
          );
          React.addons.TestUtils.Simulate.change(
            radioTagStyle,
            {target: {value: 'f'}}
          );
          //change the default multi terms checkbox
          React.addons.TestUtils.Simulate.change(
            checkMultiTerms,
            {target: {checked: true}}
          );
          component.forceUpdate(function () {
            assert.deepEqual(component.state, {
              name: "TestA",
              description: "TestA",
              vocabularyType: "f",
              learningResourceTypes: [],
              multiTerms: true
            });
            React.addons.TestUtils.Simulate.click(saveButton);
            waitForAjax(1, function () {
              assert.equal(
                saveVocabularyResponse.id,
                vocabulary.id
              );
              //testing state is reset
              assert.deepEqual(component.state, {
                name: '',
                description: '',
                vocabularyType: 'm',
                learningResourceTypes: [],
                multiTerms: false
              });
              // listing page was asked to update
              assert.equal(refreshCount, 1);
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
              var radioTagStyle = inputNodes[11];
              var checkMultiTerms = inputNodes[12];

              React.addons.TestUtils.Simulate.change(
                inputVocabularyName, {target: {value: "TestB"}}
              );
              React.addons.TestUtils.Simulate.change(
                inputVocabularyDesc, {target: {value: "TestB"}}
              );
              React.addons.TestUtils.Simulate.change(
                checkboxCourse,
                {target: {value: 'course', checked: true}}
              );
              React.addons.TestUtils.Simulate.change(
                radioTagStyle,
                {target: {value: 'f', checked: true}}
              );
              //change the default multi terms checkbox
              React.addons.TestUtils.Simulate.change(
                checkMultiTerms,
                {target: {checked: true}}
              );
              component.forceUpdate(function () {
                assert.deepEqual(component.state, {
                  name: "TestB",
                  description: "TestB",
                  vocabularyType: "f",
                  learningResourceTypes: ['course'],
                  multiTerms: true
                });
                React.addons.TestUtils.Simulate.click(saveButton);
                waitForAjax(1, function () {
                  //testing state is reset
                  assert.deepEqual(component.state, {
                    name: '',
                    description: '',
                    vocabularyType: 'm',
                    learningResourceTypes: [],
                    multiTerms: false
                  });
                  assert.equal(
                    saveVocabularyResponse.id,
                    vocabulary.id
                  );
                  // clicking button caused listing page to update
                  assert.equal(refreshCount, 2);

                  React.addons.TestUtils.Simulate.change(
                    inputVocabularyName, {target: {value: "TestC"}}
                  );
                  React.addons.TestUtils.Simulate.change(
                    inputVocabularyDesc, {target: {value: "TestC"}}
                  );
                  React.addons.TestUtils.Simulate.change(
                    checkboxCourse,
                    {target: {value: 'course', checked: true}}
                  );
                  React.addons.TestUtils.Simulate.change(
                    radioTagStyle,
                    {target: {value: 'f', checked: true}}
                  );
                  React.addons.TestUtils.Simulate.change(
                    checkMultiTerms,
                    {target: {checked: true}}
                  );

                  component.forceUpdate(function () {
                    assert.deepEqual(component.state, {
                      name: "TestC",
                      description: "TestC",
                      vocabularyType: "f",
                      learningResourceTypes: ["course"],
                      multiTerms: true
                    });
                    //uncheck checkboxes
                    React.addons.TestUtils.Simulate.change(
                      checkboxCourse,
                      {target: {value: 'course', checked: false}}
                    );
                    React.addons.TestUtils.Simulate.change(
                      checkMultiTerms,
                      {target: {checked: false}}
                    );
                    component.forceUpdate(function () {
                      assert.deepEqual(component.state, {
                        name: "TestC",
                        description: "TestC",
                        vocabularyType: "f",
                        learningResourceTypes: [],
                        multiTerms: false
                      });
                      React.addons.TestUtils.Simulate.click(saveButton);
                      waitForAjax(1, function () {
                        assert.equal(refreshCount, 3);
                        //testing state is reset
                        assert.deepEqual(component.state, {
                          name: '',
                          description: '',
                          vocabularyType: 'm',
                          learningResourceTypes: [],
                          multiTerms: false
                        });
                        assert.equal(
                          saveVocabularyResponse.id,
                          vocabulary.id
                        );
                        done();
                      });
                    });
                  });
                });
              });
            });
          });
        };
        React.addons.TestUtils.
          renderIntoDocument(
          <AddVocabulary
            editVocabulary={editVocabulary}
            repoSlug="repo"
            updateParent={updateParent}
            learningResourceTypes={propLearningResourceTypes}
            refreshFromAPI={refreshFromAPI}
            setLoadedState={function() {}}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that ajax fail in AddVocabulary',
      function (assert) {
        assert.ok(AddVocabulary, "class object not found");
        var done = assert.async();
        var editVocabulary = function () {
        };
        var updateParent = function () {
        };
        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };
        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo2/vocabularies/",
          type: "POST",
          status: 400
        });

        var vocabMessage;
        var reportMessage = function (message) {
          vocabMessage = message;
        };

        var afterMount = function (component) {
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
          var buttonNodes = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
            formNode,
            'button'
          );
          var saveButton = buttonNodes[0];
          assert.equal(inputNodes.length, 13);
          var inputVocabularyName = inputNodes[0];
          var inputVocabularyDesc = inputNodes[1];
          var checkboxCourse = inputNodes[2];

          React.addons.TestUtils.Simulate.change(
            inputVocabularyName, {target: {value: "TestB"}}
          );
          component.forceUpdate(function () {
            assert.equal(component.state.name, "TestB");
            React.addons.TestUtils.Simulate.change(
              inputVocabularyDesc, {target: {value: "TestB"}}
            );
            component.forceUpdate(function () {
              assert.equal(component.state.description, "TestB");
              React.addons.TestUtils.Simulate.change(
                checkboxCourse,
                {target: {value: 'course', checked: true}}
              );
              assert.equal(refreshCount, 0);
              component.forceUpdate(function () {
                React.addons.TestUtils.Simulate.click(saveButton);
                component.forceUpdate(function () {
                  waitForAjax(1, function () {
                    // Error is caused by a 400 status code
                    assert.equal(refreshCount, 0);
                    assert.deepEqual(
                      vocabMessage,
                      {error: "There was a problem adding the Vocabulary."}
                    );
                    done();
                  });
                });
              });
            });
          });
        };
        React.addons.TestUtils.
          renderIntoDocument(
          <AddVocabulary
            editVocabulary={editVocabulary}
            repoSlug="repo2"
            learningResourceTypes={propLearningResourceTypes}
            updateParent={updateParent}
            refreshFromAPI={refreshFromAPI}
            reportMessage={reportMessage}
            setLoadedState={function() {}}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that ajax fail in AddVocabulary: Duplicate Vocabulary',
      function (assert) {
        assert.ok(AddVocabulary, "class object not found");
        var done = assert.async();
        var updateParent = function () {
        };
        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };
        var editVocabulary = function () {
        };
        var duplicateVocabularyResponse = {
          "non_field_errors": [
            "The fields repository, name must make a unique set."
          ]
        };

        var vocabMessage;
        var reportMessage = function (message) {
          vocabMessage = message;
        };

        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo3/vocabularies/",
          contentType: "application/json; charset=utf-8",
          responseText: duplicateVocabularyResponse,
          dataType: 'json',
          type: "POST",
          status: 400
        });
        var afterMount = function (component) {
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
          var buttonNodes = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
            formNode,
            'button'
          );
          var saveButton = buttonNodes[0];
          assert.equal(inputNodes.length, 13);
          var inputVocabularyName = inputNodes[0];
          var inputVocabularyDesc = inputNodes[1];
          var checkboxCourse = inputNodes[2];

          React.addons.TestUtils.Simulate.change(
            inputVocabularyName, {target: {value: "TestB"}}
          );
          component.forceUpdate(function () {
            assert.equal(component.state.name, "TestB");
            React.addons.TestUtils.Simulate.change(
              inputVocabularyDesc, {target: {value: "TestB"}}
            );
            component.forceUpdate(function () {
              assert.equal(component.state.description, "TestB");
              React.addons.TestUtils.Simulate.change(
                checkboxCourse,
                {target: {value: 'course', checked: true}}
              );
              component.forceUpdate(function () {
                React.addons.TestUtils.Simulate.click(saveButton);
                component.forceUpdate(function () {
                  waitForAjax(1, function () {
                    // Error is caused by a 400 status code
                    assert.deepEqual(
                      vocabMessage,
                      {
                        error: 'A Vocabulary named "TestB" already exists.' +
                        ' Please choose a different name.'
                      }
                    );
                    done();
                  });
                });
              });
            });
          });
        };
        React.addons.TestUtils.
          renderIntoDocument(
          <AddVocabulary
            editVocabulary={editVocabulary}
            repoSlug="repo3"
            learningResourceTypes={propLearningResourceTypes}
            refreshFromAPI={refreshFromAPI}
            updateParent={updateParent}
            reportMessage={reportMessage}
            setLoadedState={function() {}}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that update vocabulary works',
      function (assert) {
        assert.ok(AddVocabulary, "class object not found");
        var done = assert.async();
        var vocabularyUpdateResponse = {
          "id": 1,
          "slug": "difficulty",
          "name": "TestB",
          "description": "TestB",
          "vocabulary_type": "f",
          "required": false,
          "weight": 2147483647,
          "learning_resource_types": [
            "course", "chapter"
          ],
          "multi_terms": true,
        };

        var vocabMessage;
        var reportMessage = function (message) {
          vocabMessage = message;
        };

        var confirm;
        var renderConfirmationDialog = function (options) {
          confirm = function (success) {
            options.confirmationHandler(success);
          };
        };

        var refreshFromAPI = function () {
        };
        var editVocabulary = function () {
        };
        var updateParent = function (vocab) {
          assert.equal(vocabulary.id, vocab.id);
          assert.notEqual(vocabulary.name, vocab.name);
          assert.notEqual(vocabulary.description, vocab.description);
          assert.notEqual(
            vocabulary.learning_resource_types.length,
            vocab.learning_resource_types.length
          );
        };

        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo4/vocabularies/" +
          vocabulary.slug + "/",
          contentType: "application/json; charset=utf-8",
          responseText: vocabularyUpdateResponse,
          dataType: 'json',
          type: "PATCH"
        });
        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo4/learning_resources/" +
          "?vocab_slug=difficulty&type_name=course",
          contentType: "application/json; charset=utf-8",
          // This is mostly unused, we are just checking the count
          responseText: {"count": 1},
          dataType: 'json',
          type: "GET"
        });

        var afterMount = function (component) {
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
          var buttonNodes = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
            formNode,
            'button'
          );
          var updateButton = buttonNodes[0];
          var inputVocabularyName = inputNodes[0];
          var inputVocabularyDesc = inputNodes[1];
          var checkboxCourse = inputNodes[2];

          React.addons.TestUtils.Simulate.change(
            inputVocabularyName, {target: {value: "TestB"}}
          );
          component.forceUpdate(function () {
            assert.equal(component.state.name, "TestB");
            React.addons.TestUtils.Simulate.change(
              inputVocabularyDesc, {target: {value: "TestB"}}
            );
            component.forceUpdate(function () {
              assert.equal(component.state.description, "TestB");
              React.addons.TestUtils.Simulate.change(
                checkboxCourse,
                {target: {value: 'course', checked: false}}
              );
              component.forceUpdate(function () {
                React.addons.TestUtils.Simulate.click(updateButton);
                component.forceUpdate(function () {
                  waitForAjax(1, function () {
                    assert.deepEqual(component.state, {
                      name: 'TestB',
                      description: 'TestB',
                      vocabularyType: 'f',
                      learningResourceTypes: [],
                      multiTerms: true
                    });

                    // Press confirm in dialog.
                    confirm(true);
                    waitForAjax(1, function () {
                      //testing state is reset
                      assert.deepEqual(component.state, {
                        name: '',
                        description: '',
                        vocabularyType: 'm',
                        learningResourceTypes: [],
                        multiTerms: false
                      });
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
          <AddVocabulary
            refreshFromAPI={refreshFromAPI}
            editVocabulary={editVocabulary}
            vocabularyInEdit={vocabulary}
            repoSlug="repo4"
            learningResourceTypes={propLearningResourceTypes}
            updateParent={updateParent}
            reportMessage={reportMessage}
            renderConfirmationDialog={renderConfirmationDialog}
            setLoadedState={function() {}}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that if user cancels update vocabulary dialog,' +
      ' no change is made',
      function (assert) {
        assert.ok(AddVocabulary, "class object not found");
        var done = assert.async();

        var vocabMessage;
        var reportMessage = function (message) {
          vocabMessage = message;
        };

        var confirm;
        var renderConfirmationDialog = function (options) {
          confirm = function (success) {
            options.confirmationHandler(success);
          };
        };

        var refreshFromAPI = function () {
        };
        var editVocabulary = function () {
        };
        var updateParent = function (vocab) {
          assert.equal(vocabulary.id, vocab.id);
          assert.notEqual(vocabulary.name, vocab.name);
          assert.notEqual(vocabulary.description, vocab.description);
          assert.notEqual(
            vocabulary.learning_resource_types.length,
            vocab.learning_resource_types.length
          );
        };

        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo4/learning_resources/" +
          "?vocab_slug=difficulty&type_name=course",
          contentType: "application/json; charset=utf-8",
          // This is mostly unused, we are just checking the count
          responseText: {"count": 1},
          dataType: 'json',
          type: "GET"
        });

        var afterMount = function (component) {
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
          var buttonNodes = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
            formNode,
            'button'
          );
          var updateButton = buttonNodes[0];
          var inputVocabularyName = inputNodes[0];
          var inputVocabularyDesc = inputNodes[1];
          var checkboxCourse = inputNodes[2];

          React.addons.TestUtils.Simulate.change(
            inputVocabularyName, {target: {value: "TestB"}}
          );
          component.forceUpdate(function () {
            assert.equal(component.state.name, "TestB");
            React.addons.TestUtils.Simulate.change(
              inputVocabularyDesc, {target: {value: "TestB"}}
            );
            component.forceUpdate(function () {
              assert.equal(component.state.description, "TestB");
              React.addons.TestUtils.Simulate.change(
                checkboxCourse,
                {target: {value: 'course', checked: false}}
              );
              component.forceUpdate(function () {
                React.addons.TestUtils.Simulate.click(updateButton);
                // Check that loader turns on and off.
                component.forceUpdate(function () {
                  waitForAjax(1, function () {
                    var expected = {
                      name: 'TestB',
                      description: 'TestB',
                      vocabularyType: 'f',
                      learningResourceTypes: [],
                      multiTerms: true
                    };
                    assert.deepEqual(component.state, expected);

                    // Press cancel in dialog.
                    confirm(false);
                    component.forceUpdate(function () {
                      //testing state has not changed
                      assert.deepEqual(component.state, expected);
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
          <AddVocabulary
            refreshFromAPI={refreshFromAPI}
            editVocabulary={editVocabulary}
            vocabularyInEdit={vocabulary}
            repoSlug="repo4"
            learningResourceTypes={propLearningResourceTypes}
            updateParent={updateParent}
            reportMessage={reportMessage}
            renderConfirmationDialog={renderConfirmationDialog}
            setLoadedState={function() {}}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that failure to get resource information during update' +
      ' is reported as an error',
      function (assert) {
        assert.ok(AddVocabulary, "class object not found");
        var done = assert.async();

        var vocabMessage;
        var reportMessage = function (message) {
          vocabMessage = message;
        };

        var confirm;
        var renderConfirmationDialog = function (options) {
          confirm = function (success) {
            options.confirmationHandler(success);
          };
        };

        var refreshFromAPI = function () {
        };
        var editVocabulary = function () {
        };
        var updateParent = function (vocab) {
          assert.equal(vocabulary.id, vocab.id);
          assert.notEqual(vocabulary.name, vocab.name);
          assert.notEqual(vocabulary.description, vocab.description);
          assert.notEqual(
            vocabulary.learning_resource_types.length,
            vocab.learning_resource_types.length
          );
        };

        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo4/learning_resources/" +
          "?vocab_slug=difficulty&type_name=course",
          contentType: "application/json; charset=utf-8",
          status: 400,
          dataType: 'json',
          type: "GET"
        });

        var afterMount = function (component) {
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
          var buttonNodes = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
            formNode,
            'button'
          );
          var updateButton = buttonNodes[0];
          var inputVocabularyName = inputNodes[0];
          var inputVocabularyDesc = inputNodes[1];
          var checkboxCourse = inputNodes[2];

          React.addons.TestUtils.Simulate.change(
            inputVocabularyName, {target: {value: "TestB"}}
          );
          component.forceUpdate(function () {
            assert.equal(component.state.name, "TestB");
            React.addons.TestUtils.Simulate.change(
              inputVocabularyDesc, {target: {value: "TestB"}}
            );
            component.forceUpdate(function () {
              assert.equal(component.state.description, "TestB");
              React.addons.TestUtils.Simulate.change(
                checkboxCourse,
                {target: {value: 'course', checked: false}}
              );
              component.forceUpdate(function () {
                React.addons.TestUtils.Simulate.click(updateButton);
                component.forceUpdate(function () {
                  waitForAjax(1, function () {
                    assert.deepEqual(component.state, {
                      name: 'TestB',
                      description: 'TestB',
                      vocabularyType: 'f',
                      learningResourceTypes: [],
                      multiTerms: true
                    });

                    assert.deepEqual(
                      vocabMessage, {
                        error: 'There was a problem with updating' +
                          ' the Vocabulary.'
                      }
                    );
                    done();
                  });
                });
              });
            });
          });
        };
        React.addons.TestUtils.
          renderIntoDocument(
          <AddVocabulary
            refreshFromAPI={refreshFromAPI}
            editVocabulary={editVocabulary}
            vocabularyInEdit={vocabulary}
            repoSlug="repo4"
            learningResourceTypes={propLearningResourceTypes}
            updateParent={updateParent}
            reportMessage={reportMessage}
            renderConfirmationDialog={renderConfirmationDialog}
            setLoadedState={function() {}}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that update vocabulary fail with name ' +
      'or description blank',
      function (assert) {
        assert.ok(AddVocabulary, "class object not found");
        var refreshFromAPI = function () {
        };
        var editVocabulary = function () {
        };
        var updateParent = function () {
        };

        var vocabMessage;
        var reportMessage = function (message) {
          vocabMessage = message;
        };

        var afterMount = function (component) {
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
          var buttonNodes = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
            formNode,
            'button'
          );
          var updateButton = buttonNodes[0];
          var inputVocabularyName = inputNodes[0];
          var inputVocabularyDesc = inputNodes[1];

          React.addons.TestUtils.Simulate.change(
            inputVocabularyName, {target: {value: ""}}
          );
          component.forceUpdate(function () {
            assert.equal(component.state.name, "");
            React.addons.TestUtils.Simulate.change(
              inputVocabularyDesc, {target: {value: "TestB"}}
            );
            component.forceUpdate(function () {
              assert.equal(component.state.description, "TestB");
              React.addons.TestUtils.Simulate.click(updateButton);
              component.forceUpdate(function () {
                assert.deepEqual(
                  vocabMessage,
                  {error: 'Please enter vocabulary name.'}
                );
                React.addons.TestUtils.Simulate.change(
                  inputVocabularyName, {target: {value: "Name of colours"}}
                );
                component.forceUpdate(function () {
                  assert.equal(component.state.name, "Name of colours");
                  React.addons.TestUtils.Simulate.change(
                    inputVocabularyDesc, {target: {value: ""}}
                  );
                  component.forceUpdate(function () {
                    assert.equal(component.state.description, "");
                    React.addons.TestUtils.Simulate.click(updateButton);
                    component.forceUpdate(function () {
                      assert.deepEqual(
                        vocabMessage,
                        {error: 'Please enter vocabulary description.'}
                      );
                    });
                  });
                });
              });
            });
          });
        };
        React.addons.TestUtils.
          renderIntoDocument(
          <AddVocabulary
            editVocabulary={editVocabulary}
            vocabularyInEdit={vocabulary}
            repoSlug="repo"
            learningResourceTypes={propLearningResourceTypes}
            refreshFromAPI={refreshFromAPI}
            updateParent={updateParent}
            reportMessage={reportMessage}
            setLoadedState={function() {}}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that ajax call fail in update vocabulary',
      function (assert) {
        assert.ok(AddVocabulary, "class object not found");
        var done = assert.async();
        var editVocabulary = function () {
        };
        var updateParent = function () {
        };
        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };
        var vocabMessage;
        var reportMessage = function (message) {
          vocabMessage = message;
        };

        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo' +
          '/vocabularies/' + vocabulary.slug + "/",
          type: "PATCH",
          status: 400
        });

        var afterMount = function (component) {
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
          var buttonNodes = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
            formNode,
            'button'
          );
          var updateButton = buttonNodes[0];
          var inputVocabularyName = inputNodes[0];
          var inputVocabularyDesc = inputNodes[1];
          var checkboxChapter = inputNodes[2];

          React.addons.TestUtils.Simulate.change(
            inputVocabularyName, {target: {value: "TestB"}}
          );
          component.forceUpdate(function () {
            assert.equal(component.state.name, "TestB");
            React.addons.TestUtils.Simulate.change(
              inputVocabularyDesc, {target: {value: "TestB"}}
            );
            assert.equal(refreshCount, 0);
            component.forceUpdate(function () {
              assert.equal(component.state.description, "TestB");
              React.addons.TestUtils.Simulate.change(
                checkboxChapter,
                {target: {value: 'chapter', checked: true}}
              );
              component.forceUpdate(function () {
                React.addons.TestUtils.Simulate.click(updateButton);
                component.forceUpdate(function () {
                  waitForAjax(1, function () {
                    // Error is caused by a 400 status code
                    assert.deepEqual(
                      vocabMessage,
                      {
                        error: "There was a problem with updating" +
                          " the Vocabulary."
                      }
                    );
                    done();
                  });
                });
              });
            });
          });
        };
        React.addons.TestUtils.
          renderIntoDocument(
          <AddVocabulary
            editVocabulary={editVocabulary}
            vocabularyInEdit={vocabulary}
            repoSlug="repo"
            learningResourceTypes={propLearningResourceTypes}
            updateParent={updateParent}
            refreshFromAPI={refreshFromAPI}
            reportMessage={reportMessage}
            setLoadedState={function() {}}
            ref={afterMount}
            />
        );
      }
    );

  }
);
