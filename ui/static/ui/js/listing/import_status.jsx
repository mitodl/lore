define("import_status", ["React", "lodash", "jquery", "utils",
  "react_spinner", "status_box"],
  function (React, _, $, Utils, ReactSpinner, StatusBox) {
    'use strict';

    return React.createClass({
      getInitialState: function () {
        return {
          importTasks: {},
          hasRefreshed: false
        };
      },
      updateImportStatus: function () {
        var thiz = this;

        Utils.getCollection("/api/v1/tasks/").then(function (tasks) {
          // Only deal with tasks on this repo that deal with imports.

          tasks = _.filter(tasks, function(task) {
            return (task.task_type === 'import_course' &&
              task.task_info.repo_slug === thiz.props.repoSlug);
          });
          var tasksMap = {};
          _.each(tasks, function (task) {
            tasksMap[task.id] = task;
          });
          thiz.setState({importTasks: tasksMap});

          var notProcessing = _.filter(tasks, function (task) {
            return task.status === 'success' || task.status === 'failure';
          });

          var deferred = $.Deferred();

          // Delete one after another to avoid race conditions with
          // Django session.
          _.each(notProcessing, function (task) {
            deferred.then(function () {
              return $.ajax({
                method: 'DELETE',
                url: '/api/v1/tasks/' + task.id + '/'
              });
            });
          });
          deferred.resolve();

          var numProcessing = _.filter(tasks, function (task) {
            return task.status === 'processing';
          }).length;
          if (numProcessing > 0) {
            thiz.setState({hasRefreshed: true});
            setTimeout(thiz.updateImportStatus, 3000);
          } else {
            if (thiz.state.hasRefreshed) {
              // There were tasks and they're finished now so we should refresh.
              thiz.props.refreshFromAPI();
            }
          }
        });
      },
      componentDidMount: function () {
        this.updateImportStatus();
      },
      render: function () {
        var numSuccessful = _.filter(this.state.importTasks, function (task) {
          return task.status === 'success';
        }).length;
        var numProcessing = _.filter(this.state.importTasks, function (task) {
          return task.status === 'processing';
        }).length;

        var importWord = function (n) {
          if (n === 1) {
            return "import";
          } else {
            return "imports";
          }
        };

        var successMessage;
        if (numSuccessful !== 0) {
          successMessage = <StatusBox
            message={numSuccessful + ' ' +
              importWord(numSuccessful) + ' finished'} />;
        }
        var progressMessage;
        if (numProcessing !== 0) {
          // Use a table for vertical centering
          progressMessage = <table>
            <tr>
              <td>
              {numProcessing + ' ' + importWord(numProcessing) + ' processing'}
              </td>
              <td>
              <ReactSpinner
                position="relative"
                speed={2}
                scale={0.3}
              />
              </td>
            </tr>
          </table>;
        }

        var failed = _.filter(this.state.importTasks, function (task) {
          return task.status === 'failure';
        });
        var errorMessages = [];
        _.each(failed, function (task) {
          errorMessages.push(
            <p key={errorMessages.length}>
              {"Import failed: " + task.result.error}
            </p>
          );
        });

        var errorMessage;
        if (errorMessages.length > 0) {
          errorMessage = <StatusBox message={{error: errorMessages}} />;
        }

        return <span>
          {successMessage}
          {errorMessage}
          {progressMessage}
        </span>;
      }
    });
  }
);
