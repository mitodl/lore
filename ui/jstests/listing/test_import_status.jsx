define(['QUnit', 'jquery', 'import_status', 'react',
    'test_utils'],
  function (QUnit, $, ImportStatus, React, TestUtils) {
    'use strict';

    var waitForAjax = TestUtils.waitForAjax;

    var TASK1_SUCCESS = {
      "id": "task1",
      "status": "success",
      "task_type": "import_course",
      "task_info": {
        "repo_slug": "repo"
      }
    };
    var OTHER_REPO_FAILURE = {
      "id": "task2",
      "status": "failure",
      "task_type": "import_course",
      "task_info": {
        "repo_slug": "otherrepo"
      }
    };
    var NOT_IMPORT_SUCCESS = {
      "id": "task4",
      "status": "success",
      "task_type": "reindex"
    };
    var TASK3_PROCESSING = {
      "id": "task3",
      "status": "processing",
      "task_type": "import_course",
      "task_info": {
        "repo_slug": "repo"
      }
    };
    var TASK3_SUCCESS = {
      "id": "task3",
      "status": "success",
      "task_type": "import_course",
      "task_info": {
        "repo_slug": "repo"
      }
    };
    var TASK3_FAILURE = {
      "id": "task3",
      "status": "failure",
      "task_type": "import_course",
      "task_info": {
        "repo_slug": "repo"
      },
      "result": {
        "error": "Task 3 failed"
      }
    };

    var makeCollectionResult = function(items) {
      return {
        "count": items.length,
        "next": null,
        "previous": null,
        "results": items
      };
    };

    QUnit.module('Test import status', {
      beforeEach: function () {
        TestUtils.setup();

        TestUtils.initMockjax({
          url: '/api/v1/tasks/',
          type: 'GET',
          responseText: makeCollectionResult([
            OTHER_REPO_FAILURE,
            NOT_IMPORT_SUCCESS,
            TASK3_PROCESSING
          ])
        });

        TestUtils.initMockjax({
          url: '/api/v1/tasks/task3/',
          type: 'DELETE'
        });
      },
      afterEach: function() {
        TestUtils.cleanup();
      }
    });

    QUnit.test('Assert that existing task is deleted',
      function(assert) {
        var done = assert.async();
        var refreshCount = 0;
        var refreshFromAPI = function() {
          refreshCount++;
        };
        TestUtils.replaceMockjax({
          url: '/api/v1/tasks/',
          type: 'GET',
          responseText: makeCollectionResult([
            TASK1_SUCCESS
          ])
        });
        TestUtils.initMockjax({
          url: '/api/v1/tasks/task1/',
          type: 'DELETE'
        });

        var afterMount = function(component) {
          waitForAjax(2, function () {
            // If we get 2 AJAX calls one of them should be a DELETE.
            assert.deepEqual(component.state, {
              "importTasks": {
                task1: TASK1_SUCCESS
              },
              "hasRefreshed": false
            });

            done();
          });
        };

        React.addons.TestUtils.renderIntoDocument(
          <ImportStatus
            repoSlug="repo"
            refreshFromAPI={refreshFromAPI}
            ref={afterMount}
          />
        );
      }
    );

    QUnit.test('Assert successful import status',
      function(assert) {
        var done = assert.async();

        var refreshCount = 0;
        var refreshFromAPI = function() {
          refreshCount++;
        };

        var afterMount = function(component) {
          waitForAjax(1, function() {
            assert.deepEqual(component.state, {
              "importTasks": {
                "task3": TASK3_PROCESSING
              },
              "hasRefreshed": true
            });

            TestUtils.replaceMockjax({
              url: '/api/v1/tasks/',
              type: 'GET',
              responseText: makeCollectionResult([
                OTHER_REPO_FAILURE,
                NOT_IMPORT_SUCCESS,
                TASK3_SUCCESS
              ])
            });

            waitForAjax(2, function() {
              // One ajax call to get tasks, one to delete.
              assert.deepEqual(component.state, {
                importTasks: {
                  task3: TASK3_SUCCESS
                },
                hasRefreshed: true
              });
              done();
            });
          });
        };

        React.addons.TestUtils.renderIntoDocument(
          <ImportStatus
            repoSlug="repo"
            refreshFromAPI={refreshFromAPI}
            ref={afterMount}
          />
        );
      }
    );

    QUnit.test('Assert import status of failure',
      function(assert) {
        var done = assert.async();

        var refreshCount = 0;
        var refreshFromAPI = function() {
          refreshCount++;
        };

        var afterMount = function(component) {
          waitForAjax(1, function() {
            assert.deepEqual(component.state, {
              "importTasks": {
                "task3": TASK3_PROCESSING
              },
              "hasRefreshed": true
            });

            TestUtils.replaceMockjax({
              url: '/api/v1/tasks/',
              type: 'GET',
              responseText: makeCollectionResult([
                OTHER_REPO_FAILURE,
                NOT_IMPORT_SUCCESS,
                TASK3_FAILURE
              ])
            });

            waitForAjax(2, function() {
              // One ajax call to get tasks, one to delete.
              assert.deepEqual(component.state, {
                importTasks: {
                  task3: TASK3_FAILURE
                },
                hasRefreshed: true
              });
              done();
            });
          });
        };

        React.addons.TestUtils.renderIntoDocument(
          <ImportStatus
            repoSlug="repo"
            refreshFromAPI={refreshFromAPI}
            ref={afterMount}
          />
        );
      }
    );
  }
);
