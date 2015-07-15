define("lr_exports",
  ['reactaddons', 'jquery', 'lodash', 'utils'], function (React, $, _, Utils) {
  'use strict';

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
        thiz.setState({exports: learningResources});
      })
      .fail(function() {
        thiz.setState({
          messageText: undefined,
          errorText: "Unable to load exports"
        });
      });
    },
    render: function() {
      var errorBox = null;
      if (this.state.errorText !== undefined) {
        errorBox = <div className="alert alert-danger alert-dismissible">
          {this.state.errorText}
        </div>;
      }
      var messageBox = null;
      if (this.state.messageText !== undefined) {
        messageBox = <div className="alert alert-success alert-dismissible">
          {this.state.messageText}
          </div>;
      }

      var exports = _.map(this.state.exports, function(ex) {
        return <li key={ex.id}>{ex.title}</li>;
      });

      return <div>
        {errorBox}
        {messageBox}
        <ul>
        {exports}
        </ul>
        </div>;
    },
    getInitialState: function() {
      return {
        errorText: undefined,
        messageText: undefined,
        exports: []
      };
    }
  });

  return {
    ExportsComponent: ExportsComponent,
    loader: function(repoSlug, loggedInUser, container) {
      React.unmountComponentAtNode(container);
      React.render(
        <ExportsComponent repoSlug={repoSlug} loggedInUser={loggedInUser} />,
        container
      );
    }
  };
});
