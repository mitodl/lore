define(['QUnit', 'jquery', 'manage_taxonomies', 'react',
  'test_utils', 'utils'],
  function(QUnit, $, ManageTaxonomies, React, TestUtils, Utils) {
  'use strict';

  var VocabularyComponent = ManageTaxonomies.VocabularyComponent;
  var waitForAjax = TestUtils.waitForAjax;
  var TermComponent = ManageTaxonomies.TermComponent;
  var AddTermsComponent = ManageTaxonomies.AddTermsComponent;
  var AddVocabulary = ManageTaxonomies.AddVocabulary;
  var TaxonomyComponent = ManageTaxonomies.TaxonomyComponent;
  var showConfirmationDialog = Utils.showConfirmationDialog;
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
  var learningResourceTypes = {
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
  function  assertAddTermCommon(assert, component) {
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

  QUnit.module('Test taxonomies panel', {
    beforeEach: function() {
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
        responseText: learningResourceTypes,
        dataType: 'json',
        type: "GET"
      });
      TestUtils.initMockjax({
        url: "/api/v1/repositories/repo/vocabularies/difficulty/",
        type: "DELETE"
      });
    },
    afterEach: function() {
      TestUtils.cleanup();
    }
  });

  QUnit.test('Assert that TermComponent renders properly',
    function(assert) {
      assert.ok(TermComponent, "class object not found");
      var done = assert.async();
      var term = {
        "id": 9,
        "slug": "test",
        "label": "test",
        "weight": 1
      };
      var parentUpdateCount = 0;
      var updateTerm = function() {
        parentUpdateCount += 1;
      };
      TestUtils.initMockjax({
        url: "/api/v1/repositories/repo/vocabularies/difficulty/terms/test/",
        responseText: term,
        type: "PATCH"
      });

      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };

      var afterMount = function(component) {
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
        component.forceUpdate(function() {
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
          component.forceUpdate(function() {
            assert.equal(component.state.label, "TestB");
            //save term

            assert.equal(refreshCount, 0);
            React.addons.TestUtils.Simulate.click(saveButton);
            component.forceUpdate(function() {
              //after saved term using api
              waitForAjax(1, function() {
                //term state reset
                assert.equal(component.state.formatActionState, 'show');
                // term is update in parent
                assert.equal(parentUpdateCount, 1);
                // listing was asked to refresh
                assert.equal(refreshCount, 1);

                // Edit term again
                React.addons.TestUtils.Simulate.click(editButton);
                component.forceUpdate(function() {
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
                      component.forceUpdate(function() {
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
                          editTermBox, {target: {value: "test"}}
                        );

                        component.forceUpdate(function() {
                          // save term with label equals to previous label
                          React.addons.TestUtils.Simulate.click(saveButton);

                          component.forceUpdate(function() {
                            //assert editbox is hide (UI reset)
                            editTermBoxes = React.addons.TestUtils.
                              scryRenderedDOMComponentsWithTag(
                              component,
                              'input'
                            );
                            assert.equal(editTermBoxes.length, 0);
                            React.addons.TestUtils.Simulate.click(editButton);
                            component.forceUpdate(function() {
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
                              component.forceUpdate(function() {
                                assert.equal(component.state.showError, false);
                                React.addons.TestUtils.Simulate.click(
                                  saveButton
                                );
                                component.forceUpdate(function() {
                                  assert.equal(
                                    component.state.showError, true
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
            vocabularySlug={vocabulary.slug}
            refreshFromAPI={refreshFromAPI}
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that ajax fail on update term TermComponent',
    function(assert) {
      assert.ok(TermComponent, "class object not found");
      var done = assert.async();
      var term = {
        "id": 9,
        "slug": "test",
        "label": "test",
        "weight": 1
      };
      var parentUpdateCount = 0;
      var updateTerm = function() {
        parentUpdateCount += 1;
      };
      TestUtils.initMockjax({
        url: "/api/v1/repositories/repo/vocabularies/difficulty/terms/test/",
        responseText: term,
        type: "PATCH",
        status: 400
      });

      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };

      var afterMount = function(component) {
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
        component.forceUpdate(function() {
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
          assert.equal(component.state.showError, false);
          component.forceUpdate(function() {
            assert.equal(component.state.label, "");

            assert.equal(refreshCount, 0);
            React.addons.TestUtils.Simulate.click(saveButton);
            component.forceUpdate(function () {
              assert.equal(component.state.showError, true);
              React.addons.TestUtils.Simulate.change(
                editTermBox, {target: {value: "TestB"}}
              );
              component.forceUpdate(function() {
                assert.equal(component.state.label, "TestB");

                assert.equal(refreshCount, 0);
                React.addons.TestUtils.Simulate.click(saveButton);
                component.forceUpdate(function() {
                  waitForAjax(1, function() {
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
                        assert.equal(component.state.label, "test");
                        assert.equal(component.state.formatActionState, 'show');
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
            vocabularySlug={vocabulary.slug}
            refreshFromAPI={refreshFromAPI}
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that VocabularyComponent renders properly',
    function(assert) {
      assert.ok(VocabularyComponent, "class object not found");
      var done = assert.async();

      var showConfirmationDialog = function (options) {
        options.confirmationHandler(true);
      };

      var addTermCalled = 0;
      var deleteVocabularyCalled = 0;
      var editVocabularyButton;
      var editVocabularyCalled = 0;

      var addTerm = function() {
        addTermCalled += 1;
      };
      var deleteVocabulary = function() {
        deleteVocabularyCalled += 1;
      };

      var editVocabulary = function() {
        editVocabularyCalled += 1;
      };

      var reportMessage = function() {};

      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };
      var afterMount = function(component) {
        var node = React.findDOMNode(component);

        // check vocab title
        var $vocabLinks = $(node).find(".vocab-title");
        assert.equal($vocabLinks.length, 1);
        assert.equal($vocabLinks[0].innerHTML, vocabulary.name);

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
                  waitForAjax(1, function () {
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
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that ajax fail VocabularyComponent',
    function(assert) {
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
      var addTerm = function() {
        addTermCalled += 1;
      };
      var reportMessage = function(msg) {
        message = msg;
      };

      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };

      var afterMount = function(component) {
        // wait for calls to populate form
        var node = React.findDOMNode(component);
        var textbox = $(node).find("input")[0];
        React.addons.TestUtils.Simulate.keyUp(textbox, {key: "Enter"});
        waitForAjax(1, function () {
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
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that AddTermsComponent work properly',
    function(assert) {
      assert.ok(AddTermsComponent, "class object not found");
      var vocabularies = [
        {
          "vocabulary": vocabulary,
          "terms": vocabulary.terms
        }
      ];
      var done = assert.async();
      var addTermCalled = 0;
      var addTerm = function() {
        addTermCalled += 1;
      };

      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };

      var editVocabulary = function() {};
      var afterMount = function(component) {
        assert.equal(
          component.state.message,
          undefined
        );
        assertAddTermCommon(assert, component);
        //test error message
        component.reportMessage({
          error: "Error occurred while adding new term."
        });
        component.forceUpdate(function() {
          assert.deepEqual(
            component.state.message,
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
          waitForAjax(1, function() {
            //test items
            assert.equal(addTermCalled, 1);
            // listing page was asked to update
            assert.equal(refreshCount, 1);
            done();
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
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that AddVocabulary work properly',
    function(assert) {
      assert.ok(AddVocabulary, "class object not found");
      var learningResourceTypes = ['course', 'chapter', 'sequential',
        'vertical', 'html', 'video', 'discussion', 'problem'];
      var saveVocabularyResponse;
      var done = assert.async();
      var editVocabulary = function() {};
      var updateParent = function(data) {
        saveVocabularyResponse = data;
      };

      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };
      var closeTaxonomyPanel = function() {};
      var removePanelVisibility = false;
      var afterMount = function(component) {
        assert.equal(
          component.state.name,
          ''
        );
        assert.equal(
          component.state.description,
          ''
        );
        assert.equal(
          component.state.vocabularyType,
          'm'
        );
        assert.equal(
          component.state.learningResourceTypes.length,
          0
        );
        assert.equal(
          component.state.multiTerms,
          false
        );
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
        var inputVocabularyDesc =  inputNodes[1];
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
        component.forceUpdate(function() {
          assert.equal(component.state.name, "TestA");
          assert.equal(component.state.vocabularyType, "f");
          assert.equal(component.state.description, "TestA");
          assert.equal(
            component.state.learningResourceTypes.length,
            0
          );
          //the change to the multi terms is reflected in the state
          assert.equal(component.state.multiTerms, true);
          React.addons.TestUtils.Simulate.click(saveButton);
          waitForAjax(1, function() {
            assert.equal(
              saveVocabularyResponse.id,
              vocabulary.id
            );
            //testing state is reset
            assert.equal(
              component.state.name,
              ''
            );
            assert.equal(
              component.state.description,
              ''
            );
            assert.equal(
              component.state.vocabularyType,
              'm'
            );
            assert.equal(
              component.state.learningResourceTypes.length,
              0
            );
            assert.equal(
              component.state.multiTerms,
              false
            );
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
            var inputVocabularyDesc =  inputNodes[1];
            var checkboxCourse =  inputNodes[2];
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
            component.forceUpdate(function() {
              assert.equal(component.state.name, "TestB");
              assert.equal(component.state.description, "TestB");
              assert.equal(component.state.vocabularyType, "f");
              assert.equal(
                component.state.learningResourceTypes[0],
                'course'
              );
              assert.equal(component.state.multiTerms, true);
              React.addons.TestUtils.Simulate.click(saveButton);
              waitForAjax(1, function() {
                //testing state is reset
                assert.equal(
                  component.state.name,
                  ''
                );
                assert.equal(
                  component.state.description,
                  ''
                );
                assert.equal(
                  component.state.vocabularyType,
                  'm'
                );
                assert.equal(
                  component.state.learningResourceTypes.length,
                  0
                );
                assert.equal(
                  component.state.multiTerms,
                  false
                );
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

                component.forceUpdate(function() {
                  assert.equal(component.state.name, "TestC");
                  assert.equal(component.state.description, "TestC");
                  assert.equal(component.state.vocabularyType, "f");
                  assert.equal(
                    component.state.learningResourceTypes[0],
                    'course'
                  );
                  assert.equal(component.state.multiTerms, true);
                  //uncheck checkboxes
                  React.addons.TestUtils.Simulate.change(
                    checkboxCourse,
                    {target: {value: 'course', checked: false}}
                  );
                  React.addons.TestUtils.Simulate.change(
                    checkMultiTerms,
                    {target: {checked: false}}
                  );
                  component.forceUpdate(function() {
                    assert.equal(component.state.name, "TestC");
                    assert.equal(component.state.description, "TestC");
                    assert.equal(component.state.vocabularyType, "f");
                    //assert after uncheck course, learningResourceTypes is empty
                    assert.equal(
                      component.state.learningResourceTypes.length,
                      0
                    );
                    //and the multi terms state is consistent
                    assert.equal(component.state.multiTerms, false);
                    React.addons.TestUtils.Simulate.click(saveButton);
                    waitForAjax(1, function() {
                      assert.equal(refreshCount, 3);
                      //testing state is reset
                      assert.equal(
                        component.state.name,
                        ''
                      );
                      assert.equal(
                        component.state.description,
                        ''
                      );
                      assert.equal(
                        component.state.vocabularyType,
                        'm'
                      );
                      assert.equal(
                        component.state.learningResourceTypes.length,
                        0
                      );
                      assert.equal(component.state.multiTerms, false);
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
            closeTaxonomyPanel={closeTaxonomyPanel}
            removePanelVisibility={removePanelVisibility}
            updateParent={updateParent}
            learningResourceTypes={learningResourceTypes}
            refreshFromAPI={refreshFromAPI}
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that ajax fail in AddVocabulary',
    function(assert) {
      assert.ok(AddVocabulary, "class object not found");
      var done = assert.async();
      var editVocabulary = function() {};
      var closeTaxonomyPanel = function() {};
      var updateParent = function() {};
      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };
      var removePanelVisibility = false;
      TestUtils.initMockjax({
        url: "/api/v1/repositories/repo2/vocabularies/",
        type: "POST",
        status: 400
      });
      var afterMount = function(component) {
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
        assert.equal(inputNodes.length, 8);
        var inputVocabularyName = inputNodes[0];
        var inputVocabularyDesc =  inputNodes[1];
        var checkboxCourse =  inputNodes[2];

        React.addons.TestUtils.Simulate.change(
          inputVocabularyName, {target: {value: "TestB"}}
        );
        component.forceUpdate(function() {
          assert.equal(component.state.name, "TestB");
          React.addons.TestUtils.Simulate.change(
            inputVocabularyDesc, {target: {value: "TestB"}}
          );
          component.forceUpdate(function() {
            assert.equal(component.state.description, "TestB");
            React.addons.TestUtils.Simulate.change(
              checkboxCourse,
              {target: {value: 'course', checked: true}}
            );
            assert.equal(refreshCount, 0);
            component.forceUpdate(function() {
              React.addons.TestUtils.Simulate.click(saveButton);
              component.forceUpdate(function() {
                waitForAjax(1, function() {
                  // Error is caused by a 400 status code
                  assert.equal(refreshCount, 0);
                  assert.deepEqual(
                    component.state.message,
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
            closeTaxonomyPanel={closeTaxonomyPanel}
            removePanelVisibility={removePanelVisibility}
            repoSlug="repo2"
            learningResourceTypes={learningResourceTypes}
            updateParent={updateParent}
            refreshFromAPI={refreshFromAPI}
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that ajax fail in AddVocabulary: Duplicate Vocabulary',
    function(assert) {
      assert.ok(AddVocabulary, "class object not found");
      var done = assert.async();
      var updateParent = function() {};
      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };
      var editVocabulary = function() {};
      var closeTaxonomyPanel = function() {};
      var removePanelVisibility = false;
      var duplicateVocabularyResponse = {
        "non_field_errors":[
          "The fields repository, name must make a unique set."
        ]
      };

      TestUtils.initMockjax({
        url: "/api/v1/repositories/repo3/vocabularies/",
        contentType: "application/json; charset=utf-8",
        responseText: duplicateVocabularyResponse,
        dataType: 'json',
        type: "POST",
        status: 400
      });
      var afterMount = function(component) {
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
        assert.equal(inputNodes.length, 8);
        var inputVocabularyName = inputNodes[0];
        var inputVocabularyDesc =  inputNodes[1];
        var checkboxCourse =  inputNodes[2];

        React.addons.TestUtils.Simulate.change(
          inputVocabularyName, {target: {value: "TestB"}}
        );
        component.forceUpdate(function() {
          assert.equal(component.state.name, "TestB");
          React.addons.TestUtils.Simulate.change(
            inputVocabularyDesc, {target: {value: "TestB"}}
          );
          component.forceUpdate(function() {
            assert.equal(component.state.description, "TestB");
            React.addons.TestUtils.Simulate.change(
              checkboxCourse,
              {target: {value: 'course', checked: true}}
            );
            component.forceUpdate(function() {
              React.addons.TestUtils.Simulate.click(saveButton);
              component.forceUpdate(function() {
                waitForAjax(1, function() {
                  // Error is caused by a 400 status code
                  assert.deepEqual(
                    component.state.message,
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
            closeTaxonomyPanel={closeTaxonomyPanel}
            removePanelVisibility={removePanelVisibility}
            learningResourceTypes={learningResourceTypes}
            refreshFromAPI={refreshFromAPI}
            updateParent={updateParent}
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that update vocabulary works',
    function(assert) {
      assert.ok(AddVocabulary, "class object not found");
      var done = assert.async();
      var removePanelVisibility = false;
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

      var refreshFromAPI = function() {};
      var editVocabulary = function() {};
      var closeTaxonomyPanel = function() {};
      var updateParent = function(vocab) {
        assert.equal(vocabulary.id, vocab.id);
        assert.notEqual(vocabulary.name, vocab.name);
        assert.notEqual(vocabulary.description, vocab.description);
        assert.notEqual(
          vocabulary.learning_resource_types.length,
          vocab.learning_resource_types.length
        );
      };

      //update vocabulary
      TestUtils.initMockjax({
        url: "/api/v1/repositories/repo4/vocabularies/" +
          vocabulary.slug + "/",
        contentType: "application/json; charset=utf-8",
        responseText: vocabularyUpdateResponse,
        dataType: 'json',
        type: "PATCH"
      });

      var afterMount = function(component) {
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
        var inputVocabularyDesc =  inputNodes[1];
        var checkboxCourse =  inputNodes[2];

        React.addons.TestUtils.Simulate.change(
          inputVocabularyName, {target: {value: "TestB"}}
        );
        component.forceUpdate(function() {
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
              React.addons.TestUtils.Simulate.click(updateButton);
              component.forceUpdate(function() {
                waitForAjax(1, function() {
                  //testing state is reset
                  assert.equal(
                    component.state.name,
                    ''
                  );
                  assert.equal(
                    component.state.description,
                    ''
                  );
                  assert.equal(
                    component.state.vocabularyType,
                    'm'
                  );
                  assert.equal(
                    component.state.learningResourceTypes.length,
                    0
                  );
                  assert.equal(component.state.multiTerms, false);
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
            vocabulary={vocabulary}
            closeTaxonomyPanel={closeTaxonomyPanel}
            removePanelVisibility={removePanelVisibility}
            repoSlug="repo4"
            learningResourceTypes={learningResourceTypes}
            updateParent={updateParent}
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that update vocabulary fail with name ' +
    'or description blank',
    function(assert) {
      assert.ok(AddVocabulary, "class object not found");
      var removePanelVisibility = false;
      var refreshFromAPI = function() {};
      var closeTaxonomyPanel = function () {
      };
      var editVocabulary = function () {
      };
      var updateParent = function () {
      };
      var afterMount = function(component) {
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
        component.forceUpdate(function() {
          assert.equal(component.state.name, "");
          React.addons.TestUtils.Simulate.change(
            inputVocabularyDesc, {target: {value: "TestB"}}
          );
          component.forceUpdate(function () {
            assert.equal(component.state.description, "TestB");
            React.addons.TestUtils.Simulate.click(updateButton);
            component.forceUpdate(function () {
              assert.deepEqual(
                component.state.message,
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
                      component.state.message,
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
            vocabulary={vocabulary}
            closeTaxonomyPanel={closeTaxonomyPanel}
            removePanelVisibility={removePanelVisibility}
            repoSlug="repo"
            learningResourceTypes={learningResourceTypes}
            refreshFromAPI={refreshFromAPI}
            updateParent={updateParent}
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that ajax call fail in update vocabulary',
    function(assert) {
      assert.ok(AddVocabulary, "class object not found");
      var done = assert.async();
      var closeTaxonomyPanel = function() {};
      var editVocabulary = function() {};
      var updateParent = function() {};
      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };

      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo' +
        '/vocabularies/' + vocabulary.slug + "/",
        type: "PATCH",
        status: 400
      });

      var removePanelVisibility = false;
      var afterMount = function(component) {
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
        var inputVocabularyDesc =  inputNodes[1];
        var checkboxChapter =  inputNodes[2];

        React.addons.TestUtils.Simulate.change(
          inputVocabularyName, {target: {value: "TestB"}}
        );
        component.forceUpdate(function() {
          assert.equal(component.state.name, "TestB");
          React.addons.TestUtils.Simulate.change(
            inputVocabularyDesc, {target: {value: "TestB"}}
          );
          assert.equal(refreshCount, 0);
          component.forceUpdate(function() {
            assert.equal(component.state.description, "TestB");
            React.addons.TestUtils.Simulate.change(
              checkboxChapter,
              {target: {value: 'course', checked: true}}
            );
            component.forceUpdate(function() {
              React.addons.TestUtils.Simulate.click(updateButton);
              component.forceUpdate(function() {
                waitForAjax(1, function() {
                  // Error is caused by a 400 status code
                  assert.deepEqual(
                    component.state.message,
                    {error: "There was a problem with updating the Vocabulary."}
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
            vocabulary={vocabulary}
            closeTaxonomyPanel={closeTaxonomyPanel}
            removePanelVisibility={removePanelVisibility}
            repoSlug="repo"
            learningResourceTypes={learningResourceTypes}
            updateParent={updateParent}
            refreshFromAPI={refreshFromAPI}
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that add term works in TaxonomyComponent',
    function(assert) {
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
      var refreshFromAPI = function() {
        refreshCount++;
      };
      var closeTaxonomyPanel = function() {};
      var setVocabularyActionTabName = function() {};
      var removePanelVisibility = false;
      var done = assert.async();

      var afterMount = function(component) {
        assert.equal(
          component.state.vocabularies.length,
          0
        );
        assert.equal(
          component.state.learningResourceTypes.length,
          0
        );
        waitForAjax(2, function() {
          assert.equal(
            component.state.vocabularies.length,
            1
          );
          assert.equal(
            component.state.vocabularies[0].terms.length,
            2
          );
          assertAddTermCommon(assert, component);
          // Adding second Vocabulary to make sure term added to correct vocabulary
          component.addVocabulary(vocabularyWithoutTerms);
          component.forceUpdate(function() {
            assert.equal(
              component.state.vocabularies.length,
              2
            );
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
            assert.equal(
              component.state.vocabularies[0].terms.length,
              2
            );
            React.addons.TestUtils.Simulate.keyUp(textbox, {key: "Enter"});
            waitForAjax(1, function() {
              assert.equal(
                component.state.vocabularies[0].terms.length,
                3
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
          closeTaxonomyPanel={closeTaxonomyPanel}
          removePanelVisibility={removePanelVisibility}
          repoSlug="repo"
          setVocabularyActionTabName={setVocabularyActionTabName}
          renderConfirmationDialog={function() {}}
          refreshFromAPI={refreshFromAPI}
          ref={afterMount}
        />
      );
    }
  );
  QUnit.test('Assert that add vocabulary works in TaxonomyComponent',
    function(assert) {
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
      var refreshFromAPI = function() {
        refreshCount++;
      };
      var closeTaxonomyPanel = function() {};
      var setVocabularyActionTabName = function() {};
      var removePanelVisibility = false;
      var done = assert.async();
      var afterMount = function(component) {
        assert.equal(
          component.state.vocabularies.length,
          0
        );
        assert.equal(
          component.state.learningResourceTypes.length,
          0
        );
        waitForAjax(2, function() {
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
          var inputVocabularyDesc =  inputNodes[1];
          var checkboxCourse =  inputNodes[2];

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
          waitForAjax(1, function() {
            assert.equal(
              component.state.vocabularies.length,
              2
            );
            assert.equal(refreshCount, 1);
            component.addVocabulary(vocabularyWithoutTerms);
            component.forceUpdate(function() {
              assert.equal(
                component.state.vocabularies.length,
                2
              );
              done();
            });
          });
        });
      };
      React.addons.TestUtils.renderIntoDocument
      (
        <TaxonomyComponent
          closeTaxonomyPanel={closeTaxonomyPanel}
          removePanelVisibility={removePanelVisibility}
          repoSlug="repo"
          setVocabularyActionTabName={setVocabularyActionTabName}
          renderConfirmationDialog={function() {}}
          refreshFromAPI={refreshFromAPI}
          ref={afterMount}
        />
      );
    }
  );

  QUnit.test('Assert that delete vocabulary works in TaxonomyComponent',
    function(assert) {
      assert.ok(TaxonomyComponent, "class object not found");
      var done = assert.async();
      var userSelectedConfirm = 0;
      var setVocabularyActionTabName = function() {};
      var showConfirmationDialog = function (options) {
        options.confirmationHandler(true);
        userSelectedConfirm += 1;
      };

      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };

      var afterMount = function(component) {
        waitForAjax(2, function() {
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
          component.forceUpdate(function() {
            waitForAjax(1, function() {
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
          setVocabularyActionTabName={setVocabularyActionTabName}
          renderConfirmationDialog={showConfirmationDialog}
          refreshFromAPI={refreshFromAPI}
          ref={afterMount}
        />
      );
    }
  );

  QUnit.test('Assert that delete vocabulary ajax call' +
    ' fail in TaxonomyComponent',
    function(assert) {
      assert.ok(TaxonomyComponent, "class object not found");
      var done = assert.async();
      var userSelectedConfirm = 0;
      var setVocabularyActionTabName = function() {};
      var showConfirmationDialog = function (options) {
        options.confirmationHandler(true);
        userSelectedConfirm += 1;
      };

      TestUtils.replaceMockjax({
        url: "/api/v1/repositories/repo/vocabularies/" + vocabulary.slug + "/",
        type: "DELETE",
        status: 400
      });

      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };

      var afterMount = function(component) {
        waitForAjax(2, function() {
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
          waitForAjax(1, function() {
            component.forceUpdate(function() {
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
          setVocabularyActionTabName={setVocabularyActionTabName}
          renderConfirmationDialog={showConfirmationDialog}
          refreshFromAPI={refreshFromAPI}
          ref={afterMount}
        />
      );
    }
  );

  QUnit.test('Assert that edit term works in TaxonomyComponent',
    function(assert) {
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
      var refreshFromAPI = function() {
        refreshCount++;
      };

      TestUtils.initMockjax({
        url: "/api/v1/repositories/demo/vocabularies/",
        contentType: "application/json; charset=utf-8",
        responseText: listOfVocabularies,
        dataType: 'json',
        type: "GET"
      });

      var setVocabularyActionTabName = function() {};
      var afterMount = function(component) {
        assert.equal(
          component.state.vocabularies.length,
          0
        );
        waitForAjax(2, function() {
          assert.equal(
            component.state.vocabularies.length,
            2
          );
          assert.equal(
            component.state.vocabularies[0].terms.length,
            2
          );
          var updateTermUrl = "/api/v1/repositories/demo/vocabularies/" +
              component.state.vocabularies[0].vocabulary.slug + "/terms/" +
              component.state.vocabularies[0].terms[0].slug + "/";
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
          component.forceUpdate(function() {
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
            component.forceUpdate(function() {
              //save term
              assert.equal($(React.findDOMNode(editTermBox)).val(), "TestB");
              React.addons.TestUtils.Simulate.click(saveButton);
              component.forceUpdate(function() {
                //after saved term using api
                waitForAjax(1, function () {
                  assert.equal(refreshCount, 1);
                  //assert term update
                  assert.equal(
                    component.state.vocabularies.length,
                    2
                  );
                  assert.equal(
                    component.state.vocabularies[0].terms.length,
                    2
                  );
                  assert.equal(
                    component.state.vocabularies[0].terms[0].label,
                    "TestB"
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
          setVocabularyActionTabName={setVocabularyActionTabName}
          ref={afterMount}
        />
      );
    }
  );

  QUnit.test('Assert that update vocabulary works in TaxonomyComponent',
    function(assert) {
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
      var removePanelVisibility = false;
      var setVocabularyActionTabName = function() {};
      var closeTaxonomyPanel = function() {};
      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };

      var done = assert.async();
      var afterMount = function(component) {
        waitForAjax(2, function() {
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
          component.forceUpdate(function() {
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
            var inputVocabularyDesc =  inputNodes[1];
            React.addons.TestUtils.Simulate.change(
              inputVocabularyName, {target: {value: "TestA"}}
            );
            component.forceUpdate(function() {
              React.addons.TestUtils.Simulate.change(
                inputVocabularyDesc, {target: {value: "TestA"}}
              );
              component.forceUpdate(function() {
                React.addons.TestUtils.Simulate.click(updateButton);
                component.forceUpdate(function() {
                  waitForAjax(1, function() {
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
          closeTaxonomyPanel={closeTaxonomyPanel}
          removePanelVisibility={removePanelVisibility}
          setVocabularyActionTabName={setVocabularyActionTabName}
          repoSlug="repo"
          refreshFromAPI={refreshFromAPI}
          ref={afterMount}
        />
      );
    }
  );

  QUnit.test('Assert that taxonomy panel close',
    function(assert) {
      assert.ok(TaxonomyComponent, "class object not found");
      var done = assert.async();
      var removePanelVisibility = true;
      var closeTaxonomyPanelCount = 0;
      var setVocabularyActionTabNameCount = 0;
      var closeTaxonomyPanel = function() {
        closeTaxonomyPanelCount += 1;
      };
      var setVocabularyActionTabName = function() {
        setVocabularyActionTabNameCount += 1;
      };
      var refreshCount = 0;
      var refreshFromAPI = function() {
        refreshCount++;
      };
      var afterMount = function(component) {
        assert.equal(closeTaxonomyPanelCount, 1);
        waitForAjax(2, function() {
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
          component.forceUpdate(function() {
            var formNode = React.addons.TestUtils.
              findRenderedDOMComponentWithClass(
              component,
              'form-horizontal'
            );
            var messageNode = React.addons.TestUtils.
              findRenderedDOMComponentWithClass(
              component,
              'alert-dismissible'
            );
            assert.ok(formNode);
            //test form submission
            var inputNodes = React.addons.TestUtils.
              scryRenderedDOMComponentsWithTag(
                formNode,
                'input'
              );
            var inputVocabularyName = inputNodes[0];
            var inputVocabularyDesc =  inputNodes[1];
            // Test for user made changes on edit mode and try exit
            // panel without saving changes. Assert that he will get a warning
            // message to save changes or cancel edit mode.
            React.addons.TestUtils.Simulate.change(
              inputVocabularyName, {target: {value: "TestA"}}
            );
            component.forceUpdate(function() {
              React.addons.TestUtils.Simulate.change(
                inputVocabularyDesc, {target: {value: "TestA"}}
              );
              component.forceUpdate(function() {
                assert.equal(
                  $(React.findDOMNode(messageNode)).html(),
                  'Please save changes or cancel before exit.'
                );
                done();
              });
            });
          });
        });
      };
      React.addons.TestUtils.renderIntoDocument
      (
        <TaxonomyComponent
          closeTaxonomyPanel={closeTaxonomyPanel}
          removePanelVisibility={removePanelVisibility}
          repoSlug="repo"
          setVocabularyActionTabName={setVocabularyActionTabName}
          refreshFromAPI={refreshFromAPI}
          ref={afterMount}
        />
      );
    }
  );

  QUnit.test("Test that ManageTaxonomies.loader renders into div",
    function(assert) {
      var container = document.createElement("div");
      assert.equal(0, $(container).find("input").size());
      ManageTaxonomies.loader(
        "repo", container, function() {}, function() {}, function() {},
        function() {}
      );
      assert.equal(5, $(container).find("input").size());
    }
  );

  QUnit.test("Assert that ConfirmationDialog  renders " +
    "proper props",
    function(assert) {
      var container = document.createElement("div");
      assert.equal(0, $(container).find(".modal").size());
      var options = {
        actionButtonName: "Delete",
        actionButtonClass: "btn btn-danger btn-ok",
        title: "Delete ?",
        message: "Are you sure you want to delete vocabulary ?",
        description: "Deleting this vocabulary will remove it from all " +
          "learning resources.",
        confirmationHandler: function() {}
      };
      showConfirmationDialog(options, container);
      assert.equal(1, $(container).find(".modal").size());
    }
  );
});
