define(['QUnit', 'jquery', 'react', 'lodash', 'learning_resources',
  'test_utils', 'jquery_mockjax'], function(
  QUnit, $, React, _, LearningResources, TestUtils) {
  'use strict';

  var VocabSelect = LearningResources.VocabSelect;
  var TermList = LearningResources.TermList;
  var TermSelect = LearningResources.TermSelect;
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
        responseText: vocabulariesResponseFirst
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo/vocabularies/?type_name=course&page=2',
        type: 'GET',
        responseText: vocabulariesResponseSecond
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo/vocabularies/difficulty/terms/',
        type: 'POST',
        responseText: termResponseMedium
      });
    },
    afterEach: function() {
      TestUtils.cleanup();
    }
  });

  QUnit.test(
    'Assert that VocabSelect renders properly',
    function (assert) {
      var done = assert.async();

      var afterMount = function(component) {
        var $node = $(React.findDOMNode(component));

        var $vocabSelect = $node.find("select");
        assert.equal($vocabSelect.size(), 1);

        done();
      };

      React.addons.TestUtils.renderIntoDocument(
        <VocabSelect
          vocabs={vocabulariesAndTerms}
          selectedVocabulary={selectedVocabulary}
          ref={afterMount}
        />
      );
    }
  );

  QUnit.test(
    'Assert that TermSelect renders properly',
    function (assert) {
      var done = assert.async();

      var afterMount = function(component) {
        var $node = $(React.findDOMNode(component));

        var $termSelect = $node.find("select");
        assert.equal($termSelect.size(), 1);

        done();
      };

      React.addons.TestUtils.renderIntoDocument(
        <TermSelect
          vocabs={vocabulariesAndTerms}
          selectedVocabulary={selectedVocabulary}
          ref={afterMount}
        />
      );
    }
  );

  QUnit.test(
    'Assert that TermList renders properly',
    function (assert) {
      var done = assert.async();
      var afterMount = function(component) {
        var $node = $(React.findDOMNode(component));
        var $termList = $node.find("ul");
        assert.equal($termList.size(), 1);
        done();
      };

      React.addons.TestUtils.renderIntoDocument(
        <TermList
          vocabs={vocabulariesAndTerms}
          ref={afterMount}
        />
      );
    }
  );
  QUnit.test(
    'Assert that LearningResourcePanel changes state properly',
    function(assert) {
      var done = assert.async();
      var afterMount = function(component) {
        // wait for calls to populate form
        waitForAjax(3, function () {
          // two menus: vocabulary and terms.
          var $node = $(React.findDOMNode(component));

          var $allSelects = $node.find("#vocabularies select");
          assert.equal($allSelects.size(), 2);

          var $vocabSelect = $node.find($allSelects).first();
          assert.equal($vocabSelect.size(), 1);

          // first vocab, two options
          var $vocabOptions = $vocabSelect.find("option");
          assert.equal($vocabOptions.size(), 2);

          assert.equal($vocabOptions[0].selected, true);
          assert.equal($vocabOptions[1].selected, false);

          // TestUtils.Simulate.change only simulates a change event,
          // we need to update the value first ourselves
          $vocabSelect.val("prerequisite").trigger('change');
          component.forceUpdate(function() {
            assert.equal($vocabOptions[0].selected, false);
            assert.equal($vocabOptions[1].selected, true);
            // re-fetch the selects to get the prerequisite one
            $allSelects = $node.find("#vocabularies select");
            var termsSelect = $allSelects[1];
            var $termsOptions = $(termsSelect).find("option");
            assert.equal($termsOptions.size(), 2);
            assert.equal($termsOptions[0].selected, true);
            assert.equal($termsOptions[1].selected, false);
            assert.equal($(termsSelect).val(), "required");

            // remove selection for this vocabulary to not interfere to the rest of the test
            $(termsSelect).val("").trigger('change');
            component.forceUpdate(function() {
              // Switch to difficulty
              $vocabSelect.val("difficulty").trigger('change');
              component.forceUpdate(function() {
                // re-fetch the selects to get the difficulty one
                $allSelects = $node.find("#vocabularies select");
                // update the term select
                termsSelect = $allSelects[1];
                $termsOptions = $(termsSelect).find("option");

                assert.equal($termsOptions.size(), 2);
                assert.equal($termsOptions[0].selected, false);
                assert.equal($termsOptions[1].selected, false);
                // the second vocabulary can be a multi select
                $(termsSelect)
                  .val(["hard", "easy"])
                  .trigger('change');
                component.forceUpdate(function () {
                  assert.equal($termsOptions[0].selected, true);
                  assert.equal($termsOptions[1].selected, true);
                  // be sure that the state reflects the selection
                  var terms = _.map(component.state.vocabulariesAndTerms,
                    function (tuple) {
                      return tuple.selectedTerms;
                    });
                  terms = _.flatten(terms);
                  terms.sort();
                  var expectedTerms = [
                    $termsOptions[0].value,
                    $termsOptions[1].value
                  ];
                  expectedTerms.sort();
                  assert.deepEqual(terms, expectedTerms);

                  // the second vocabulary also allows free tagging
                  $(termsSelect)
                    // hack to simulate the free tagging
                    .append($('<option />', {value: 'medium'}))
                    .val(["hard", "easy", "medium"])
                    .trigger('change');
                  waitForAjax(1, function () {
                    component.forceUpdate(function () {
                      // check if the new option has been added
                      $termsOptions = $(termsSelect).find("option");
                      assert.equal($termsOptions.size(), 3);
                      assert.equal($termsOptions[0].selected, true);
                      assert.equal($termsOptions[1].selected, true);
                      assert.equal($termsOptions[2].selected, true);
                      // be sure that the state reflects the selection
                      var terms = _.map(component.state.vocabulariesAndTerms,
                        function (tuple) {
                          return tuple.selectedTerms;
                        });
                      terms = _.flatten(terms);
                      terms.sort();
                      var expectedTerms = [
                        $termsOptions[0].value,
                        $termsOptions[1].value,
                        $termsOptions[2].value
                      ];
                      expectedTerms.sort();
                      assert.deepEqual(terms, expectedTerms);
                      done();
                    });
                  });

                });
              });
            });
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
    'Assert that LearningResourcePanel saves properly',
    function(assert) {
      var done = assert.async();

      var afterMount = function(component) {
        // wait for calls to populate form
        waitForAjax(3, function () {
          var $node = $(React.findDOMNode(component));

          var saveButton = $node.find("button")[0];
          React.addons.TestUtils.Simulate.click(saveButton);
          waitForAjax(1, function() {
            assert.equal(component.state.message,
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
      var afterMount = function(component) {
        // wait for calls to populate form
        waitForAjax(3, function () {
          var $node = $(React.findDOMNode(component));

          TestUtils.replaceMockjax({
            url: '/api/v1/repositories/repo/learning_resources/1/',
            type: 'PATCH',
            status: 400
          });
          var saveButton = $node.find("button")[0];
          React.addons.TestUtils.Simulate.click(saveButton);
          waitForAjax(1, function() {
            assert.deepEqual(
              component.state.message,
              {error: "Unable to save form"}
            );
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
          assert.deepEqual(
            component.state.message,
            {error: "Unable to read information about learning resource."}
          );

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
          assert.deepEqual(
            component.state.message,
            {error: "Unable to read information about learning resource."}
          );

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
        waitForAjax(3, function () {
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
