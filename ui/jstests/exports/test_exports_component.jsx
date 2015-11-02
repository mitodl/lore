define(['QUnit', 'jquery', 'lr_exports', 'test_utils', 'react'],
  function (QUnit, $, Exports, TestUtils, React) {
    'use strict';

    var waitForAjax = TestUtils.waitForAjax;
    var ExportsComponent = Exports.ExportsComponent;

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

    QUnit.module('Test exports component', {
      beforeEach: function () {
        TestUtils.setup();

        // The mocked AJAX omits task_info and task_type but currently they aren't
        // used in the javascript.

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
          url: '/api/v1/tasks/',
          type: 'GET',
          responseText: {
            "count": 1,
            "next": null,
            "previous": null,
            "results": [
              {
                "id": "task1",
                "status": "successful",
                "result": {
                  "url": "/media/resource_exports/export_task1.tar.gz",
                  "collision": false
                }
              }
            ]
          }
        });
        TestUtils.initMockjax({
          url: '/api/v1/tasks/',
          type: 'POST',
          responseText: {
            "id": "task2"
          }
        });
        TestUtils.initMockjax({
          url: '/api/v1/tasks/task2/',
          type: 'GET',
          responseText: {
            "id": "task2",
            "status": "processing",
            "result": null
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

    QUnit.test("Test functionality for ExportComponent", function (assert) {
      var done = assert.async();

      var clearExportCount = 0;
      var clearExports = function () {
        clearExportCount++;
      };

      var afterMount = function (component) {
        // Initial state
        assert.deepEqual(
          {
            exportButtonVisible: false,
            exports: [],
            exportsSelected: [],
            collision: false
          },
          component.state
        );

        // Wait for GET exports and GET related learning resources.
        waitForAjax(2, function () {
          // one export
          assert.deepEqual(
            {
              exports: [learningResourceResponse],
              exportButtonVisible: true,
              exportsSelected: [learningResourceResponse.id],
              collision: false
            },
            component.state
          );

          var $node = $(React.findDOMNode(component));
          var button = $node.find("button")[0];

          // Click the button. There should be a POST to start the task
          // followed by an immediate GET to check status (which is 'processing').
          React.addons.TestUtils.Simulate.click(button);
          waitForAjax(2, function () {
            assert.deepEqual(
              {
                exports: [learningResourceResponse],
                exportButtonVisible: false,
                exportsSelected: [learningResourceResponse.id],
                collision: false
              },
              component.state
            );

            TestUtils.replaceMockjax({
              url: '/api/v1/tasks/task2/',
              type: 'GET',
              responseText: {
                "id": "task2",
                "status": "processing",
                "result": null
              }
            });

            // Wait a second for task which is processing.
            waitForAjax(1, function () {
              assert.deepEqual(
                {
                  exportButtonVisible: false,
                  exports: [learningResourceResponse],
                  exportsSelected: [learningResourceResponse.id],
                  collision: false
                },
                component.state
              );

              TestUtils.replaceMockjax({
                url: '/api/v1/tasks/task2/',
                type: 'GET',
                responseText: {
                  "id": "task2",
                  "status": "success",
                  "result": {
                    "url": "/media/resource_exports/export_task2.tar.gz",
                    "collision": false
                  }
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
                    exportsSelected: [],
                    collision: false,
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

    QUnit.test("Test empty list of exports", function (assert) {
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

      var afterMount = function (component) {
        // Initial state
        assert.deepEqual(
          {
            exportButtonVisible: false,
            exports: [],
            exportsSelected: [],
            collision: false
          },
          component.state
        );

        // Wait for GET of export list.
        waitForAjax(1, function () {
          assert.deepEqual(
            {
              exports: [],
              exportButtonVisible: false,
              exportsSelected: [],
              collision: false
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

    QUnit.test("Test failure to POST a task", function (assert) {
      var done = assert.async();

      var afterMount = function (component) {
        // Initial state
        assert.deepEqual(
          {
            exportButtonVisible: false,
            exports: [],
            exportsSelected: [],
            collision: false
          },
          component.state
        );

        // Wait for GET exports and GET related learning resources.
        waitForAjax(2, function () {
          // one export
          assert.deepEqual(
            {
              exports: [learningResourceResponse],
              exportButtonVisible: true,
              exportsSelected: [learningResourceResponse.id],
              collision: false
            },
            component.state
          );

          var $node = $(React.findDOMNode(component));
          var button = $node.find("button")[0];

          // The task fails!
          TestUtils.replaceMockjax({
            url: '/api/v1/tasks/',
            type: 'POST',
            status: 400
          });

          // Click the button. There should be a POST to start the task.
          React.addons.TestUtils.Simulate.click(button);
          waitForAjax(1, function () {
            assert.deepEqual(
              {
                exports: [learningResourceResponse],
                exportButtonVisible: true,
                exportsSelected: [learningResourceResponse.id],
                collision: false,
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

    QUnit.test("Test failure to get status update", function (assert) {
      var done = assert.async();

      var afterMount = function (component) {
        // Initial state
        assert.deepEqual(
          {
            exportButtonVisible: false,
            exports: [],
            exportsSelected: [],
            collision: false
          },
          component.state
        );

        // Wait for GET exports and GET related learning resources.
        waitForAjax(2, function () {
          // one export
          assert.deepEqual(
            {
              exports: [learningResourceResponse],
              exportButtonVisible: true,
              exportsSelected: [learningResourceResponse.id],
              collision: false
            },
            component.state
          );

          var $node = $(React.findDOMNode(component));
          var button = $node.find("button")[0];

          TestUtils.replaceMockjax({
            url: '/api/v1/tasks/task2/',
            type: 'GET',
            status: 400
          });

          // Click the button. There should be a POST to start the task
          // followed by an immediate GET to check status (which is 'processing').
          React.addons.TestUtils.Simulate.click(button);
          waitForAjax(2, function () {
            assert.deepEqual(
              {
                exports: [learningResourceResponse],
                exportButtonVisible: false,
                exportsSelected: [learningResourceResponse.id],
                collision: false,
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
      function (assert) {
        var done = assert.async();

        var afterMount = function (component) {
          // Initial state
          assert.deepEqual(
            {
              exportButtonVisible: false,
              exports: [],
              exportsSelected: [],
              collision: false
            },
            component.state
          );

          // Wait for GET exports and GET related learning resources.
          waitForAjax(2, function () {
            // one export
            assert.deepEqual(
              {
                exports: [learningResourceResponse],
                exportButtonVisible: true,
                exportsSelected: [learningResourceResponse.id],
                collision: false
              },
              component.state
            );

            var $node = $(React.findDOMNode(component));
            var button = $node.find("button")[0];

            // Click the button. There should be a POST to start the task
            // followed by an immediate GET to check status (which is 'processing').
            React.addons.TestUtils.Simulate.click(button);
            waitForAjax(2, function () {
              assert.deepEqual(
                {
                  exports: [learningResourceResponse],
                  exportButtonVisible: false,
                  exportsSelected: [learningResourceResponse.id],
                  collision: false
                },
                component.state
              );

              TestUtils.replaceMockjax({
                url: '/api/v1/tasks/task2/',
                type: 'GET',
                status: 400
              });

              // In three seconds another GET for status will happen which will
              // fail.
              waitForAjax(1, function () {
                assert.deepEqual(
                  {
                    exports: [learningResourceResponse],
                    exportButtonVisible: false,
                    exportsSelected: [learningResourceResponse.id],
                    collision: false,
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
      function (assert) {
        var done = assert.async();

        var afterMount = function (component) {
          // Initial state
          assert.deepEqual(
            {
              exportButtonVisible: false,
              exports: [],
              exportsSelected: [],
              collision: false
            },
            component.state
          );

          // Wait for GET exports and GET related learning resources.
          waitForAjax(2, function () {
            // one export
            assert.deepEqual(
              {
                exports: [learningResourceResponse],
                exportButtonVisible: true,
                exportsSelected: [learningResourceResponse.id],
                collision: false
              },
              component.state
            );

            var $node = $(React.findDOMNode(component));
            var button = $node.find("button")[0];

            // Click the button. There should be a POST to start the task
            // followed by an immediate GET to check status (which is 'processing').
            React.addons.TestUtils.Simulate.click(button);
            waitForAjax(2, function () {
              assert.deepEqual(
                {
                  exports: [learningResourceResponse],
                  exportButtonVisible: false,
                  exportsSelected: [learningResourceResponse.id],
                  collision: false
                },
                component.state
              );

              TestUtils.replaceMockjax({
                url: '/api/v1/tasks/task2/',
                type: 'GET',
                responseText: {
                  "id": "task2",
                  "status": "processing",
                  "result": null
                }
              });

              // In a second another GET for status will happen which will
              // fail.
              waitForAjax(1, function () {
                assert.deepEqual(
                  {
                    exportButtonVisible: false,
                    exports: [learningResourceResponse],
                    exportsSelected: [learningResourceResponse.id],
                    collision: false
                  },
                  component.state
                );

                TestUtils.replaceMockjax({
                  url: '/api/v1/tasks/task2/',
                  type: 'GET',
                  responseText: {
                    "id": "task2",
                    "status": "failure",
                    "result": null
                  }
                });

                waitForAjax(1, function () {
                  assert.deepEqual(
                    {
                      exports: [learningResourceResponse],
                      exportButtonVisible: false,
                      exportsSelected: [learningResourceResponse.id],
                      message: {
                        error: "Error occurred preparing learning " +
                        "resources for download."
                      },
                      collision: false
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

    QUnit.test("Test failure to get status update due to 500",
      function (assert) {
        var done = assert.async();

        var afterMount = function (component) {
          // Initial state
          assert.deepEqual(
            {
              exportButtonVisible: false,
              exports: [],
              exportsSelected: [],
              collision: false
            },
            component.state
          );

          // Wait for GET exports and GET related learning resources.
          waitForAjax(2, function () {
            // one export
            assert.deepEqual(
              {
                exports: [learningResourceResponse],
                exportButtonVisible: true,
                exportsSelected: [learningResourceResponse.id],
                collision: false
              },
              component.state
            );

            var $node = $(React.findDOMNode(component));
            var button = $node.find("button")[0];

            // Click the button. There should be a POST to start the task
            // followed by an immediate GET to check status (which is 'processing').
            React.addons.TestUtils.Simulate.click(button);
            waitForAjax(2, function () {
              assert.deepEqual(
                {
                  exports: [learningResourceResponse],
                  exportButtonVisible: false,
                  exportsSelected: [learningResourceResponse.id],
                  collision: false
                },
                component.state
              );

              TestUtils.replaceMockjax({
                url: '/api/v1/tasks/task2/',
                type: 'GET',
                responseText: {
                  "id": "task2",
                  "status": "processing",
                  "result": null
                }
              });

              // In a second another GET for status will happen which will
              // fail.
              waitForAjax(1, function () {
                assert.deepEqual(
                  {
                    exportButtonVisible: false,
                    exports: [learningResourceResponse],
                    exportsSelected: [learningResourceResponse.id],
                    collision: false
                  },
                  component.state
                );

                TestUtils.replaceMockjax({
                  url: '/api/v1/tasks/task2/',
                  type: 'GET',
                  status: 500
                });

                waitForAjax(1, function () {
                  assert.deepEqual(
                    {
                      exports: [learningResourceResponse],
                      exportButtonVisible: false,
                      exportsSelected: [learningResourceResponse.id],
                      collision: false,
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

    QUnit.test("Test failure to clear exports", function (assert) {
      var done = assert.async();

      var clearExportCount = 0;
      var clearExports = function () {
        clearExportCount++;
      };

      var afterMount = function (component) {
        // Initial state
        assert.deepEqual(
          {
            exportButtonVisible: false,
            exports: [],
            exportsSelected: [],
            collision: false,
          },
          component.state
        );

        // Wait for GET exports and GET related learning resources.
        waitForAjax(2, function () {
          // one export
          assert.deepEqual(
            {
              exports: [learningResourceResponse],
              exportButtonVisible: true,
              exportsSelected: [learningResourceResponse.id],
              collision: false
            },
            component.state
          );

          var $node = $(React.findDOMNode(component));
          var button = $node.find("button")[0];

          // Click the button. There should be a POST to start the task
          // followed by an immediate GET to check status (which is 'processing').
          React.addons.TestUtils.Simulate.click(button);
          waitForAjax(2, function () {
            assert.deepEqual(
              {
                exports: [learningResourceResponse],
                exportButtonVisible: false,
                exportsSelected: [learningResourceResponse.id],
                collision: false
              },
              component.state
            );

            TestUtils.replaceMockjax({
              url: '/api/v1/tasks/task2/',
              type: 'GET',
              responseText: {
                "id": "task2",
                "status": "success",
                "result": {
                  "url": "/media/resource_exports/export_task2.tar.gz",
                  "collision": true
                }
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
            waitForAjax(2, function () {
              assert.deepEqual(
                {
                  exports: [learningResourceResponse],
                  exportButtonVisible: false,
                  exportsSelected: [learningResourceResponse.id],
                  message: {
                    error: "Error clearing learning resource exports."
                  },
                  url: "/media/resource_exports/export_task2.tar.gz",
                  collision: true
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

    QUnit.test("Assert that export checkboxes adjust ids sent to server",
      function (assert) {
        var done = assert.async();

        var clearExportCount = 0;
        var clearExports = function () {
          clearExportCount++;
        };

        var afterMount = function (component) {
          // Initial state
          assert.deepEqual(
            {
              exportButtonVisible: false,
              exports: [],
              exportsSelected: [],
              collision: false,
            },
            component.state
          );

          // Wait for GET exports and GET related learning resources.
          waitForAjax(2, function () {
            // one export
            assert.deepEqual(
              {
                exports: [learningResourceResponse],
                exportButtonVisible: true,
                exportsSelected: [learningResourceResponse.id],
                collision: false
              },
              component.state
            );

            var $node = $(React.findDOMNode(component));
            var button = $node.find("button")[0];

            // This matches against an empty set of ids which verifies that
            // exportsSelected affects what's sent to the server.
            TestUtils.replaceMockjax({
              url: '/api/v1/tasks/',
              type: 'POST',
              responseText: {
                id: "task2"
              },
              data: JSON.stringify({
                task_type: "resource_export",
                task_info: {
                  ids: [],
                  repo_slug: "repo"
                }
              })
            });

            component.setState({
              exportsSelected: []
            }, function () {
              // Click the button. There should be a POST to start the task
              // followed by an immediate GET to check status.
              React.addons.TestUtils.Simulate.click(button);
              waitForAjax(2, function () {
                // If we reach this point the request data matched successfully.
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

    QUnit.test("Verify that checkboxes alter state", function (assert) {
      var done = assert.async();

      var response1 = learningResourceResponse;
      var response2 = $.extend({}, learningResourceResponse, {id: 345});
      var response3 = $.extend({}, learningResourceResponse, {id: 789});

      TestUtils.replaceMockjax({
        url: '/api/v1/repositories/repo/learning_resource_exports/user/',
        type: 'GET',
        responseText: {
          "count": 3,
          "next": null,
          "previous": null,
          "results": [
            {"id": response1.id},
            {"id": response2.id},
            {"id": response3.id}]
        }
      });
      TestUtils.initMockjax({
        url: '/api/v1/repositories/repo/learning_resources/?id=123%2C345%2C789',
        type: 'GET',
        responseText: {
          "count": 3,
          "next": null,
          "previous": null,
          "results": [
            response1,
            response2,
            response3
          ]
        }
      });

      var afterMount = function (component) {
        var node = React.findDOMNode(component);
        // Wait for GET exports and GET related learning resources.
        waitForAjax(2, function () {
          assert.deepEqual(
            component.state.exportsSelected,
            [response1.id, response2.id, response3.id]
          );

          // Deselect first and second
          $($(node).find("ins")[0]).click();
          $($(node).find("ins")[1]).click();

          component.forceUpdate(function () {
            assert.deepEqual(
              component.state.exportsSelected,
              [response3.id]
            );

            // Select first one
            $($(node).find("ins")[1]).click();
            component.forceUpdate(function () {
              assert.deepEqual(
                component.state.exportsSelected,
                [response3.id, response2.id]
              );
              done();
            });
          });
        });
      };

      React.addons.TestUtils.renderIntoDocument(
        <ExportsComponent
          repoSlug="repo"
          loggedInUser="user"
          ref={afterMount}
          />
      );
    });
  }
);
