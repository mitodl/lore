define(['QUnit', 'jquery', 'lr_exports', 'reactaddons',
  'test_utils'], function(QUnit, $, Exports, React, TestUtils) {
  'use strict';

  var ExportsComponent = Exports.ExportsComponent;
  var waitForAjax = TestUtils.waitForAjax;

  var learningResourceResponse = {
    "id": 123,
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

  QUnit.module('Test exports panel', {
    beforeEach: function () {
      TestUtils.setup();
      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo/learning_resource_exports/user/',
        type: 'GET',
        responseText: {
          "count": 1,
          "next": null,
          "previous": null,
          "results": [{"id": 123}]
        }
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo/learning_resources/?id=123',
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
      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo/learning_resource_export_tasks/',
        type: 'GET',
        responseText: {
          "count": 1,
          "next": null,
          "previous": null,
          "results": [
            {
              "id": "task1",
              "status": "successful",
              "url": "/media/resource_exports/export_task1.tar.gz"
            }
          ]
        }
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo/learning_resource_export_tasks/',
        type: 'POST',
        responseText: {
          "id": "task2"
        }
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo/learning_resource_export_tasks/task2/',
        type: 'GET',
        responseText: {
          "id": "task2",
          "status": "processing",
          "url": ""
        }
      });
      TestUtils.initMockjax({
        url: '/media/resource_exports/export_task2.tar.gz',
        type: 'GET',
        responseText: ''
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo/learning_resource_exports/user/',
        type: 'DELETE'
      });
    },
    afterEach: function () {
      TestUtils.cleanup();
    }
  });

  QUnit.test("Test functionality for ExportComponent", function(assert) {
    var done = assert.async();

    var clearExportCount = 0;
    var clearExports = function() {
      clearExportCount++;
    };

    var afterMount = function(component) {
      // Initial state
      assert.deepEqual(
        {
          exportButtonVisible: false,
          exports: []
        },
        component.state
      );

      // Wait for GET exports and GET related learning resources.
      waitForAjax(2, function() {
        // one export
        assert.deepEqual(
          {
            exports: [learningResourceResponse],
            exportButtonVisible: true
          },
          component.state
        );

        var $node = $(React.findDOMNode(component));
        var button = $node.find("button")[0];

        // Click the button. There should be a POST to start the task
        // followed by an immediate GET to check status (which is 'processing').
        React.addons.TestUtils.Simulate.click(button);
        waitForAjax(2, function() {
          assert.deepEqual(
            {
              exports: [learningResourceResponse],
              exportButtonVisible: false
            },
            component.state
          );

          TestUtils.replaceMockjax({
            url: '/api/v1/repositories/repo/' +
              'learning_resource_export_tasks/task2/',
            type: 'GET',
            responseText: {
              "id": "task2",
              "status": "processing",
              "url": ""
            }
          });

          // Wait a second for task which is processing.
          waitForAjax(1, function() {
            assert.deepEqual(
              {
                exportButtonVisible: false,
                exports: [learningResourceResponse]
              },
              component.state
            );

            TestUtils.replaceMockjax({
              url: '/api/v1/repositories/repo/' +
              'learning_resource_export_tasks/task2/',
              type: 'GET',
              responseText: {
                "id": "task2",
                "status": "success",
                "url": "/media/resource_exports/export_task2.tar.gz"
              }
            });

            assert.equal(0, clearExportCount);

            // In a second another GET for status will happen which will be
            // successful. Then a DELETE to clear exports list.
            waitForAjax(2, function () {
              assert.deepEqual(
                {
                  exports: [],
                  exportButtonVisible: false,
                  url: "/media/resource_exports/export_task2.tar.gz"
                },
                component.state
              );
              assert.equal(1, clearExportCount);

              done();
            });
          });
        });
      });
    };

    React.addons.TestUtils.renderIntoDocument(
      <ExportsComponent
      interval={200}
      repoSlug="repo"
      loggedInUser="user"
      clearExports={clearExports}
      ref={afterMount}
      />);
  });

  QUnit.test("Test empty list of exports", function(assert) {
    var done = assert.async();

    TestUtils.replaceMockjax({
      url: '/api/v1/repositories/repo/learning_resource_exports/user/',
      type: 'GET',
      responseText: {
        "count": 0,
        "next": null,
        "previous": null,
        "results": []
      }
    });

    var afterMount = function(component) {
      // Initial state
      assert.deepEqual(
        {
          exportButtonVisible: false,
          exports: []
        },
        component.state
      );

      // Wait for GET of export list.
      waitForAjax(1, function() {
        assert.deepEqual(
          {
            exports: [],
            exportButtonVisible: false
          },
          component.state
        );
        done();
      });
    };

    React.addons.TestUtils.renderIntoDocument(
      <ExportsComponent
      interval={200}
      repoSlug="repo"
      loggedInUser="user"
      clearExports={function() {}}
      ref={afterMount}
      />);
  });

  QUnit.test("Test failure to POST a task", function(assert) {
    var done = assert.async();

    var afterMount = function(component) {
      // Initial state
      assert.deepEqual(
        {
          exportButtonVisible: false,
          exports: []
        },
        component.state
      );

      // Wait for GET exports and GET related learning resources.
      waitForAjax(2, function() {
        // one export
        assert.deepEqual(
          {
            exports: [learningResourceResponse],
            exportButtonVisible: true
          },
          component.state
        );

        var $node = $(React.findDOMNode(component));
        var button = $node.find("button")[0];

        // The task fails!
        TestUtils.replaceMockjax({
          url: '/api/v1/repositories/repo/' +
          'learning_resource_export_tasks/',
          type: 'POST',
          status: 400
        });

        // Click the button. There should be a POST to start the task.
        React.addons.TestUtils.Simulate.click(button);
        waitForAjax(1, function() {
          assert.deepEqual(
            {
              exports: [learningResourceResponse],
              exportButtonVisible: true,
              message: {
                error: "Error preparing learning resources for download."
              }
            },
            component.state
          );

          done();
        });
      });
    };

    React.addons.TestUtils.renderIntoDocument(
      <ExportsComponent
      interval={200}
      repoSlug="repo"
      loggedInUser="user"
      clearExports={function() {}}
      ref={afterMount}
      />);
  });

  QUnit.test("Test failure to get status update", function(assert) {
    var done = assert.async();

    var afterMount = function(component) {
      // Initial state
      assert.deepEqual(
        {
          exportButtonVisible: false,
          exports: []
        },
        component.state
      );

      // Wait for GET exports and GET related learning resources.
      waitForAjax(2, function() {
        // one export
        assert.deepEqual(
          {
            exports: [learningResourceResponse],
            exportButtonVisible: true
          },
          component.state
        );

        var $node = $(React.findDOMNode(component));
        var button = $node.find("button")[0];

        TestUtils.replaceMockjax({
          url: '/api/v1/repositories/repo/' +
          'learning_resource_export_tasks/task2/',
          type: 'GET',
          status: 400
        });

        // Click the button. There should be a POST to start the task
        // followed by an immediate GET to check status (which is 'processing').
        React.addons.TestUtils.Simulate.click(button);
        waitForAjax(2, function() {
          assert.deepEqual(
            {
              exports: [learningResourceResponse],
              exportButtonVisible: false,
              message: {
                error: "Error occurred preparing " +
                "learning resources for download."
              }
            },
            component.state
          );

          done();
        });
      });
    };

    React.addons.TestUtils.renderIntoDocument(
      <ExportsComponent
      interval={200}
      repoSlug="repo"
      loggedInUser="user"
      clearExports={function() {}}
      ref={afterMount}
      />);
  });

  QUnit.test("Test failure to get status update, second attempt",
    function(assert) {
    var done = assert.async();

    var afterMount = function(component) {
      // Initial state
      assert.deepEqual(
        {
          exportButtonVisible: false,
          exports: []
        },
        component.state
      );

      // Wait for GET exports and GET related learning resources.
      waitForAjax(2, function() {
        // one export
        assert.deepEqual(
          {
            exports: [learningResourceResponse],
            exportButtonVisible: true
          },
          component.state
        );

        var $node = $(React.findDOMNode(component));
        var button = $node.find("button")[0];

        // Click the button. There should be a POST to start the task
        // followed by an immediate GET to check status (which is 'processing').
        React.addons.TestUtils.Simulate.click(button);
        waitForAjax(2, function() {
          assert.deepEqual(
            {
              exports: [learningResourceResponse],
              exportButtonVisible: false
            },
            component.state
          );

          TestUtils.replaceMockjax({
            url: '/api/v1/repositories/repo/' +
            'learning_resource_export_tasks/task2/',
            type: 'GET',
            status: 400
          });

          // In three seconds another GET for status will happen which will
          // fail.
          waitForAjax(1, function() {
            assert.deepEqual(
              {
                exports: [learningResourceResponse],
                exportButtonVisible: false,
                message: {
                  error: "Error occurred preparing learning " +
                  "resources for download."
                }
              },
              component.state
            );

            done();
          });
        });
      });
    };

    React.addons.TestUtils.renderIntoDocument(
      <ExportsComponent
      interval={200}
      repoSlug="repo"
      loggedInUser="user"
      clearExports={function() {}}
      ref={afterMount}
      />);
  });

  QUnit.test("Test failure to get status update, third attempt",
    function(assert) {
    var done = assert.async();

    var afterMount = function(component) {
      // Initial state
      assert.deepEqual(
        {
          exportButtonVisible: false,
          exports: []
        },
        component.state
      );

      // Wait for GET exports and GET related learning resources.
      waitForAjax(2, function() {
        // one export
        assert.deepEqual(
          {
            exports: [learningResourceResponse],
            exportButtonVisible: true
          },
          component.state
        );

        var $node = $(React.findDOMNode(component));
        var button = $node.find("button")[0];

        // Click the button. There should be a POST to start the task
        // followed by an immediate GET to check status (which is 'processing').
        React.addons.TestUtils.Simulate.click(button);
        waitForAjax(2, function() {
          assert.deepEqual(
            {
              exports: [learningResourceResponse],
              exportButtonVisible: false
            },
            component.state
          );

          TestUtils.replaceMockjax({
            url: '/api/v1/repositories/repo/' +
            'learning_resource_export_tasks/task2/',
            type: 'GET',
            responseText: {
              "id": "task2",
              "status": "processing",
              "url": ""
            }
          });

          // In a second another GET for status will happen which will
          // fail.
          waitForAjax(1, function() {
            assert.deepEqual(
              {
                exportButtonVisible: false,
                exports: [learningResourceResponse]
              },
              component.state
            );

            TestUtils.replaceMockjax({
              url: '/api/v1/repositories/repo/' +
              'learning_resource_export_tasks/task2/',
              type: 'GET',
              status: 400
            });

            waitForAjax(1, function() {
              assert.deepEqual(
                {
                  exports: [learningResourceResponse],
                  exportButtonVisible: false,
                  message: {
                    error: "Error occurred preparing learning " +
                    "resources for download."
                  }
                },
                component.state
              );
              done();
            });
          });
        });
      });
    };

    React.addons.TestUtils.renderIntoDocument(
      <ExportsComponent
      interval={200}
      repoSlug="repo"
      loggedInUser="user"
      clearExports={function() {}}
      ref={afterMount}
      />);
  });

  QUnit.test("Test failure to clear exports", function(assert) {
    var done = assert.async();

    var clearExportCount = 0;
    var clearExports = function() {
      clearExportCount++;
    };

    var afterMount = function(component) {
      // Initial state
      assert.deepEqual(
        {
          exportButtonVisible: false,
          exports: []
        },
        component.state
      );

      // Wait for GET exports and GET related learning resources.
      waitForAjax(2, function() {
        // one export
        assert.deepEqual(
          {
            exports: [learningResourceResponse],
            exportButtonVisible: true
          },
          component.state
        );

        var $node = $(React.findDOMNode(component));
        var button = $node.find("button")[0];

        // Click the button. There should be a POST to start the task
        // followed by an immediate GET to check status (which is 'processing').
        React.addons.TestUtils.Simulate.click(button);
        waitForAjax(2, function() {
          assert.deepEqual(
            {
              exports: [learningResourceResponse],
              exportButtonVisible: false
            },
            component.state
          );

          TestUtils.replaceMockjax({
            url: '/api/v1/repositories/repo/' +
            'learning_resource_export_tasks/task2/',
            type: 'GET',
            responseText: {
              "id": "task2",
              "status": "success",
              "url": "/media/resource_exports/export_task2.tar.gz"
            }
          });
          TestUtils.replaceMockjax({
            url: '/api/v1/repositories/repo/' +
            'learning_resource_exports/user/',
            type: 'DELETE',
            status: 400
          });

          // In three seconds another GET for status will happen which will be
          // successful. Then a DELETE to clear export list fails.
          waitForAjax(2, function() {
            assert.deepEqual(
              {
                exports: [learningResourceResponse],
                exportButtonVisible: false,
                message: {
                  error: "Error clearing learning resource exports."
                },
                url: "/media/resource_exports/export_task2.tar.gz"
              },
              component.state
            );
            assert.equal(0, clearExportCount);

            done();
          });
        });
      });
    };

    React.addons.TestUtils.renderIntoDocument(
      <ExportsComponent
      interval={200}
      repoSlug="repo"
      loggedInUser="user"
      clearExports={clearExports}
      ref={afterMount}
      />);
  });

  QUnit.test("Test resource export panel renders into div", function(assert) {
    var container = document.createElement("div");

    assert.equal(0, $(container).find("div").size());
    Exports.loader("repo", "user", function() {}, container);
    assert.equal(1, $(container).find("div").size());
  });
});
