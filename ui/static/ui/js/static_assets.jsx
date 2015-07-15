define('static_assets', [
  'reactaddons', 'jquery', 'lodash', 'utils'], function (React, $, _, Utils) {
  'use strict';

  var StaticAssetsPanel = React.createClass({
    getInitialState: function() {
      return {
        results: []
      };
    },
    componentDidMount: function () {
      var thiz = this;

      Utils.getCollection("/api/v1/repositories/" + this.props.repoSlug +
          "/learning_resources/" +
          this.props.learningResourceId + "/static_assets/")
          .done(function (assets) {
            if (!thiz.isMounted()) {
              // In time AJAX call happens component may become unmounted
              return;
            }

            thiz.setState({
              results: assets
            });
          })
          .fail(function () {
            thiz.setState({
              errorText: "Unable to read information about static assets.",
              messageText: undefined
            });
          });
    },
    render: function () {
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

      var staticAssets = _.map(this.state.results, function (asset) {
        return <li className="list-group-item" key={asset.asset}>
            <a href={asset.asset}>{asset.name}</a>
          </li>;
      });

      return <div>
        {errorBox}
        {messageBox}
        <ul className="list-group">
          {staticAssets}
        </ul>
      </div>;
    }
  });

  return {
    StaticAssetsPanel: StaticAssetsPanel,
    loader: function (repoSlug, learningResourceId, container) {
      React.render(<StaticAssetsPanel
        repoSlug={repoSlug} learningResourceId={learningResourceId}
        key={[repoSlug, learningResourceId]}
        />, container);
    }
  };
});
