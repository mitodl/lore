define(['QUnit', 'jquery', 'setup_manage_taxonomies', 'reactaddons',
  'test_utils'],
  function(QUnit, $, ManageTaxonomies, React, TestUtils) {
  'use strict';

  var VocabularyComponent = ManageTaxonomies.VocabularyComponent;
  var waitForAjax = TestUtils.waitForAjax;
  var TermComponent = ManageTaxonomies.TermComponent;
  var AddTermsComponent = ManageTaxonomies.AddTermsComponent;
  var AddVocabulary = ManageTaxonomies.AddVocabulary;
  var TaxonomyComponent = ManageTaxonomies.TaxonomyComponent;
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
  function  assertAddTermCommon(assert, component) {
    // check term title
    var listOfLinks = React.addons.TestUtils.
      scryRenderedDOMComponentsWithTag(
        component,
        'a'
    );
    assert.equal(listOfLinks.length, 2);
    var linkHeader = React.findDOMNode(listOfLinks[0]);
    assert.equal(linkHeader.innerHTML, vocabulary.name);
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
    assert.equal(itemList.length, 2);
    return devItems;
  }
  QUnit.module('Test taxonomies panel', {
    beforeEach: function() {
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
            "terms": vocabulary.terms
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
      var duplicateVocabularyResponse = {
        "non_field_errors":[
          "The fields repository, name must make a unique set."
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
        url: "/api/v1/repositories/repo2/vocabularies/",
        type: "POST",
        status: 400
      });
      TestUtils.initMockjax({
        url: "/api/v1/repositories/repo3/vocabularies/",
        contentType: "application/json; charset=utf-8",
        responseText: duplicateVocabularyResponse,
        dataType: 'json',
        type: "POST",
        status: 400
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
    },
    afterEach: function() {
      TestUtils.cleanup();
    }
  });

  QUnit.test('Assert that TermComponent renders properly',
    function(assert) {
      assert.ok(TermComponent, "class object not found");
      var term = {
        "id": 9,
        "slug": "test",
        "label": "test",
        "weight": 1
      };
      var termComponentRendered = React.addons.TestUtils.
        renderIntoDocument(
          <TermComponent
            term={term}
          />
        );

      var labelComponent = React.addons.TestUtils.
        findRenderedDOMComponentWithTag(
          termComponentRendered,
          'label'
      );
      //testing label value render
      var label = labelComponent.getDOMNode();
      assert.equal(label.innerHTML, term.label);
    }
  );

  QUnit.test('Assert that VocabularyComponent renders properly',
    function(assert) {
      assert.ok(VocabularyComponent, "class object not found");
      var done = assert.async();

      var addTermCalled = 0;
      var addTerm = function() {
        addTermCalled += 1;
      };
      var reportError = function() {};
      var afterMount = function(component) {
        var node = React.findDOMNode(component);
        var textbox = $(node).find("input")[0];

        // check term title
        var listOfLinks = React.addons.TestUtils.
          scryRenderedDOMComponentsWithTag(
            component,
            'a'
        );
        assert.equal(listOfLinks.length, 2);
        var linkHeader = React.findDOMNode(listOfLinks[0]);
        assert.equal(linkHeader.innerHTML, vocabulary.name);

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
        assert.equal(itemList.length, 2);
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
        component.forceUpdate(function() {
          assert.equal(
            'test12',
            component.state.newTermLabel
          );
          React.addons.TestUtils.Simulate.keyUp(textbox, {key: "x"});
          assert.equal(addTermCalled, 0);

          React.addons.TestUtils.Simulate.keyUp(textbox, {key: "Enter"});
          waitForAjax(1, function() {
            assert.equal(addTermCalled, 1);
            done();
          });
        });
      };
      React.addons.TestUtils.
        renderIntoDocument(
          <VocabularyComponent
            vocabulary={vocabulary}
            terms={vocabulary.terms}
            reportError={reportError}
            addTerm={addTerm}
            repoSlug="repo"
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
      var errorMessage;
      var addTerm = function() {
        addTermCalled += 1;
      };
      var reportError = function(msg) {
        errorMessage = msg;
      };
      var afterMount = function(component) {
        // wait for calls to populate form
        var node = React.findDOMNode(component);
        var textbox = $(node).find("input")[0];
        React.addons.TestUtils.Simulate.keyUp(textbox, {key: "Enter"});
        waitForAjax(1, function () {
          assert.equal(addTermCalled, 0);
          assert.equal(//Error is caused by a 400 status code
            errorMessage,
            "Error occurred while adding new term."
          );
          done();
        });
      };
      React.addons.TestUtils.
        renderIntoDocument(
          <VocabularyComponent
            vocabulary={vocabulary}
            terms={vocabulary.terms}
            reportError={reportError}
            addTerm={addTerm}
            repoSlug="repo"
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
      var afterMount = function(component) {
        assert.equal(
         component.state.errorText,
          ''
        );
        assertAddTermCommon(assert, component);
        //test error message
        component.reportError(
          "Error occurred while adding new term."
        );
        component.forceUpdate(function() {
          assert.equal(
            component.state.errorText,
            'Error occurred while adding new term.'
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
            done();
          });
        });
      };
      var addTerm = function() {
        addTermCalled += 1;
      };
      React.addons.TestUtils.
        renderIntoDocument(
          <AddTermsComponent
            vocabularies={vocabularies}
            repoSlug="repo"
            addTerm={addTerm}
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that AddVocabulary work properly',
    function(assert) {
      assert.ok(AddVocabulary, "class object not found");
      var vocabularies = [
        {
          "vocabulary": vocabulary,
          "terms": vocabulary.terms
        }
      ];
      var learningResourceTypes = ['course', 'chapter', 'sequential',
        'vertical', 'html', 'video', 'discussion', 'problem'];
      var saveVocabularyResponse;
      var done = assert.async();
      var updateParent = function(data) {
        saveVocabularyResponse = data;
      };
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
        assert.equal(inputNodes.length, 12);
        var inputVocabularyName = inputNodes[0];
        var inputVocabularyDesc =  inputNodes[1];
        var radioTagStyle = inputNodes[11];

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
        component.forceUpdate(function() {
          assert.equal(component.state.name, "TestA");
          assert.equal(component.state.vocabularyType, "f");
          assert.equal(component.state.description, "TestA");
          assert.equal(
            component.state.learningResourceTypes.length,
            0
          );
          React.addons.TestUtils.Simulate.submit(formNode);
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
            var inputNodes = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
              formNode,
              'input'
            );
            var inputVocabularyName = inputNodes[0];
            var inputVocabularyDesc =  inputNodes[1];
            var checkboxCourse =  inputNodes[2];
            var radioTagStyle = inputNodes[11];

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
            component.forceUpdate(function() {
              assert.equal(component.state.name, "TestB");
              assert.equal(component.state.description, "TestB");
              assert.equal(component.state.vocabularyType, "f");
              assert.equal(
                component.state.learningResourceTypes[0],
                'course'
              );
              React.addons.TestUtils.Simulate.submit(formNode);
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
                  saveVocabularyResponse.id,
                  vocabulary.id
                );
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

                component.forceUpdate(function() {
                  assert.equal(component.state.name, "TestC");
                  assert.equal(component.state.description, "TestC");
                  assert.equal(component.state.vocabularyType, "f");
                  assert.equal(
                    component.state.learningResourceTypes[0],
                    'course'
                  );
                  //uncheck checkbox
                  React.addons.TestUtils.Simulate.change(
                    checkboxCourse,
                    {target: {value: 'course', checked: false}}
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
                    React.addons.TestUtils.Simulate.submit(formNode);
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
            vocabularies={vocabularies}
            repoSlug="repo"
            updateParent={updateParent}
            learningResourceTypes={learningResourceTypes}
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that ajax fail in AddVocabulary',
    function(assert) {
      assert.ok(AddVocabulary, "class object not found");
      var vocabularies = [
        {
          "vocabulary": vocabulary,
          "terms": vocabulary.terms
        }
      ];
      var done = assert.async();
      var updateParent = function() {};
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
        assert.equal(inputNodes.length, 4);
        var inputVocabularyName = inputNodes[0];
        var inputVocabularyDesc =  inputNodes[1];
        var checkboxCourse =  inputNodes[2];

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
        React.addons.TestUtils.Simulate.submit(formNode);
        waitForAjax(1, function() {
          assert.equal(//Error is caused by a 400 status code
            component.state.errorMessage,
            "There was a problem adding the Vocabulary."
          );
          done();
        });
      };
      React.addons.TestUtils.
        renderIntoDocument(
          <AddVocabulary
            vocabularies={vocabularies}
            repoSlug="repo2"
            updateParent={updateParent}
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that ajax fail in AddVocabulary: Duplicate Vocabulary',
    function(assert) {
      assert.ok(AddVocabulary, "class object not found");
      var vocabularies = [
        {
          "vocabulary": vocabulary,
          "terms": vocabulary.terms
        }
      ];
      var done = assert.async();
      var updateParent = function() {};
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
        assert.equal(inputNodes.length, 4);
        var inputVocabularyName = inputNodes[0];
        var inputVocabularyDesc =  inputNodes[1];
        var checkboxCourse =  inputNodes[2];

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
        React.addons.TestUtils.Simulate.submit(formNode);
        waitForAjax(1, function() {
          assert.equal(//Error is caused by a 400 status code
            component.state.errorMessage,
            'A Vocabulary named "" already exists.' +
            ' Please choose a different name.'
          );
          done();
        });
      };
      React.addons.TestUtils.
        renderIntoDocument(
          <AddVocabulary
            vocabularies={vocabularies}
            repoSlug="repo3"
            updateParent={updateParent}
            ref={afterMount}
          />
        );
    }
  );

  QUnit.test('Assert that add term works in TaxonomyComponent',
    function(assert) {
      assert.ok(TaxonomyComponent, "class object not found");
      var vocabularies = [
        {
          "vocabulary": vocabulary,
          "terms": vocabulary.terms
        }
      ];
      var vocabularyWithoutTerms = {
        "id": 2,
        "slug": "difficulty2",
        "name": "difficulty2",
        "description": "easy",
        "vocabulary_type": "f",
        "required": false,
        "weight": 2147483647,
      };
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
              done();
            });
          });
        });
      };
      React.addons.TestUtils.renderIntoDocument
      (
        <TaxonomyComponent
          vocabularies={vocabularies}
          repoSlug="repo"
          ref={afterMount}
        />
      );
    }
  );
  QUnit.test('Assert that add vocabulary works in TaxonomyComponent',
    function(assert) {
      assert.ok(TaxonomyComponent, "class object not found");
      var vocabularies = [
        {
          "vocabulary": vocabulary,
          "terms": vocabulary.terms
        }
      ];
      var vocabularyWithoutTerms = {
        "id": 2,
        "slug": "difficulty2",
        "name": "difficulty2",
        "description": "easy",
        "vocabulary_type": "f",
        "required": false,
        "weight": 2147483647,
      };
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
          assert.ok(formNode);
          //test form submission
          var inputNodes = React.addons.TestUtils.
            scryRenderedDOMComponentsWithTag(
              formNode,
              'input'
            );
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
          React.addons.TestUtils.Simulate.submit(formNode);
          waitForAjax(1, function() {
            assert.equal(
              component.state.vocabularies.length,
              2
            );
            component.addVocabulary(vocabularyWithoutTerms);
            component.forceUpdate(function() {
              assert.equal(
                component.state.vocabularies.length,
                3
              );
              done();
            });
          });
        });
      };
      React.addons.TestUtils.renderIntoDocument
      (
        <TaxonomyComponent
          vocabularies={vocabularies}
          repoSlug="repo"
          ref={afterMount}
        />
      );
    }
  );
});
