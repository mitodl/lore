define(["QUnit", "react", "test_utils", "jquery", "lodash",
    "learning_resource_panel"],
  function (QUnit, React, TestUtils, $, _, LearningResourcePanel) {
    'use strict';

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
    var learningResourceResponseMinusContentXml = $.extend(
      {}, learningResourceResponse);
    delete learningResourceResponseMinusContentXml.content_xml;
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
      beforeEach: function () {
        TestUtils.setup();

        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo/learning_resources/1/',
          type: 'GET',
          responseText: learningResourceResponse
        });
        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo/learning_resources/' +
          '1/?remove_content_xml=true',
          type: 'GET',
          responseText: learningResourceResponseMinusContentXml
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
          url: '/api/v1/repositories/repo/vocabularies/' +
            '?type_name=course&page=2',
          type: 'GET',
          responseText: vocabulariesResponseSecond
        });
        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo/vocabularies/difficulty/terms/',
          type: 'POST',
          responseText: termResponseMedium
        });
      },
      afterEach: function () {
        TestUtils.cleanup();
      }
    });

    QUnit.test(
      'Assert that LearningResourcePanel changes state properly',
      function (assert) {
        var done = assert.async();
        var closeLearningResourcePanel = function () {
        };
        var afterMount = function (component) {
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
            component.forceUpdate(function () {
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
              component.forceUpdate(function () {
                // Switch to difficulty
                $vocabSelect.val("difficulty").trigger('change');
                component.forceUpdate(function () {
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
          closeLearningResourcePanel={closeLearningResourcePanel}
          learningResourceId="1"
          ref={afterMount}/>);
      }
    );
    QUnit.test(
      'Assert that LearningResourcePanel saves properly',
      function (assert) {
        var done = assert.async();
        var closeLearningResourcePanelCount = 0;
        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };
        var closeLearningResourcePanel = function () {
          closeLearningResourcePanelCount += 1;
        };
        var afterMount = function (component) {
          // wait for calls to populate form
          waitForAjax(3, function () {
            var $node = $(React.findDOMNode(component));

            assert.equal(refreshCount, 0);
            var saveButton = $node.find("button")[0];
            var saveAndCloseButton = $node.find("button")[1];
            React.addons.TestUtils.Simulate.click(saveButton);
            waitForAjax(1, function () {
              assert.equal(component.state.message,
                "Form saved successfully!");
              assert.equal(refreshCount, 1);
              //assert that panel does not close on save button click
              assert.equal(closeLearningResourcePanelCount, 0);
              React.addons.TestUtils.Simulate.click(saveAndCloseButton);
              component.forceUpdate(function () {
                assert.equal(component.state.loaded, false);
                waitForAjax(1, function () {
                  assert.equal(component.state.loaded, true);
                  assert.equal(component.state.message,
                    "Form saved successfully!");
                  assert.equal(refreshCount, 2);
                  //assert that panel close after save
                  assert.equal(closeLearningResourcePanelCount, 1);
                  done();
                });
              });
            });
          });
        };

        React.addons.TestUtils.renderIntoDocument(<LearningResourcePanel
          repoSlug="repo"
          learningResourceId="1"
          closeLearningResourcePanel={closeLearningResourcePanel}
          refreshFromAPI={refreshFromAPI}
          ref={afterMount}/>);
      }
    );

    QUnit.test(
      'An error should show up on AJAX failure while saving form',
      function (assert) {
        var done = assert.async();
        var closeLearningResourcePanelCount = 0;
        var closeLearningResourcePanel = function () {
          closeLearningResourcePanelCount += 1;
        };
        var refreshCount = 0;
        var refreshFromAPI = function () {
          refreshCount++;
        };

        var afterMount = function (component) {
          // wait for calls to populate form
          waitForAjax(3, function () {
            var $node = $(React.findDOMNode(component));

            assert.equal(0, refreshCount);

            TestUtils.replaceMockjax({
              url: '/api/v1/repositories/repo/learning_resources/1/',
              type: 'PATCH',
              status: 400
            });
            var saveButton = $node.find("button")[0];
            React.addons.TestUtils.Simulate.click(saveButton);
            component.forceUpdate(function () {
              assert.equal(component.state.loaded, false);
              waitForAjax(1, function () {
                assert.equal(component.state.loaded, true);
                assert.deepEqual(
                  component.state.message,
                  {error: "Unable to save form"}
                );

                assert.equal(0, refreshCount);
                //assert that panel does not close on ajax fail
                assert.equal(closeLearningResourcePanelCount, 0);
                done();
              });
            });
          });
        };

        React.addons.TestUtils.renderIntoDocument(<LearningResourcePanel
          repoSlug="repo"
          closeLearningResourcePanel={closeLearningResourcePanel}
          learningResourceId="1"
          refreshFromAPI={refreshFromAPI}
          ref={afterMount}/>);
      }
    );

    QUnit.test(
      'An error should show up on AJAX failure while ' +
      'getting learning resource info',
      function (assert) {
        var done = assert.async();
        var closeLearningResourcePanel = function () {
        };
        TestUtils.replaceMockjax({
          url: '/api/v1/repositories/repo/learning_resources/1/' +
          '?remove_content_xml=true',
          type: 'GET',
          status: 400
        });
        var afterMount = function (component) {
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
          closeLearningResourcePanel={closeLearningResourcePanel}
          learningResourceId="1"
          ref={afterMount}/>);
      }
    );

    QUnit.test(
      'An error should show up on AJAX failure while ' +
      'getting vocabularies',
      function (assert) {
        var closeLearningResourcePanel = function () {
        };
        var done = assert.async();

        TestUtils.replaceMockjax({
          url: '/api/v1/repositories/repo/vocabularies/?type_name=course',
          type: 'GET',
          status: 400
        });
        var afterMount = function (component) {
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
          closeLearningResourcePanel={closeLearningResourcePanel}
          learningResourceId="1"
          ref={afterMount}/>);
      }
    );

    QUnit.test('If terms or description are changed, clear error messages',
      function (assert) {
        var done = assert.async();

        var afterMount = function (component) {
          waitForAjax(3, function () {
            // Set component message then type into description to clear it.
            component.setState({message: "Hello, world!"}, function () {
              var textarea = React.addons.TestUtils.
                findRenderedDOMComponentWithTag(
                component,
                'textarea'
              );

              React.addons.TestUtils.Simulate.change(textarea, {value: "x"});
              component.forceUpdate(function () {
                assert.equal(component.state.message, undefined);

                // Reset component message then adjust vocabs list to clear it.
                component.setState({message: "Hello, world!"}, function () {
                  var selects = _.map(React.addons.TestUtils.
                    scryRenderedDOMComponentsWithTag(
                    component,
                    'select'
                  ), function (piece) {
                    return React.findDOMNode(piece);
                  });

                  // First is vocab, second is terms
                  assert.equal(selects.length, 2);
                  $(selects[0]).val('difficulty').trigger('change');
                  component.forceUpdate(function () {
                    assert.equal(component.state.message, undefined);

                    // Reset component message then
                    // adjust term list to clear it.
                    component.setState({message: {error: "Error!"}},
                      function () {
                        $(selects[1]).val('required').trigger('change');

                        component.forceUpdate(function () {
                          assert.equal(component.state.message, undefined);

                          done();
                        });
                      }
                    );
                  });
                });
              });
            });
          });
        };

        React.addons.TestUtils.renderIntoDocument(
          <LearningResourcePanel
            repoSlug="repo"
            closeLearningResourcePanel={function() {}}
            learningResourceId="1"
            ref={afterMount}/>
        );
      }
    );
  }
);
