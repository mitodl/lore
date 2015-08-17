define(['QUnit', 'jquery', 'react', 'test_utils', 'utils'],
  function(QUnit, $, React, TestUtils, Utils) {
    "use strict";

    var InfiniteList = Utils.InfiniteList;
    var waitForAjax = TestUtils.waitForAjax;
    var page1 = {
      "count": 4,
      "next": "/api/v1/repositories/?page=2",
      "previous": null,
      "results": [
        {
          "id": 1,
          "slug": "test",
          "name": "test",
          "description": "test",
          "date_created": "2015-07-17T17:28:10.628509Z"
        },
        {
          "id": 2,
          "slug": "empty",
          "name": "empty",
          "description": "empty",
          "date_created": "2015-07-30T18:21:59.110309Z"
        },
        {
          "id": 3,
          "slug": "import",
          "name": "import",
          "description": "import",
          "date_created": "2015-07-30T18:35:08.504801Z"
        }
      ]
    };

    var page2 = {
      count: 4,
      next: null,
      previous: null,
      results: {
        "id": 4,
        "slug": "manyassets",
        "name": "manyassets",
        "description": "manyassets",
        "date_created": "2015-08-18T13:51:23.124149Z"
      }
    };

    QUnit.module('Test InfiniteList', {
      beforeEach: function() {
        TestUtils.setup();

        TestUtils.initMockjax({
          url: '/api/v1/repositories/',
          type: 'GET',
          responseText: page1
        });
        TestUtils.initMockjax({
          url: '/api/v1/repositories/?page=2',
          type: 'GET',
          responseText: page2
        });
      },
      afterEach: function() {
        TestUtils.cleanup();
      }
    });

    QUnit.test('Test empty list', function(assert) {
      var done = assert.async();
      var errorCount = 0;
      var onError = function() {
        errorCount++;
      };

      var afterMount = function(component) {
        assert.equal(errorCount, 0);
        assert.deepEqual(component.state, {
          next: null,
          isInfiniteLoading: false,
          elements: []
        });

        done();
      };

      React.addons.TestUtils.renderIntoDocument(<ul><InfiniteList
        url={null}
        onError={onError}
        elementHeight={50}
        containerHeight={500}
        ref={afterMount}
        /></ul>);
    });

    QUnit.test('Test infinite scroll error handling #1', function(assert) {
      var done = assert.async();
      var errorCount = 0;
      var onError = function() {
        errorCount++;
      };

      TestUtils.replaceMockjax({
        url: '/api/v1/repositories/',
        type: 'GET',
        status: 400
      });

      var elementHeight = 150;
      var containerHeight = 125;
      $("<div id='container' style='height: " + containerHeight + "px;'/>")
        .appendTo($("body"));

      var makeElement = function(data) {
        return <li key={data.slug}
                   style={{height: elementHeight}}>{data.name}</li>;
      };

      var afterMount = function(component) {
        assert.deepEqual(
          {
            elements: [],
            isInfiniteLoading: false,
            next: "/api/v1/repositories/"
          },
          component.state
        );

        waitForAjax(1, function () {
          component.forceUpdate(function () {
            assert.equal(errorCount, 1);
            assert.deepEqual(
              {
                elements: [],
                isInfiniteLoading: false,
                next: "/api/v1/repositories/"
              },
              component.state
            );

            $("#container").remove();
            done();
          });
        });
      };

      React.render(<ul><InfiniteList
        url="/api/v1/repositories/"
        onError={onError}
        makeElement={makeElement}
        containerHeight={containerHeight}
        elementHeight={elementHeight}
        ref={afterMount}
        /></ul>, $("#container")[0]);
    });

    QUnit.test('Test infinite scroll error handling #2', function(assert) {
      var done = assert.async();
      var errorCount = 0;
      var onError = function() {
        errorCount++;
      };

      TestUtils.replaceMockjax({
        url: '/api/v1/repositories/?page=2',
        type: 'GET',
        status: 400
      });

      var elementHeight = 150;
      var containerHeight = 125;
      $("<div id='container' style='height: " + containerHeight + "px;'/>")
        .appendTo($("body"));

      var makeElement = function(data) {
        return <li key={data.slug}
                   style={{height: elementHeight}}>{data.name}</li>;
      };

      var afterMount = function(component) {
        assert.deepEqual(
          {
            elements: [],
            isInfiniteLoading: false,
            next: "/api/v1/repositories/"
          },
          component.state
        );

        var node = React.findDOMNode(component);
        waitForAjax(1, function () {
          component.forceUpdate(function () {
            assert.equal(errorCount, 0);
            assert.deepEqual(
              {
                elements: page1.results,
                isInfiniteLoading: false,
                next: "/api/v1/repositories/?page=2"
              },
              component.state
            );

            $($(node).find("div")[0]).animate({scrollTop: elementHeight * 3}, {
              complete: function() {
                waitForAjax(1, function () {
                  component.forceUpdate(function () {
                    assert.equal(errorCount, 1);
                    assert.deepEqual(
                      {
                        elements: page1.results,
                        isInfiniteLoading: false,
                        next: "/api/v1/repositories/?page=2"
                      },
                      component.state
                    );

                    $("#container").remove();
                    done();
                  });
                });
              },
              duration: 10
            });
          });
        });
      };

      React.render(<ul><InfiniteList
        url="/api/v1/repositories/"
        onError={onError}
        makeElement={makeElement}
        containerHeight={containerHeight}
        elementHeight={elementHeight}
        ref={afterMount}
        /></ul>, $("#container")[0]);
    });

    QUnit.test('Test infinite scroll', function(assert) {
      var done = assert.async();
      var errorCount = 0;
      var onError = function() {
        errorCount++;
      };

      var elementHeight = 150;
      var containerHeight = 125;
      $("<div id='container' style='height: " + containerHeight + "px;'/>")
        .appendTo($("body"));

      var makeElement = function(data) {
        return <li key={data.slug}
                   style={{height: elementHeight}}>{data.name}</li>;
      };

      var afterMount = function(component) {
        assert.deepEqual(
          {
            elements: [],
            isInfiniteLoading: false,
            next: "/api/v1/repositories/"
          },
          component.state
        );

        var node = React.findDOMNode(component);
        waitForAjax(1, function () {
          component.forceUpdate(function () {
            assert.deepEqual(
              {
                elements: page1.results,
                isInfiniteLoading: false,
                next: "/api/v1/repositories/?page=2"
              },
              component.state
            );

            $($(node).find("div")[0]).animate({scrollTop: elementHeight * 3}, {
              complete: function() {
                waitForAjax(1, function () {
                  component.forceUpdate(function () {
                    assert.deepEqual(
                      {
                        elements: page1.results.concat(page2.results),
                        isInfiniteLoading: false,
                        next: null
                      },
                      component.state
                    );
                    assert.equal(errorCount, 0);

                    $("#container").remove();
                    done();
                  });
                });
              },
              duration: 10
            });
          });
        });
      };

      React.render(<ul><InfiniteList
        url="/api/v1/repositories/"
        onError={onError}
        makeElement={makeElement}
        containerHeight={containerHeight}
        elementHeight={elementHeight}
        ref={afterMount}
        /></ul>, $("#container")[0]);
    });
  }
);
