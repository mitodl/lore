define(['QUnit', 'jquery', 'listing_resources', 'react',
    'test_utils', 'lodash'],
  function (QUnit, $, ListingResources, React, TestUtils, _) {
    'use strict';

    var facetCounts = {
      "1": {
        "facet": {"key": "1", "label": "a"},
        "values": [
          {"count": 2, "key": "1", "label": "t1"},
          {"count": 2, "key": "2", "label": "t2"}
        ]
      },
      "2": {
        "facet": {
          "key": "2",
          "label": "run"
        },
        "values": []
      },
      "3": {
        "facet": {
          "key": "3",
          "label": "s"
        },
        "values": []
      },
      "4": {
        "facet": {
          "key": "4",
          "label": "allowmulti"
        },
        "values": [
          {"count": 4, "key": "6", "label": "term1"},
          {"count": 4, "key": "7", "label": "term2"}
        ]
      },
      "5": {
        "facet": {
          "key": "5",
          "label": "disallowmultiple"
        },
        "values": [
          {"count": 2, "key": "8", "label": "term3"},
          {"count": 2, "key": "9", "label": "term4"}
        ]
      },
      "6": {
        "facet": {
          "key": "6",
          "label": "one"
        },
        "values": []
      },
      "7": {
        "facet": {
          "key": "7",
          "label": "infinite"
        },
        "values": []
      },
      "8": {
        "facet": {
          "key": "8",
          "label": "free"
        },
        "values": [
          {"count": 1, "key": "12", "label": "tagging"},
          {"count": 1, "key": "13", "label": "tagging with spaces"}
        ]
      },
      "course": {
        "facet": {
          "key": "course",
          "label": "Course"
        },
        "values": [
          {"count": 47, "key": "0.001", "label": "0.001"},
          {"count": 43, "key": "MIT.latex2edx", "label": "MIT.latex2edx"}
        ]
      },
      "resource_type": {
        "facet": {
          "key": "resource_type",
          "label": "Item Type"
        },
        "values": [
          {"count": 35, "key": "problem", "label": "problem"},
          {"count": 30, "key": "vertical", "label": "vertical"},
          {"count": 12, "key": "sequential", "label": "sequential"},
          {"count": 6, "key": "chapter", "label": "chapter"},
          {"count": 3, "key": "html", "label": "html"},
          {"count": 2, "key": "video", "label": "video"},
          {"count": 2, "key": "course", "label": "course"}
        ]
      },
      "run": {
        "facet": {
          "key": "run",
          "label": "Run"
        },
        "values": [
          {"count": 47, "key": "2015_Summer", "label": "2015_Summer"},
          {"count": 43, "key": "2014_Spring", "label": "2014_Spring"}
        ]
      }
    };

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

    var Facets = ListingResources.Facets;

    QUnit.module('Test listing facets', {
      beforeEach: function () {
        TestUtils.setup();
      },
      afterEach: function() {
        TestUtils.cleanup();
      }
    });

    QUnit.test('Assert that facets render correctly', function(assert) {
      var done = assert.async();

      var selectedFacets = {};
      var updateFacets = function(facetId, id, checked) {
        if (!_.has(selectedFacets, facetId)) {
          selectedFacets[facetId] = {};
        }
        selectedFacets[facetId][id] = checked;
      };

      var afterMount = function (component) {
        var $node = $(React.findDOMNode(component));

        // Assert correct ordering of facet counts
        var titles = _.map($node.find(".panel-title"), function(child) {
          return $(child).text();
        });
        assert.deepEqual([
          "Course", "Run", "Item Type",
          "a", "allowmulti", "disallowmultiple", "free"
        ], titles);

        var terms = _.map($node.find("li label"), function(child) {
          return $(child).text();
        });
        assert.deepEqual([
          "0.001", "MIT.latex2edx", "2015_Summer", "2014_Spring", "problem",
          "vertical", "sequential", "chapter", "html", "video", "course",
          "t1", "t2", "term1", "term2", "term3", "term4", "tagging",
          "tagging with spaces"
        ], terms);

        done();
      };

      React.addons.TestUtils.renderIntoDocument(<Facets
        facetCounts={facetCounts}
        selectedFacets={selectedFacets}
        imageDir="/images"
        updateFacets={updateFacets}
        ref={afterMount}
        />);
    });

    QUnit.test('Assert that an empty facet count displays nothing',
      function(assert) {
        var done = assert.async();

        var selectedFacets = {};
        var updateFacets = function(facetId, id, checked) {
          if (!_.has(selectedFacets, facetId)) {
            selectedFacets[facetId] = {};
          }
          selectedFacets[facetId][id] = checked;
        };

        var afterMount = function (component) {
          var $node = $(React.findDOMNode(component));

          // Assert correct ordering of facet counts
          var titles = _.map($node.find(".panel-title"), function(child) {
            return $(child).text();
          });
          assert.deepEqual([], titles);

          var terms = _.map($node.find("li label"), function(child) {
            return $(child).text();
          });
          assert.deepEqual([], terms);

          done();
        };

        React.addons.TestUtils.renderIntoDocument(<Facets
          facetCounts={emptyFacetCounts}
          selectedFacets={selectedFacets}
          imageDir="/images"
          updateFacets={updateFacets}
          ref={afterMount}
          />);
      }
    );

    QUnit.test('Assert that facets can be clicked', function(assert) {
      var done = assert.async();

      var selectedFacets = {};
      var updateFacets = function(facetId, id, checked) {
        if (!_.has(selectedFacets, facetId)) {
          selectedFacets[facetId] = {};
        }
        selectedFacets[facetId][id] = checked;
      };

      var afterMountCheck = function (component) {
        var $node = $(React.findDOMNode(component));

        // iCheckbox uses ins elements to contain their checkbox.
        var $firstCheckbox = $node.find("ins").first();
        assert.deepEqual(selectedFacets, {});
        $firstCheckbox.click();
        assert.deepEqual(selectedFacets, {
          course: {
            "0.001": true
          }
        });

        var afterMountUncheck = function(component) {
          var $node = $(React.findDOMNode(component));

          var $firstCheckbox = $node.find("ins").first();
          assert.deepEqual(selectedFacets, {
            course: {
              "0.001": true
            }
          });
          $firstCheckbox.click();
          assert.deepEqual(selectedFacets, {
            course: {
              "0.001": false
            }
          });

          done();
        };

        // Unselect that checkbox
        React.addons.TestUtils.renderIntoDocument(<Facets
          facetCounts={facetCounts}
          selectedFacets={selectedFacets}
          imageDir="/images"
          updateFacets={updateFacets}
          ref={afterMountUncheck}
          />);
      };

      React.addons.TestUtils.renderIntoDocument(<Facets
        facetCounts={facetCounts}
        selectedFacets={selectedFacets}
        imageDir="/images"
        updateFacets={updateFacets}
        ref={afterMountCheck}
        />);
    });

  }
);
