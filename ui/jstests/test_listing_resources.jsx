define(['QUnit', 'jquery', 'listing_resources', 'react',
    'test_utils', 'lodash'],
  function (QUnit, $, ListingResources, React, TestUtils, _) {
    'use strict';

    var imageRoot = "/base/ui/static/ui/images";

    var Listing = ListingResources.Listing;
    var ListingResource = ListingResources.ListingResource;
    var SortingDropdown = ListingResources.SortingDropdown;
    var loader = ListingResources.loader;
    var getImageFile = ListingResources.getImageFile;

    var waitForAjax = TestUtils.waitForAjax;

    // This is mostly filler, we test facets in more detail in test_facets.jsx
    var emptyFacetCounts = {
      "run": {
        "facet": {"key": "run", "label": "Run"},
        "values": []
      },
      "1": {"facet": {"key": "1", "label": "a"}, "values": []},
      "course": {"facet": {"key": "course", "label": "Course"}, "values": []},
      "3": {"facet": {"key": "3", "label": "s"}, "values": []},
      "2": {"facet": {"key": "2", "label": "run"}, "values": []},
      "5": {"facet": {"key": "5", "label": "disallowmultiple"}, "values": []},
      "4": {"facet": {"key": "4", "label": "allowmulti"}, "values": []},
      "7": {"facet": {"key": "7", "label": "infinite"}, "values": []},
      "6": {"facet": {"key": "6", "label": "one"}, "values": []},
      "8": {"facet": {"key": "8", "label": "free"}, "values": []},
      "resource_type": {
        "facet": {"key": "resource_type", "label": "Item Type"},
        "values": []
      }
    };

    var sampleResources = [{
      "run": "2015_Summer",
      "description": "Description A",
      "course": "0.001",
      "xa_avg_grade": 68.0,
      "lid": 23,
      "title": "Circuit Schematic Builder",
      "description_path": "Ops / Content/problem tests / Sample problems" +
      " / Circuit schematic builder / Circuit Schematic Builder",
      "xa_nr_views": 9755,
      "preview_url": "https://www.sandbox.edx.org/courses/DevOps/0.001/" +
      "2015_Summer/jump_to_id/71101093d5234c8a87488ed9a27db531",
      "xa_nr_attempts": 717,
      "resource_type": "problem"
    }, {
      "run": "2015_Summer",
      "description": "Description B",
      "course": "0.001",
      "xa_avg_grade": 75.0,
      "lid": 45,
      "title": "LTI",
      "description_path": "Ops / LTI",
      "xa_nr_views": 8185,
      "preview_url": "https://www.sandbox.edx.org/courses/DevOps/0.001/" +
      "2015_Summer/jump_to_id/c8ce33eb31e3477a817baaa25f401926",
      "xa_nr_attempts": 126,
      "resource_type": "chapter"
    }];

    var allExports = [45];
    var sortingOptions = {
      "current": ["nr_views", "Number of Views (desc)"],
      "all": [
        ["nr_attempts", "Number of Attempts (desc)"],
        ["avg_grade", "Average Grade (desc)"]
      ]
    };

    var listingOptions = {
      repoSlug: "test",
      resources: sampleResources,
      allExports: allExports,
      sortingOptions: sortingOptions,
      loggedInUsername: "user",
      qsPrefix: "qs",
      imageDir: imageRoot,
      facetCounts: emptyFacetCounts
    };

    // NOTE: these tests will show 404 for /images/*.png due to these
    // files not being served. We can't mock them since they aren't
    // jQuery AJAX calls so we have to just ignore it for now.
    QUnit.module('Test listing resources', {
      beforeEach: function () {
        TestUtils.setup();

        TestUtils.initMockjax({
          url: '/api/v1/repositories/test/learning_resource_exports/user/',
          type: 'POST',
          status: 200
        });
        TestUtils.initMockjax({
          url: '/api/v1/repositories/test/learning_resource_exports/user/45/',
          type: 'DELETE',
          status: 204
        });
      },
      afterEach: function() {
        TestUtils.cleanup();
      }
    });

    QUnit.test('Assert that loader does something', function(assert) {
      var div = document.createElement("div");
      assert.equal($(div).find("div").size(), 0);
      loader(listingOptions, div, function() {}, function() {});
      assert.ok($(div).find("div").size() > 0);
    });

    QUnit.test('Assert export links and count', function(assert) {
      var done = assert.async();
      var afterMount = function(component) {
        assert.deepEqual(component.state, {
          exportSelection: {
            23: false,
            45: true
          }
        });
        var node = React.findDOMNode(component);
        assert.equal($(node).find(".btn-primary .badge").text(), 1);

        // Click each export link to flip the values.
        _.each($(node).find(".link-export"), function(link) {
          React.addons.TestUtils.Simulate.click(link);
        });
        waitForAjax(2, function () {
          component.forceUpdate(function () {
            assert.deepEqual(component.state, {
              exportSelection: {
                23: true,
                45: false
              }
            });
            assert.equal($(node).find(".btn-primary .badge").text(), 1);

            // Remove 45 from state, this should make Listing
            // assume that 45 is true from its presence in allExports,
            // increasing count to 2.
            component.setState({exportSelection: {23: true}});
            component.forceUpdate(function() {
              assert.equal($(node).find(".btn-primary .badge").text(), 2);

              // Set all exports to false, verify export badge is not present.
              component.setState({exportSelection: {
                23: false,
                45: false
              }});
              component.forceUpdate(function() {
                assert.equal($(node).find(".btn-primary .badge").text(), "");

                done();
              });
            });
          });
        });
      };

      React.addons.TestUtils.renderIntoDocument(
        <Listing {...listingOptions}
          openExportsPanel={function() {}}
          openResourcePanel={function() {}}
          ref={afterMount}
          />
      );
    });

    QUnit.test('Assert export button and resource links', function(assert) {
      var done = assert.async();

      var openExportsPanelCalled = 0;
      var openExportsPanel = function() {
        openExportsPanelCalled++;
      };

      var openResourcePanelCalled = {};
      var openResourcePanel = function(lid) {
        openResourcePanelCalled[lid] = true;
      };

      var afterMount = function(component) {
        var node = React.findDOMNode(component);
        var exportButton = $(node).find(".btn:contains('Export')")[0];

        assert.equal(openExportsPanelCalled, 0);
        React.addons.TestUtils.Simulate.click(exportButton);
        assert.equal(openExportsPanelCalled, 1);

        assert.deepEqual(openResourcePanelCalled, {});
        _.each($(node).find(".tile-content h2 a"), function(link) {
          React.addons.TestUtils.Simulate.click(link);
        });
        assert.deepEqual(openResourcePanelCalled, {
          23: true,
          45: true
        });

        done();
      };

      React.addons.TestUtils.renderIntoDocument(
        <Listing {...listingOptions}
          openExportsPanel={openExportsPanel}
          openResourcePanel={openResourcePanel}
          ref={afterMount}
          />
      );
    });

    QUnit.test('Assert sorting options', function(assert) {
      var done = assert.async();
      var afterMount = function(component) {
        var node = React.findDOMNode(component);

        var $buttonGroup = $(node).find(".btn-group");
        assert.equal(
          $buttonGroup.find("button").first().text(),
          sortingOptions.current[1]
        );
        var sortText = _.map($(node).find(".dropdown-menu li a"),
          function(link) {
            return $(link).text();
          }
        );
        assert.deepEqual(sortText, _.map(sortingOptions.all, function(option) {
          return option[1];
        }));

        done();
      };

      React.addons.TestUtils.renderIntoDocument(
        <SortingDropdown
          sortingOptions={sortingOptions}
          qsPrefix="?"
          repoSlug="test"
          ref={afterMount}
          />
      );
    });

    QUnit.test('Assert rendering of ListingResource',
      function(assert) {
        var done = assert.async();

        var resource = sampleResources[1];
        var openResourcePanelCount = {};
        var openResourcePanel = function(lid) {
          openResourcePanelCount[lid] = true;
        };

        var updateExportLinkClickCount = {};
        var updateExportLinkClick = function(lid, selected) {
          updateExportLinkClickCount[lid] = selected;
        };

        var afterMount = function(component) {
          // ListingResource has no state
          assert.equal(null, component.state);

          // Assert link behavior
          var node = React.findDOMNode(component);
          assert.deepEqual(openResourcePanelCount, {});
          var resourceLink = $(node).find("h2 a")[0];
          React.addons.TestUtils.Simulate.click(resourceLink);
          assert.equal(openResourcePanelCount[resource.lid], true);

          assert.deepEqual(updateExportLinkClickCount, {});
          var exportLink = $(node).find(".link-export")[0];
          React.addons.TestUtils.Simulate.click(exportLink);
          assert.equal(updateExportLinkClickCount[resource.lid], false);

          var $firstRow = $(node).find("h2");
          var $secondRow = $(node).find(".tile-meta").first();
          var $thirdRow = $(node).find(".tile-blurb");
          var $lastRow = $($(node).find(".tile-meta")[1]);

          // Title link
          assert.equal(resource.title, $firstRow.find("a").text());
          assert.equal(resource.lid,
            $firstRow.find("a").data("learningresource-id"));

          // Description path
          assert.equal(resource.description_path, $secondRow.text());

          // Description
          assert.equal(resource.description, $thirdRow.text());

          // Course and run
          assert.equal(resource.course,
            $($lastRow.find(".meta-item")[0]).text());
          assert.equal(resource.run,
            $($lastRow.find(".meta-item")[1]).text());

          // Xanalytics
          assert.equal(resource.xa_nr_views,
            $lastRow.find(".mi-col-1").text());
          assert.equal(resource.xa_nr_attempts,
            $lastRow.find(".mi-col-2").text());
          assert.equal(resource.xa_avg_grade,
            $lastRow.find(".mi-col-3").text());

          // Assert preview link href
          assert.equal(resource.preview_url,
            $lastRow.find("a[target='_blank']").attr('href'));

          done();
        };

        React.addons.TestUtils.renderIntoDocument(
          <ListingResource
            resource={resource}
            exportSelected={_.includes(listingOptions.allExports, resource.lid)}
            imageDir={listingOptions.imageDir}
            repoSlug={listingOptions.repoSlug}
            openResourcePanel={openResourcePanel}
            updateExportLinkClick={updateExportLinkClick}
            ref={afterMount}
            />
        );
      }
    );

    QUnit.test('Assert getImageFile', function(assert) {
      assert.equal(getImageFile('chapter'), 'ic-book.png');
      assert.equal(getImageFile('sequential'), 'ic-sequential.png');
      assert.equal(getImageFile('vertical'), 'ic-vertical.png');
      assert.equal(getImageFile('problem'), 'ic-pieces.png');
      assert.equal(getImageFile('video'), 'ic-video.png');
      assert.equal(getImageFile('some other value'), 'ic-code.png');
    });

    QUnit.test('Assert export button visibility', function(assert) {

      var listingOptionsWithoutExports = $.extend({}, listingOptions);
      listingOptionsWithoutExports.allExports = [];

      var doneFalse = assert.async();
      var afterMountFalse = function(component) {
        var node = React.findDOMNode(component);
        var $exportBadge = $(node).find(".btn:contains('Export') .badge");
        assert.equal($exportBadge.size(), 0);

        doneFalse();
      };

      React.addons.TestUtils.renderIntoDocument(
        <Listing {...listingOptionsWithoutExports}
          ref={afterMountFalse} />
      );

      var doneTrue = assert.async();
      var afterMountTrue = function(component) {
        var node = React.findDOMNode(component);
        var $exportBadge = $(node).find(".btn:contains('Export') .badge");
        assert.equal($exportBadge.text(), "1");

        doneTrue();
      };

      React.addons.TestUtils.renderIntoDocument(
        <Listing {...listingOptions}
          ref={afterMountTrue} />
      );
    });
  }
);
