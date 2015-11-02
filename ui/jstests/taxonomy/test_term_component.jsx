define(['QUnit', 'jquery', 'lodash', 'manage_taxonomies', 'react',
    'test_utils'],
  function (QUnit, $, _, ManageTaxonomies, React, TestUtils) {
    'use strict';

    var waitForAjax = TestUtils.waitForAjax;
    var TermComponent = ManageTaxonomies.TermComponent;

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

    QUnit.module('Test TermComponent', {
      beforeEach: function () {
        TestUtils.setup();
      },
      afterEach: function () {
        TestUtils.cleanup();
      }
    });

    QUnit.test('Assert that edit TermComponent renders properly',
      function (assert) {
        assert.ok(TermComponent, "class object not found");
        var done = assert.async();
        var term = {
          "id": 9,
          "slug": "test",
          "label": "test",
          "weight": 1
        };
        var parentUpdateCount = 0;
        var updateTerm = function () {
          parentUpdateCount += 1;
        };
        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo/vocabularies/difficulty/terms/test/",
          responseText: term,
          type: "PATCH"
        });

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

        var afterMount = function (component) {
          var labels = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
            component,
            'label'
          );

          //testing label value render
          var termLabel = labels[0];
          var label = termLabel.getDOMNode();
          assert.equal(label.innerHTML, term.label);
          assert.equal(component.state.formatActionState, 'show');

          var editButton = React.addons.TestUtils.
            findRenderedDOMComponentWithClass(
            component,
            'format-button'
          );

          //open edit mode
          React.addons.TestUtils.Simulate.click(editButton);
          component.forceUpdate(function () {
            assert.equal(component.state.formatActionState, 'edit');
            var saveButton = React.addons.TestUtils.
              findRenderedDOMComponentWithClass(
              component,
              'save-button'
            );
            var cancelButton = React.addons.TestUtils.
              findRenderedDOMComponentWithClass(
              component,
              'editable-cancel'
            );
            //edit term
            var editTermBox = React.addons.TestUtils.
              findRenderedDOMComponentWithTag(
              component,
              'input'
            );
            React.addons.TestUtils.Simulate.change(
              editTermBox, {target: {value: "TestB"}}
            );
            component.forceUpdate(function () {
              assert.equal(component.state.label, "TestB");
              //save term

              assert.equal(refreshCount, 0);
              React.addons.TestUtils.Simulate.click(saveButton);
              component.forceUpdate(function () {
                assert.equal(loadedState, false);
                //after saved term using api
                waitForAjax(1, function () {
                  assert.equal(loadedState, true);
                  //term state reset
                  assert.equal(component.state.formatActionState, 'show');
                  // term is update in parent
                  assert.equal(parentUpdateCount, 1);
                  // listing was asked to refresh
                  assert.equal(refreshCount, 1);

                  // Edit term again
                  React.addons.TestUtils.Simulate.click(editButton);
                  component.forceUpdate(function () {
                    saveButton = React.addons.TestUtils.
                      findRenderedDOMComponentWithClass(
                      component,
                      'save-button'
                    );
                    cancelButton = React.addons.TestUtils.
                      findRenderedDOMComponentWithClass(
                      component,
                      'editable-cancel'
                    );
                    assert.equal(component.state.formatActionState, 'edit');
                    editTermBox = React.addons.TestUtils.
                      findRenderedDOMComponentWithTag(
                      component,
                      'input'
                    );
                    React.addons.TestUtils.Simulate.change(
                      editTermBox, {target: {value: "TestB"}}
                    );
                    component.forceUpdate(function () {
                      // press cancel button and assert term layout is reset.
                      React.addons.TestUtils.Simulate.click(cancelButton);

                      component.forceUpdate(function () {
                        assert.equal(component.state.formatActionState, 'show');
                        //assert editbox is hide (UI reset)
                        var editTermBoxes = React.addons.TestUtils.
                          scryRenderedDOMComponentsWithTag(
                          component,
                          'input'
                        );

                        assert.equal(editTermBoxes.length, 0);

                        // Edit again term with same label
                        React.addons.TestUtils.Simulate.click(editButton);
                        component.forceUpdate(function () {
                          saveButton = React.addons.TestUtils.
                            findRenderedDOMComponentWithClass(
                            component,
                            'save-button'
                          );
                          cancelButton = React.addons.TestUtils.
                            findRenderedDOMComponentWithClass(
                            component,
                            'editable-cancel'
                          );
                          assert.equal(
                            component.state.formatActionState, 'edit');
                          editTermBox = React.addons.TestUtils.
                            findRenderedDOMComponentWithTag(
                            component,
                            'input'
                          );
                          React.addons.TestUtils.Simulate.change(
                            editTermBox, {target: {value: "test"}}
                          );

                          component.forceUpdate(function () {
                            // save term with label equals to previous label
                            React.addons.TestUtils.Simulate.click(saveButton);

                            component.forceUpdate(function () {
                              //assert editbox is hide (UI reset)
                              editTermBoxes = React.addons.TestUtils.
                                scryRenderedDOMComponentsWithTag(
                                component,
                                'input'
                              );
                              assert.equal(editTermBoxes.length, 0);
                              React.addons.TestUtils.Simulate.click(editButton);
                              component.forceUpdate(function () {
                                saveButton = React.addons.TestUtils.
                                  findRenderedDOMComponentWithClass(
                                  component,
                                  'save-button'
                                );
                                editTermBox = React.addons.TestUtils.
                                  findRenderedDOMComponentWithTag(
                                  component,
                                  'input'
                                );
                                React.addons.TestUtils.Simulate.change(
                                  editTermBox, {target: {value: ""}}
                                );
                                component.forceUpdate(function () {
                                  assert.equal(
                                    component.state.errorMessage, '');
                                  React.addons.TestUtils.Simulate.click(
                                    saveButton
                                  );
                                  component.forceUpdate(function () {
                                    assert.equal(
                                      component.state.errorMessage,
                                      "Term cannot be empty."
                                    );
                                    done();
                                  });
                                });
                              });
                            });
                          });
                        });
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
          <TermComponent
            term={term}
            repoSlug="repo"
            updateTerm={updateTerm}
            vocabulary={vocabulary}
            refreshFromAPI={refreshFromAPI}
            reportMessage={reportMessage}
            setLoadedState={setLoadedState}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that ajax fail on update term TermComponent',
      function (assert) {
        assert.ok(TermComponent, "class object not found");
        var done = assert.async();
        var term = {
          "id": 9,
          "slug": "test",
          "label": "test",
          "weight": 1
        };
        var parentUpdateCount = 0;
        var updateTerm = function () {
          parentUpdateCount += 1;
        };
        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo/vocabularies/difficulty/terms/test/",
          responseText: term,
          type: "PATCH",
          status: 400
        });

        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };

        var loadedState;
        var setLoadedState = function (loaded) {
          loadedState = loaded;
        };

        var afterMount = function (component) {
          var labels = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
            component,
            'label'
          );
          //testing label value render
          var termLabel = labels[0];
          var label = termLabel.getDOMNode();
          assert.equal(label.innerHTML, term.label);
          assert.equal(component.state.formatActionState, 'show');
          var editButton = React.addons.TestUtils.
            findRenderedDOMComponentWithClass(
            component,
            'format-button'
          );
          React.addons.TestUtils.Simulate.click(editButton);
          component.forceUpdate(function () {
            var saveButton = React.addons.TestUtils.
              findRenderedDOMComponentWithClass(
              component,
              'save-button'
            );
            var cancelButton = React.addons.TestUtils.
              findRenderedDOMComponentWithClass(
              component,
              'editable-cancel'
            );
            assert.equal(component.state.formatActionState, 'edit');
            var editTermBox = React.addons.TestUtils.
              findRenderedDOMComponentWithTag(
              component,
              'input'
            );
            React.addons.TestUtils.Simulate.change(
              editTermBox, {target: {value: ""}}
            );
            assert.equal(component.state.errorMessage, '');
            component.forceUpdate(function () {
              assert.equal(component.state.label, "");

              assert.equal(refreshCount, 0);
              React.addons.TestUtils.Simulate.click(saveButton);
              component.forceUpdate(function () {
                assert.equal(component.state.errorMessage,
                  'Term cannot be empty.');
                React.addons.TestUtils.Simulate.change(
                  editTermBox, {target: {value: "TestB"}}
                );
                component.forceUpdate(function () {
                  assert.equal(component.state.label, "TestB");
                  assert.equal(component.state.formatActionState, 'edit');
                  assert.equal(parentUpdateCount, 0);
                  // listing page was not asked to refresh
                  assert.equal(refreshCount, 0);
                  React.addons.TestUtils.Simulate.click(saveButton);
                  component.forceUpdate(function () {
                    // Loader is spinning...
                    assert.equal(loadedState, false);
                    waitForAjax(1, function () {
                      assert.equal(loadedState, true);
                      assert.equal(component.state.label, "TestB");
                      assert.equal(
                        component.state.errorMessage, 'Unable to update term'
                      );
                      assert.equal(component.state.formatActionState, 'edit');
                      assert.equal(parentUpdateCount, 0);
                      // listing page was not asked to refresh
                      assert.equal(refreshCount, 0);

                      editTermBox = React.addons.TestUtils.
                        findRenderedDOMComponentWithTag(
                        component,
                        'input'
                      );
                      React.addons.TestUtils.Simulate.change(
                        editTermBox, {target: {value: "TestB"}}
                      );
                      //after unable to save you can reset edit mode
                      component.forceUpdate(function () {
                        React.addons.TestUtils.Simulate.click(cancelButton);
                        component.forceUpdate(function () {
                          assert.equal(component.state.label, "TestB");
                          assert.equal(
                            component.state.formatActionState, 'show');
                          //assert editbox is hide (UI reset)
                          var editTermBoxes = React.addons.TestUtils.
                            scryRenderedDOMComponentsWithTag(
                            component,
                            'input'
                          );
                          assert.equal(editTermBoxes.length, 0);
                          done();
                        });
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
          <TermComponent
            term={term}
            repoSlug="repo"
            updateTerm={updateTerm}
            vocabulary={vocabulary}
            refreshFromAPI={refreshFromAPI}
            setLoadedState={setLoadedState}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that delete TermComponent renders properly',
      function (assert) {
        assert.ok(TermComponent, "class object not found");
        var done = assert.async();
        var term = {
          "id": 9,
          "slug": "test",
          "label": "test",
          "weight": 1
        };
        var parentUpdateCount = 0;
        var deleteTerm = function () {
          parentUpdateCount += 1;
        };
        var renderConfirmationDialog = function (options) {
          options.confirmationHandler(true);
        };

        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo/vocabularies/difficulty/terms/test/",
          type: "DELETE"
        });

        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };

        var loadedState;
        var setLoadedState = function (loaded) {
          loadedState = loaded;
        };

        var afterMount = function (component) {
          var deleteButton = React.addons.TestUtils.
            findRenderedDOMComponentWithClass(
            component,
            'revert-button'
          );
          //select delete
          React.addons.TestUtils.Simulate.click(deleteButton);
          component.forceUpdate(function () {
            assert.equal(loadedState, false);
            assert.equal(component.state.formatActionState, 'show');
            waitForAjax(1, function () {
              assert.equal(loadedState, true);
              // term is delete in parent
              assert.equal(parentUpdateCount, 1);
              // listing was asked to refresh
              assert.equal(refreshCount, 1);
              done();
            });
          });
        };

        React.addons.TestUtils.
          renderIntoDocument(
          <TermComponent
            term={term}
            repoSlug="repo"
            renderConfirmationDialog={renderConfirmationDialog}
            deleteTerm={deleteTerm}
            vocabulary={vocabulary}
            refreshFromAPI={refreshFromAPI}
            setLoadedState={setLoadedState}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert that delete ajax call fail TermComponent' +
      ' renders properly',
      function (assert) {
        assert.ok(TermComponent, "class object not found");
        var done = assert.async();
        var term = {
          "id": 9,
          "slug": "test",
          "label": "test",
          "weight": 1
        };
        var parentUpdateCount = 0;
        var deleteTerm = function () {
          parentUpdateCount += 1;
        };
        var renderConfirmationDialog = function (options) {
          options.confirmationHandler(true);
        };

        TestUtils.initMockjax({
          url: "/api/v1/repositories/repo/vocabularies/difficulty/terms/test/",
          type: "DELETE",
          status: 400
        });

        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };

        var loadedState;
        var setLoadedState = function (loaded) {
          loadedState = loaded;
        };

        var afterMount = function (component) {
          var deleteButton = React.addons.TestUtils.
            findRenderedDOMComponentWithClass(
            component,
            'revert-button'
          );
          //select delete
          React.addons.TestUtils.Simulate.click(deleteButton);
          component.forceUpdate(function () {
            assert.equal(
              component.state.errorMessage, ''
            );
            assert.equal(component.state.formatActionState, 'show');
            assert.equal(loadedState, false);
            waitForAjax(1, function () {
              assert.equal(loadedState, true);
              // check state of error message
              assert.equal(
                component.state.errorMessage, 'Unable to delete term.'
              );
              done();
            });
          });
        };

        React.addons.TestUtils.
          renderIntoDocument(
          <TermComponent
            term={term}
            repoSlug="repo"
            renderConfirmationDialog={renderConfirmationDialog}
            deleteTerm={deleteTerm}
            vocabulary={vocabulary}
            refreshFromAPI={refreshFromAPI}
            setLoadedState={setLoadedState}
            ref={afterMount}
            />
        );
      }
    );
  }
);
