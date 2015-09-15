define("lr_exports",
  ['react', 'jquery', 'lodash', 'utils', 'icheck'],
  function (React, $, _, Utils) {
  'use strict';

  var StatusBox = Utils.StatusBox;
  var ICheckbox = Utils.ICheckbox;

  var ExportsHeader = React.createClass({
    render: function() {
      if (this.props.exportCount > 0) {
        return <h1>Export ({this.props.exportCount}) </h1>;
      }
      return <h1>Export</h1>;
    }
  });
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
            var exportsSelected = _.map(learningResources, function(resource) {
              return resource.id;
            });
            thiz.setState({
              exports: learningResources,
              exportButtonVisible: true,
              exportsSelected: exportsSelected
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
    updateChecked: function(exportId, event) {
      if (event.target.checked) {
        this.setState({
          exportsSelected: _.uniq(this.state.exportsSelected.concat([exportId]))
        });
      } else {
        this.setState({
          exportsSelected: _.remove(this.state.exportsSelected, function(id) {
            return id !== exportId;
          })
        });
      }
    },
    render: function() {
      var thiz = this;

      var exports = _.map(this.state.exports, function(ex) {
        var checked = _.includes(thiz.state.exportsSelected, ex.id);
        return <li key={ex.id}>
            <ICheckbox value={ex.id} checked={checked}
                       onChange={_.curry(thiz.updateChecked)(ex.id)} />
          <label>
            {ex.title}
          </label>
          <span className="tile-blurb">{ex.description}</span>
          </li>;
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

      var collisionMessage = null;
      if (this.state.collision) {
        collisionMessage = "WARNING: some static assets had the " +
          "same filename and were automatically renamed.";
      }

      return <div>
        <StatusBox message={this.state.message} />
        <ul className="icheck-list export-list">
        {exports}
        </ul>
        {collisionMessage}
        {urlLink}
        {iframe}
        <button className="btn btn-lg btn-primary"
                onClick={this.startArchiving}
                style={{display: displayExportButton}}
          >Export Selected Items</button>
        </div>;
    },
    getInitialState: function() {
      return {
        exports: [],
        exportButtonVisible: false, // This will become true when exports load.
        exportsSelected: [],
        collision: false
      };
    },
    startArchiving: function() {
      var thiz = this;

      $.ajax({
          type: "POST",
          url: "/api/v1/repositories/" + this.props.repoSlug +
          "/learning_resource_export_tasks/",
          data: JSON.stringify({ids: this.state.exportsSelected}),
          contentType: 'application/json'
        }
      ).then(function(result) {
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
                exports: [],
                exportsSelected: []
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
              url: result.url,
              collision: result.collision
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
    },
    loadExportsHeader: function(exportCount, container) {
      React.unmountComponentAtNode(container);
      React.render(
        <ExportsHeader exportCount={exportCount} />,
        container
      );
    }
  };
});
