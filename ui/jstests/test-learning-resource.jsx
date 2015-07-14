define(['QUnit', 'jquery', 'learning_resources', 'reactaddons',
  'test_utils', 'jquery_mockjax'], function(
  QUnit, $, LearningResources, React, TestUtils) {
  'use strict';

  var VocabularyOption = LearningResources.VocabularyOption;
  var LearningResourcePanel = LearningResources.LearningResourcePanel;
  var waitForAjax = TestUtils.waitForAjax;

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
  var prereqTermsResponseRequired = {
    "id": 3,
    "slug": "required",
    "label": "required",
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
    "terms": [prereqTermsResponseRequired]
  };
  var vocabularyResponseDifficulty = {
    "id": 1,
    "slug": "difficulty",
    "name": "difficulty",
    "description": "Difficulty",
    "vocabulary_type": "f",
    "required": false,
    "weight": 2147483647,
    "terms": [termResponseEasy, termResponseHard]
  };
  var vocabulariesResponse = {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [vocabularyResponseDifficulty, vocabularyResponsePrereq]
  };
  var difficultyTermsResponse = {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [termResponseEasy, termResponseHard]
  };

  QUnit.module('Test learning resource panel', {
    beforeEach: function() {
      TestUtils.setup();

      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo/learning_resources/1/',
        type: 'GET',
        responseText: learningResourceResponse
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo/learning_resources/1/',
        type: 'PATCH',
        responseText: learningResourceResponse
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo/vocabularies/?type_name=course',
        type: 'GET',
        responseText: vocabulariesResponse
      });
    },
    afterEach: function() {
      TestUtils.cleanup();
    }
  });

  QUnit.test(
    'Assert that VocabularyOption renders properly',
    function (assert) {
      var done = assert.async();
      var afterMount = function (component) {
        var $node = $(React.findDOMNode(component));

        // one vocabulary
        var $vocabSelect = $node.find("select");
        assert.equal($vocabSelect.size(), 1);

        // two terms
        var $termsSelect = $vocabSelect.find("option");
        assert.equal($termsSelect.size(), 3);
        assert.equal($termsSelect[0].text, "");
        assert.equal($termsSelect[0].value, "");
        assert.equal($termsSelect[1].text, "easy");
        assert.equal($termsSelect[1].value, "easy");
        assert.equal($termsSelect[2].text, "hard");
        assert.equal($termsSelect[2].value, "hard");

        done();
      };

      React.addons.TestUtils.renderIntoDocument(
        <VocabularyOption vocabulary={vocabularyResponseDifficulty}
                          terms={difficultyTermsResponse.results}
                          selectedTerm="hard"
                          ref={afterMount}/>
      );
    }
  );

  QUnit.test(
    'Assert that LearningResourcePanel changes state properly',
    function(assert) {
      var done = assert.async();

      var afterMount = function(component) {
        // wait for calls to populate form
        waitForAjax(2, function () {
          // one vocabulary
          var $node = $(React.findDOMNode(component));
          var $vocabSelect = $node.find("select");
          assert.equal($vocabSelect.size(), 2);

          // two terms, first vocab
          var $terms1Select = $($vocabSelect[0]).find("option");
          assert.equal($terms1Select.size(), 3);
          assert.equal($terms1Select[0].selected, true);
          assert.equal($terms1Select[1].selected, false);
          assert.equal($terms1Select[2].selected, false);

          // TestUtils.Simulate.change only simulates a change event,
          // we need to update the value first ourselves
          $vocabSelect[0].value = "hard";
          React.addons.TestUtils.Simulate.change($vocabSelect[0]);
          assert.equal($terms1Select[0].selected, false);
          assert.equal($terms1Select[1].selected, false);
          assert.equal($terms1Select[2].selected, true);

          // make sure second vocab (which has a default value) is set properly
          var $terms2Select = $($vocabSelect[1]).find("option");
          assert.equal($terms2Select.size(), 2);
          assert.equal($terms2Select[0].selected, false);
          assert.equal($terms2Select[1].selected, true);

          done();
        });
      };

      React.addons.TestUtils.renderIntoDocument(<LearningResourcePanel
        repoSlug="repo"
        learningResourceId="1"
        ref={afterMount} />);
    }
  );

  QUnit.test(
    'Assert that LearningResourcePanel saves properly',
    function(assert) {
      var done = assert.async();

      var afterMount = function(component) {
        // wait for calls to populate form
        waitForAjax(2, function () {
          var $node = $(React.findDOMNode(component));

          var saveButton = $node.find("button")[0];
          React.addons.TestUtils.Simulate.click(saveButton);
          waitForAjax(1, function() {
            assert.equal(component.state.errorText, undefined);
            assert.equal(component.state.messageText,
              "Form saved successfully!");
            done();
          });
        });
      };

      React.addons.TestUtils.renderIntoDocument(<LearningResourcePanel
        repoSlug="repo"
        learningResourceId="1"
        ref={afterMount} />);
    }
  );
  QUnit.test(
    'An error should show up on AJAX failure while saving form',
    function(assert) {
      var done = assert.async();
      var thiz = this;

      var afterMount = function(component) {
        // wait for calls to populate form
        waitForAjax(2, function () {
          var $node = $(React.findDOMNode(component));

          $.mockjax.clear(thiz.learningResourcesPatchId);
          TestUtils.initMockjax({
            url: '/api/v1/repositories/repo/learning_resources/1/',
            type: 'PATCH',
            status: 400
          });
          var saveButton = $node.find("button")[0];
          React.addons.TestUtils.Simulate.click(saveButton);
          waitForAjax(1, function() {
            assert.equal(component.state.errorText, "Unable to save form");
            assert.equal(component.state.messageText, undefined);
            done();
          });
        });
      };

      React.addons.TestUtils.renderIntoDocument(<LearningResourcePanel
        repoSlug="repo"
        learningResourceId="1"
        ref={afterMount} />);
    }
  );

  QUnit.test(
    'An error should show up on AJAX failure while ' +
    'getting learning resource info',
    function(assert) {
      var done = assert.async();

      TestUtils.replaceMockjax({
        url: '/api/v1/repositories/repo/learning_resources/1/',
        type: 'GET',
        status: 400
      });
      var afterMount = function(component) {
        // wait for calls to populate form
        waitForAjax(1, function () {
          assert.equal(component.state.errorText,
            "Unable to read information about learning resource.");
          assert.equal(component.state.messageText, undefined);

          done();
        });
      };
      React.addons.TestUtils.renderIntoDocument(<LearningResourcePanel
        repoSlug="repo"
        learningResourceId="1"
        ref={afterMount} />);
    }
  );

  QUnit.test(
    'An error should show up on AJAX failure while ' +
    'getting vocabularies',
    function(assert) {
      var done = assert.async();

      TestUtils.replaceMockjax({
        url: '/api/v1/repositories/repo/vocabularies/?type_name=course',
        type: 'GET',
        status: 400
      });
      var afterMount = function(component) {
        // wait for calls to populate form
        waitForAjax(2, function () {
          assert.equal(component.state.errorText,
            "Unable to read information about learning resource.");
          assert.equal(component.state.messageText, undefined);

          done();
        });
      };
      React.addons.TestUtils.renderIntoDocument(<LearningResourcePanel
        repoSlug="repo"
        learningResourceId="1"
        ref={afterMount} />);
    }
  );

  QUnit.test(
    'Textarea should be selected',
    function(assert) {
      var done = assert.async();
      var afterMount = function(component) {
        var $node = $(React.findDOMNode(component));

        // wait for calls to populate form
        waitForAjax(2, function () {
          var $selectLink = $node.find("#copy-textarea-xml");
          var textarea = $node.find(".textarea-xml")[0];

          textarea.selectionEnd = 0;

          assert.equal(textarea.selectionStart, 0);
          assert.equal(textarea.selectionEnd, 0);

          React.addons.TestUtils.Simulate.click($selectLink[0]);

          assert.equal(textarea.selectionStart, 0);
          assert.equal(textarea.selectionEnd, 10);

          $("#testingDiv").remove();
          done();
        });
      };

      // for selection testing to work this needs to be in the DOM
      $("body").append($("<div id='testingDiv'>TEST</div>"));

      React.render(<LearningResourcePanel repoSlug="repo"
        learningResourceId="1"
        ref={afterMount} />, $("#testingDiv")[0]);
    }
  );
  QUnit.test(
    "LearningResourcePanel.loader should populate its stuff",
    function(assert) {
      var div = document.createElement("div");
      assert.equal(0, $(div).find("textarea").size());
      LearningResources.loader("repo", "1", div);
      assert.equal(2, $(div).find("textarea").size());
    }
  );
});
