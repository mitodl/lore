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
          "lid": 1,
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
          "lid": 2,
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
          "lid": 1375,
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
          "lid": 1,
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
          "lid": 2,
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

        $("body").append($("<div id='listing_container'>" +
          "<div id='listing'></div>" +
            "<div id='exports_content'></div>" +
            "<div id='exports_heading'></div>" +
            "<div id='tab-1'></div>" +
            "<div id='tab-3'></div>" +
            "<div id='lore-pagination'></div>" +
            "<div id='taxonomy-component'></div>" +
            "<div class='btn-taxonomies'></div>" +
            "<div class='btn-members'></div>" +
            "<div class='cd-panel'></div>" +
            "<div class='cd-panel-2'></div>" +
            "<div class='cd-panel-exports'></div>" +
            "<div class='cd-panel-members'></div>" +
          "</div>"));
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
        "lid": 1,
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
        "lid": 2,
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
      waitForAjax(3, function() {
        assert.ok(!$('.cd-panel-2').hasClass("is-visible"));

        // click Manage Taxonomies button
        $(".btn-taxonomies").click();
        assert.ok($('.cd-panel-2').hasClass("is-visible"));

        // Press escape to close
        var press = $.Event("keyup");
        press.keyCode = 27;
        $(document).trigger(press);
        assert.ok(!$('.cd-panel-2').hasClass("is-visible"));
        done();
      });
    });

    QUnit.test('Assert members tab opens', function(assert) {
      var done = assert.async();
      Listing.loader(listingOptions, $("#listing")[0]);
      waitForAjax(3, function() {
        assert.ok(!$('.cd-panel-members').hasClass("is-visible"));

        // click Members button
        $(".btn-members").click();
        assert.ok($('.cd-panel-members').hasClass("is-visible"));

        // Press escape to close
        var press = $.Event("keyup");
        press.keyCode = 27;
        $(document).trigger(press);
        assert.ok(!$('.cd-panel-members').hasClass("is-visible"));
        done();
      });
    });

    QUnit.test("Assert that lone query strings don't have a question mark",
      function(assert) {
        var done = assert.async();

        var oldLocation = window.location.toString();
        var container = $("#listing")[0];
        Listing.loader(listingOptions, container);

        // NOTE: after manage taxonomy PR is merged this will change.
        waitForAjax(3, function() {
          assert.equal(window.location.toString(), oldLocation);

          // Select course facet
          $(container).find("ins").first().click();
          waitForAjax(1, function() {
            assert.equal(
              window.location.toString(),
              oldLocation + "?selected_facets=course_exact%3A8.01"
            );

            $(container).find("ins").first().click();
            waitForAjax(1, function() {
              // Note lack of '?'
              assert.equal(window.location.toString(), oldLocation);
              done();
            });
          });
        });

      }
    );
  }
);
