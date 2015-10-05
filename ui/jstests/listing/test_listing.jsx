define(['QUnit', 'jquery', 'react', 'test_utils', 'utils', 'listing'],
  function (QUnit, $, React, TestUtils, Utils, Listing) {
    'use strict';

    var waitForAjax = TestUtils.waitForAjax;

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

    var searchResponseAll = {
      "count": 3,
      "next": null,
      "previous": null,
      "results": [
        {
          "resource_type": "course",
          "course": "8.01",
          "run": "2014_Fall",
          "xa_nr_views": 0,
          "xa_nr_attempts": 0,
          "xa_avg_grade": 0.0,
          "id": 1,
          "title": "MISSING",
          "description": "",
          "description_path": "MISSING",
          "preview_url": "..."
        },
        {
          "resource_type": "chapter",
          "course": "8.01",
          "run": "2014_Fall",
          "xa_nr_views": 0,
          "xa_nr_attempts": 0,
          "xa_avg_grade": 0.0,
          "id": 2,
          "title": "Course Information",
          "description": "",
          "description_path": "MISSING / Course Information",
          "preview_url": "..."
        },
        {
          "resource_type": "course",
          "course": "DemoX",
          "run": "Demo_Course",
          "xa_nr_views": 0,
          "xa_nr_attempts": 0,
          "xa_avg_grade": 0.0,
          "id": 1375,
          "title": "Open edX Demonstration Course",
          "description": "",
          "description_path": "Open edX Demonstration Course",
          "preview_url": "..."
        }
      ],
      "facet_counts": {
        "run": {
          "facet": {
            "key": "run",
            "label": "Run"
          },
          "values": [
            {
              "count": 2,
              "key": "2014_Fall",
              "label": "2014_Fall"
            },
            {
              "count": 1,
              "key": "Demo_Course",
              "label": "Demo_Course"
            }
          ]
        },
        "course": {
          "facet": {
            "key": "course",
            "label": "Course"
          },
          "values": [
            {
              "count": 2,
              "key": "8.01",
              "label": "8.01"
            },
            {
              "count": 1,
              "key": "DemoX",
              "label": "DemoX"
            }
          ]
        },
        "7": {
          "facet": {
            "missing_count": 3,
            "key": "7",
            "label": "new12"
          },
          "values": []
        },
        "6": {
          "facet": {
            "missing_count": 2,
            "key": "6",
            "label": "new1"
          },
          "values": [
            {
              "count": 1,
              "key": "2",
              "label": "t1"
            }
          ]
        },
        "8": {
          "facet": {
            "missing_count": 3,
            "key": "8",
            "label": "new5"
          },
          "values": []
        },
        "resource_type": {
          "facet": {
            "key": "resource_type",
            "label": "Item Type"
          },
          "values": [
            {
              "count": 2,
              "key": "course",
              "label": "course"
            },
            {
              "count": 1,
              "key": "chapter",
              "label": "chapter"
            }
          ]
        }
      },
      "selected_facets": {
        "run": {},
        "course": {},
        "7": {},
        "6": {},
        "8": {},
        "resource_type": {}
      },
      "selected_missing_facets": {}
    };
    var searchResponseCourseFacet = {
      "count": 2,
      "next": null,
      "previous": null,
      "results": [
        {
          "resource_type": "course",
          "course": "8.01",
          "run": "2014_Fall",
          "xa_nr_views": 0,
          "xa_nr_attempts": 0,
          "xa_avg_grade": 0.0,
          "id": 1,
          "title": "MISSING",
          "description": "",
          "description_path": "MISSING",
          "preview_url": "..."
        },
        {
          "resource_type": "chapter",
          "course": "8.01",
          "run": "2014_Fall",
          "xa_nr_views": 0,
          "xa_nr_attempts": 0,
          "xa_avg_grade": 0.0,
          "id": 2,
          "title": "Course Information",
          "description": "",
          "description_path": "MISSING / Course Information",
          "preview_url": "..."
        }
      ],
      "facet_counts": {
        "run": {
          "facet": {
            "key": "run",
            "label": "Run"
          },
          "values": [
            {
              "count": 2,
              "key": "2014_Fall",
              "label": "2014_Fall"
            }
          ]
        },
        "course": {
          "facet": {
            "key": "course",
            "label": "Course"
          },
          "values": [
            {
              "count": 2,
              "key": "8.01",
              "label": "8.01"
            }
          ]
        },
        "7": {
          "facet": {
            "missing_count": 2,
            "key": "7",
            "label": "new12"
          },
          "values": []
        },
        "6": {
          "facet": {
            "missing_count": 1,
            "key": "6",
            "label": "new1"
          },
          "values": [
            {
              "count": 1,
              "key": "2",
              "label": "t1"
            }
          ]
        },
        "8": {
          "facet": {
            "missing_count": 2,
            "key": "8",
            "label": "new5"
          },
          "values": []
        },
        "resource_type": {
          "facet": {
            "key": "resource_type",
            "label": "Item Type"
          },
          "values": [
            {
              "count": 1,
              "key": "course",
              "label": "course"
            },
            {
              "count": 1,
              "key": "chapter",
              "label": "chapter"
            }
          ]
        }
      },
      "selected_facets": {
        "run": {},
        "course": {
          "8.01": true
        },
        "7": {},
        "6": {},
        "8": {},
        "resource_type": {}
      },
      "selected_missing_facets": {}
    };
    var vocabularyResponse = {
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
        }]
    };
    var membersResponse = {
      "count": 1,
      "next": null,
      "previous": null,
      "results": [
        {
          "username": "root",
          "group_type": "administrators"
        }
      ]
    };
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

    // Substituted in for window.location
    var queryString;
    var updateQueryString = function (query) {
      queryString = query;
    };
    var getQueryString = function () {
      return queryString;
    };

    QUnit.module('Tests for listing page', {
      beforeEach: function() {
        TestUtils.setup();
        TestUtils.initMockjax({
          url: '/api/v1/repositories/test/search/',
          type: 'GET',
          responseText: searchResponseAll
        });
        TestUtils.initMockjax({
          url: '/api/v1/repositories/test/search/' +
          '?selected_facets=course_exact%3A8.01',
          type: 'GET',
          responseText: searchResponseCourseFacet
        });
        TestUtils.initMockjax({
          url: "/api/v1/learning_resource_types/",
          contentType: "application/json; charset=utf-8",
          responseText: learningResourceTypes,
          dataType: 'json',
          type: "GET"
        });
        TestUtils.initMockjax({
          url: "/api/v1/repositories/test/vocabularies/",
          contentType: "application/json; charset=utf-8",
          responseText: vocabularyResponse,
          dataType: 'json',
          type: "GET"
        });
        TestUtils.initMockjax({
          url: "/api/v1/repositories/test/members/",
          contentType: "application/json; charset=utf-8",
          responseText: membersResponse,
          dataType: 'json',
          type: 'GET'
        });

        $("body").append($(
          "<div id='listing_container'>" +
            "<div id='listing' />" +
            "<div id='exports_content' />" +
            "<div id='exports_heading' />" +
            "<div id='tab-1' />" +
            "<div id='tab-2' />" +
            "<div id='tab-3' />" +
            "<div id='lore-pagination' />" +
            "<div id='taxonomy-component' />" +
            "<div id='members-alert' />" +
            "<button class='btn-taxonomies' />" +
            "<button class='btn-members' />" +
            "<div class='cd-panel' />" +
            "<div class='cd-panel-2' />" +
            "<div class='cd-panel-exports'>" +
            "<a href='#' class='cd-panel-close' />" +
            "</div>" +
            "<div class='cd-panel-members' " +
            "data-members-url='/api/v1/repositories/test/members/' />" +
            "<button id='search_button' />" +
            "<a href='#tab-1' />" +
            "<a href='#tab-2' />" +
            "<a href='#tab-3' />" +
            "<a href='#tab-vocab' />" +
            "<a href='#tab-taxonomies' />" +
            "<input type='text' id='id_q' />" +
          "</div>"));

        queryString = "";
      },
      afterEach: function() {
        TestUtils.cleanup();

        $("#listing_container").remove();
      }
    });

    var listingOptions = {
      repoSlug: "test",
      resources: [{
        "run": "Demo_Course",
        "description": "",
        "course": "DemoX",
        "xa_avg_grade": 0.0,
        "id": 1,
        "title": "Open edX Demonstration Course",
        "description_path": "Open edX Demonstration Course",
        "xa_nr_views": 0,
        "preview_url": "...",
        "xa_nr_attempts": 0,
        "resource_type": "course"
      }, {
        "run": "Demo_Course",
        "description": "another description",
        "course": "DemoX",
        "xa_avg_grade": 0.0,
        "id": 2,
        "title": "Introduction",
        "description_path": "Open edX Demonstration Course / Introduction",
        "xa_nr_views": 0,
        "preview_url": "...",
        "xa_nr_attempts": 0,
        "resource_type": "chapter"
      }],
      allExports: [2],
      sortingOptions: {
        "current": ["nr_views", "Number of Views (desc)"],
        "all": [
          ["nr_attempts", "Number of Attempts (desc)"],
          ["avg_grade", "Average Grade (desc)"]
        ]
      },
      loggedInUsername: "test",
      qsPrefix: "?",
      imageDir: "/base/ui/static/ui/images",
      facetCounts: {
        "run": {
          "facet": {"key": "run", "label": "Run"},
          "values": [{
            "count": 139,
            "key": "Demo_Course",
            "label": "Demo_Course"
          }]
        },
        "course": {
          "facet": {"key": "course", "label": "Course"},
          "values": [{"count": 139, "key": "DemoX", "label": "DemoX"}]
        },
        "resource_type": {
          "facet": {"key": "resource_type", "label": "Item Type"},
          "values": [{
            "count": 39,
            "key": "vertical",
            "label": "vertical"
          }]
        }
      }
    };

    QUnit.test('Assert taxonomy tab opens', function(assert) {
      Listing.loader(listingOptions, $("#listing")[0]);
      var done = assert.async();
      waitForAjax(1, function() {
        assert.ok(!$('.cd-panel-2').hasClass("is-visible"));

        // click Manage Taxonomies button
        $(".btn-taxonomies").click();
        assert.ok($('.cd-panel-2').hasClass("is-visible"));
        waitForAjax(2, function() {
          // Press escape to close
          var press = $.Event("keyup");
          press.keyCode = 27;
          $(document).trigger(press);
          assert.ok(!$('.cd-panel-2').hasClass("is-visible"));
          done();
        });
      });
    });

    QUnit.test('Assert members tab opens', function(assert) {
      var done = assert.async();
      Listing.loader(listingOptions, $("#listing")[0]);
      waitForAjax(1, function() {
        assert.ok(!$('.cd-panel-members').hasClass("is-visible"));

        // click Members button
        $(".btn-members").click();
        assert.ok($('.cd-panel-members').hasClass("is-visible"));
        waitForAjax(1, function() {
          // Press escape to close
          var press = $.Event("keyup");
          press.keyCode = 27;
          $(document).trigger(press);
          assert.ok(!$('.cd-panel-members').hasClass("is-visible"));
          done();
        });
      });
    });

    QUnit.test("Assert facet checkboxes",
      function(assert) {
        var done = assert.async();

        var afterMount = function(component) {
          var container = React.findDOMNode(component);
          waitForAjax(1, function() {
            assert.equal(queryString, "");
            assert.equal(
              component.state.resources.length,
              searchResponseAll.count
            );

            // Select course facet
            $(container).find("ins").first().click();
            waitForAjax(1, function() {
              assert.equal(
                queryString,
                "?selected_facets=course_exact%3A8.01"
              );
              assert.equal(
                component.state.resources.length,
                searchResponseCourseFacet.count
              );

              $(container).find("ins").first().click();
              waitForAjax(1, function() {
                // Note lack of '?'
                assert.equal(queryString, "");
                assert.equal(
                  component.state.resources.length,
                  searchResponseAll.count
                );
                done();
              });
            });
          });

        };

        var options = {
          allExports: listingOptions.allExports,
          sortingOptions: listingOptions.sortingOptions,
          imageDir: listingOptions.imageDir,
          pageSize: 25,
          repoSlug: listingOptions.repoSlug,
          loggedInUsername: listingOptions.loggedInUsername,
          updateQueryString: updateQueryString,
          getQueryString: getQueryString,
          ref: afterMount
        };

        React.addons.TestUtils.renderIntoDocument(
          React.createElement(Listing.ListingContainer, options)
        );
      }
    );

    QUnit.test("Check sorting options", function(assert) {
      var done = assert.async();

      // Note that results here are not meaningful
      TestUtils.initMockjax({
        url: '/api/v1/repositories/test/search/' +
          '?selected_facets=course_exact%3A8.01&' +
          'selected_facets=run_exact%3A2014_Fall',
        type: 'GET',
        responseText: searchResponseAll
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/test/search/' +
          '?selected_facets=course_exact%3A8.01&' +
          'selected_facets=run_exact%3A2014_Fall&' +
          'sortby=avg_grade',
        type: 'GET',
        responseText: searchResponseAll
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/test/search/?sortby=avg_grade&q=text',
        type: 'GET',
        responseText: searchResponseAll
      });

      var afterMount = function (component) {
        var node = React.findDOMNode(component);

        waitForAjax(1, function () {
          // Select course facet
          $(node).find("ins").first().click();
          waitForAjax(1, function () {
            assert.equal(queryString, "?selected_facets=course_exact%3A8.01");

            // Select second course facet.
            // Checkboxes change between refreshes but that won't matter here.
            // This will make sure we can handle two checkboxes.
            $($(node).find("ins")[1]).click();
            waitForAjax(1, function() {
              assert.equal(
                queryString,
                "?selected_facets=course_exact%3A8.01&" +
                "selected_facets=run_exact%3A2014_Fall"
              );

              // Sort by title
              React.addons.TestUtils.Simulate.click(
                $(node).find("a:contains('Average')")[0]
              );
              waitForAjax(1, function() {
                assert.equal(
                  queryString,
                  "?selected_facets=course_exact%3A8.01&" +
                  "selected_facets=run_exact%3A2014_Fall&" +
                  "sortby=avg_grade"
                );

                // Filter by text
                $("#id_q").val("text");
                $("#search_button").click();
                waitForAjax(1, function() {
                  // Sort was kept but facets were lost
                  assert.equal(queryString, "?sortby=avg_grade&q=text");

                  done();
                });
              });
            });
          });
        });
      };

      var options = {
        allExports: listingOptions.allExports,
        sortingOptions: listingOptions.sortingOptions,
        imageDir: listingOptions.imageDir,
        pageSize: 25,
        repoSlug: listingOptions.repoSlug,
        loggedInUsername: listingOptions.loggedInUsername,
        updateQueryString: updateQueryString,
        getQueryString: getQueryString,
        ref: afterMount
      };

      React.addons.TestUtils.renderIntoDocument(
        React.createElement(Listing.ListingContainer, options)
      );
    });

    QUnit.test("Test pagination", function(assert) {
      var done = assert.async();
      var pageSize = 2;

      var afterMount = function(component) {
        // Initial state
        assert.equal(
          component.state.numPages,
          0
        );
        waitForAjax(1, function() {
          assert.equal(
            component.state.numPages,
            Math.ceil(searchResponseAll.count / pageSize)
          );
          done();
        });
      };

      var options = {
        allExports: listingOptions.allExports,
        sortingOptions: listingOptions.sortingOptions,
        imageDir: listingOptions.imageDir,
        pageSize: pageSize,
        repoSlug: listingOptions.repoSlug,
        loggedInUsername: listingOptions.loggedInUsername,
        updateQueryString: updateQueryString,
        getQueryString: getQueryString,
        ref: afterMount
      };

      React.addons.TestUtils.renderIntoDocument(
        React.createElement(Listing.ListingContainer, options)
      );

    });

    QUnit.test("Assert search textbox", function (assert) {
      var done = assert.async();

      // This is a failure but shouldn't affect changing of query string
      TestUtils.initMockjax({
        url: '/api/v1/repositories/test/search/?q=text+with+spaces',
        type: 'GET',
        responseText: searchResponseCourseFacet,
        status: 400
      });

      var afterMount = function (component) {
        waitForAjax(1, function () {
          assert.equal(queryString, "");
          assert.equal(
            component.state.resources.length,
            searchResponseAll.count
          );

          // Set search text
          $("#id_q").val("text with spaces");
          $("#search_button").click();
          waitForAjax(1, function () {
            assert.equal(queryString, "?q=text+with+spaces");
            assert.equal(
              component.state.resources.length,
              searchResponseAll.count
            );

            $("#id_q").val("");
            $("#search_button").click();
            waitForAjax(1, function () {
              // Note lack of '?'
              assert.equal(queryString, "");
              assert.equal(
                component.state.resources.length,
                searchResponseAll.count
              );
              done();
            });
          });
        });
      };

      var options = {
        allExports: listingOptions.allExports,
        sortingOptions: listingOptions.sortingOptions,
        imageDir: listingOptions.imageDir,
        pageSize: 25,
        repoSlug: listingOptions.repoSlug,
        loggedInUsername: listingOptions.loggedInUsername,
        updateQueryString: updateQueryString,
        getQueryString: getQueryString,
        ref: afterMount
      };

      React.addons.TestUtils.renderIntoDocument(
        React.createElement(Listing.ListingContainer, options)
      );
    });

    QUnit.test('Assert loader behavior', function(assert) {
      var done = assert.async();

      // Success on initial load but fail after clicking checkbox
      TestUtils.replaceMockjax({
        url: '/api/v1/repositories/test/search/' +
        '?selected_facets=course_exact%3A8.01',
        type: 'GET',
        responseText: searchResponseCourseFacet,
        status: 400
      });

      var afterMount = function (component) {
        var container = React.findDOMNode(component);
        assert.equal(component.state.pageLoaded, false);
        waitForAjax(1, function () {
          assert.equal(component.state.pageLoaded, true);

          // Select course facet
          $(container).find("ins").first().click();
          component.forceUpdate(function() {
            assert.equal(component.state.pageLoaded, false);
            waitForAjax(1, function () {
              assert.equal(component.state.pageLoaded, true);
              done();
            });
          });
        });

      };

      var options = {
        allExports: listingOptions.allExports,
        sortingOptions: listingOptions.sortingOptions,
        imageDir: listingOptions.imageDir,
        pageSize: 25,
        repoSlug: listingOptions.repoSlug,
        loggedInUsername: listingOptions.loggedInUsername,
        updateQueryString: updateQueryString,
        getQueryString: getQueryString,
        ref: afterMount
      };

      React.addons.TestUtils.renderIntoDocument(
        React.createElement(Listing.ListingContainer, options)
      );
    });

    QUnit.test('Check isEmail', function(assert) {
      assert.ok(Listing.isEmail("staff@edx.org"));
      assert.ok(Listing.isEmail("staff@mit.edu"));
      assert.ok(!Listing.isEmail("@mit.edu"));
      assert.ok(!Listing.isEmail("other"));
    });

    QUnit.test('Assert resource tab lazy loading', function(assert) {
      var done = assert.async();

      TestUtils.initMockjax({
        url: '/api/v1/repositories/test/learning_resources/' +
          '1/?remove_content_xml=true',
        type: 'GET',
        responseText: learningResourceResponseMinusContentXml
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/test/learning_resources/1/',
        type: 'GET',
        responseText: learningResourceResponse
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/test/vocabularies/?type_name=course',
        type: 'GET',
        responseText: vocabularyResponse
      });
      var afterMount = function(component) {
        var node = React.findDOMNode(component);
        waitForAjax(1, function() {
          React.addons.TestUtils.Simulate.click(
            $(node).find("h2 .cd-btn")[0]
          );

          waitForAjax(2, function() {
            assert.equal(component.state.currentResourceId, 1);
            assert.deepEqual(
              component.state.loadedPanels,
              {"tab-1": true}
            );

            $("a[href='#tab-2']").click();
            waitForAjax(1, function() {
              assert.deepEqual(
                component.state.loadedPanels,
                {
                  "tab-1": true,
                  "tab-2": true
                }
              );
              done();
            });
          });
        });
      };

      var options = {
        allExports: listingOptions.allExports,
        sortingOptions: listingOptions.sortingOptions,
        imageDir: listingOptions.imageDir,
        pageSize: 25,
        repoSlug: listingOptions.repoSlug,
        loggedInUsername: listingOptions.loggedInUsername,
        updateQueryString: updateQueryString,
        getQueryString: getQueryString,
        ref: afterMount
      };

      React.addons.TestUtils.renderIntoDocument(
        React.createElement(Listing.ListingContainer, options)
      );
    });

    QUnit.test('Open and close exports panel', function(assert) {
      var done = assert.async();

      TestUtils.initMockjax({
        url: '/api/v1/repositories/test/learning_resource_exports/test/',
        type: 'GET',
        responseText: {
          "count": 1,
          "next": null,
          "previous": null,
          "results": [{"id": 123}]
        }
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/test/learning_resources/?id=123',
        type: 'GET',
        responseText: {
          "count": 1,
          "next": null,
          "previous": null,
          "results": [
            learningResourceResponse
          ]
        }
      });
      var afterMount = function(component) {
        var node = React.findDOMNode(component);
        waitForAjax(1, function() {
          assert.ok(!$('.cd-panel-exports').hasClass("is-visible"));
          React.addons.TestUtils.Simulate.click(
            $(node).find("button:contains('Export')")[0]
          );
          waitForAjax(2, function() {

            assert.ok($('.cd-panel-exports').hasClass("is-visible"));

            $(".cd-panel-exports .cd-panel-close").click();
            assert.ok(!$('.cd-panel-exports').hasClass("is-visible"));

            done();
          });
        });
      };

      var options = {
        allExports: listingOptions.allExports,
        sortingOptions: listingOptions.sortingOptions,
        imageDir: listingOptions.imageDir,
        pageSize: 25,
        repoSlug: listingOptions.repoSlug,
        loggedInUsername: listingOptions.loggedInUsername,
        updateQueryString: updateQueryString,
        getQueryString: getQueryString,
        ref: afterMount
      };

      React.addons.TestUtils.renderIntoDocument(
        React.createElement(Listing.ListingContainer, options)
      );

    });

    QUnit.test('Open and close learning resource panel', function(assert) {
      var done = assert.async();
      TestUtils.initMockjax({
        url: '/api/v1/repositories/test/learning_resources/' +
        '1/?remove_content_xml=true',
        type: 'GET',
        responseText: learningResourceResponse
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/test/vocabularies/?type_name=course',
        type: 'GET',
        responseText: vocabularyResponse
      });

      var afterMount = function(component) {
        waitForAjax(1, function() {
          assert.notOk($('.cd-panel').hasClass("is-visible"));
          component.openResourcePanel(1);
          waitForAjax(2, function() {
            assert.equal(component.state.currentResourceId , 1);
            assert.ok($('.cd-panel').hasClass("is-visible"));
            component.setState({
              isLearningResourcePanelDirty: true
            }, function () {
              component.closeLearningResourcePanel();
              assert.ok($('.cd-panel').hasClass("is-visible"),
                "LR Panel should not close because it is marked dirty");
              component.setState({
                isLearningResourcePanelDirty: false
              }, function() {
                component.closeLearningResourcePanel();
                assert.notOk($('.cd-panel').hasClass("is-visible"),
                  "LR Panel should close");
                done();
              });
            });
          });
        });
      };

      var options = {
        allExports: listingOptions.allExports,
        sortingOptions: listingOptions.sortingOptions,
        imageDir: listingOptions.imageDir,
        pageSize: 25,
        repoSlug: listingOptions.repoSlug,
        loggedInUsername: listingOptions.loggedInUsername,
        updateQueryString: updateQueryString,
        getQueryString: getQueryString,
        showConfirmationDialog: function() {},
        ref: afterMount
      };

      React.addons.TestUtils.renderIntoDocument(
        React.createElement(Listing.ListingContainer, options)
      );
    });
  }
);
