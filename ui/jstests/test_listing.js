define(['QUnit', 'jquery', 'react', 'test_utils', 'utils', 'listing'],
  function(QUnit, $, React, TestUtils, Utils, Listing) {
    'use strict';
    QUnit.module('Tests for listing page', {
      beforeEach: function() {
        TestUtils.setup();

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
      Listing.loader(listingOptions, 1, 2, $("#listing")[0]);
      assert.ok(!$('.cd-panel-2').hasClass("is-visible"));

      // click Manage Taxonomies button
      $(".btn-taxonomies").click();
      assert.ok($('.cd-panel-2').hasClass("is-visible"));

      // Press escape to close
      var press = $.Event("keyup");
      press.keyCode = 27;
      $(document).trigger(press);
      assert.ok(!$('.cd-panel-2').hasClass("is-visible"));
    });

    QUnit.test('Assert members tab opens', function(assert) {
      Listing.loader(listingOptions, 1, 2, $("#listing")[0]);
      assert.ok(!$('.cd-panel-members').hasClass("is-visible"));

      // click Members button
      $(".btn-members").click();
      assert.ok($('.cd-panel-members').hasClass("is-visible"));

      // Press escape to close
      var press = $.Event("keyup");
      press.keyCode = 27;
      $(document).trigger(press);
      assert.ok(!$('.cd-panel-members').hasClass("is-visible"));
    });
  }
);
