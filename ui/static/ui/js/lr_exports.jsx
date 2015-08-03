define("lr_exports",
  ['reactaddons', 'jquery', 'lodash', 'utils'], function (React, $, _, Utils) {
  'use strict';

  var StatusBox = Utils.StatusBox;

  /**
   * A React component which shows the list of exports
   * and provides a way to export these learning resources in bulk.
   */
  var ExportsComponent = React.createClass({
    componentDidMount: function() {

      var thiz = this;
      Utils.getCollection("/api/v1/repositories/" + thiz.props.repoSlug +
        "/learning_resource_exports/" + thiz.props.loggedInUser + "/"
      ).then(function (ids) {
        if (!thiz.isMounted()) {
          return;
        }
        ids = _.map(ids, function (obj) {
          return obj.id;
        });
        if (ids.length > 0) {
          return Utils.getCollection("/api/v1/repositories/" +
            thiz.props.repoSlug +
            "/learning_resources/?id=" + encodeURIComponent(ids.join(","))
          );
        } else {
          return [];
        }
      })
      .then(function (learningResources) {
          if (!thiz.isMounted()) {
            return;
          }
          if (learningResources.length > 0) {
            thiz.setState({
              exports: learningResources,
              exportButtonVisible: true
            });
          }
        })
      .fail(function() {
        if (!thiz.isMounted()) {
          return;
        }

        thiz.setState({
          message: {
            error: "Unable to load exports."
          }
        });
      });
    },
    render: function() {
      var exports = _.map(this.state.exports, function(ex) {
        return <li key={ex.id}>{ex.title}</li>;
      });

      var urlLink = null;
      var iframe = null;
      if (this.state.url !== undefined) {
        urlLink = <div>
          Resources are ready for download. If download has not started
          click <a className="cd-btn" target="_blank"
                   href={this.state.url}>here</a> to download
          learning resources.
        </div>;
        iframe = <iframe style={{display: "none"}} src={this.state.url} />;
      }

      var displayExportButton = "block";
      if (!this.state.exportButtonVisible) {
        displayExportButton = "none";
      }

      return <div>
        <StatusBox message={this.state.message} />
        <ul>
        {exports}
        </ul>
        {urlLink}
        {iframe}
        <button className="btn btn-primary"
                onClick={this.startArchiving}
                style={{display: displayExportButton}}
          >Export Resources</button>
        </div>;
    },
    getInitialState: function() {
      return {
        exports: [],
        exportButtonVisible: false // This will become true when exports load.
      };
    },
    startArchiving: function() {
      var thiz = this;

      var exportIds = _.map(this.state.exports, function(ex) {
        return ex.id;
      });

      $.post("/api/v1/repositories/" + this.props.repoSlug +
        "/learning_resource_export_tasks/", exportIds).then(function(result) {
        if (!thiz.isMounted()) {
          return;
        }

        thiz.setState({
          exportButtonVisible: false
        });

        thiz.updateStatus(result.id);
      }).fail(function() {
        if (!thiz.isMounted()) {
          return;
        }

        thiz.setState({
          message: {
            error: "Error preparing learning resources for download."
          }
        });
      });
    },
    updateStatus: function(taskId) {
      var thiz = this;

      $.get("/api/v1/repositories/" + this.props.repoSlug +
        "/learning_resource_export_tasks/" + taskId + "/")
        .done(function (result) {
          if (!thiz.isMounted()) {
            return;
          }

          if (result.status === "success") {
            thiz.setState({
              exportButtonVisible: false
            });

            $.ajax({
              type: "DELETE",
              url: "/api/v1/repositories/" + thiz.props.repoSlug +
              "/learning_resource_exports/" + thiz.props.loggedInUser + "/"
            }).then(function() {
              thiz.setState({
                exports: []
              });
              thiz.props.clearExports();
            }).fail(function() {
              thiz.setState({
                message: {
                  error: "Error clearing learning resource exports."
                }
              });
            });

            thiz.setState({
              url: result.url
            });
          } else if (result.status === "processing") {
            setTimeout(function() {
              thiz.updateStatus(taskId);
            }, thiz.props.interval);
          } else {
            thiz.setState({
              message: {
                error: "Error occurred preparing " +
                "learning resources for download."
              }
            });
          }
        }).fail(function() {
          if (!thiz.isMounted()) {
            return;
          }

          thiz.setState({
            message: {
              error: "Error occurred preparing " +
              "learning resources for download."
            }
          });
        });
    },
  });

  return {
    ExportsComponent: ExportsComponent,
    loader: function(repoSlug, loggedInUser, clearExports, container) {
      React.unmountComponentAtNode(container);
      React.render(
        <ExportsComponent repoSlug={repoSlug} loggedInUser={loggedInUser}
                          interval={1000}
          clearExports={clearExports}
          />,
        container
      );
    }
  };
});
