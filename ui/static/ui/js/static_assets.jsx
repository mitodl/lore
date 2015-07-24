define('static_assets', [
  'reactaddons', 'jquery', 'lodash', 'utils'], function (React, $, _, Utils) {
  'use strict';

  var StatusBox = Utils.StatusBox;

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
              message: {
                error: "Unable to read information about static assets."
              }
            });
          });
    },
    render: function () {
      var staticAssets = _.map(this.state.results, function (asset) {
        return <li className="list-group-item" key={asset.asset}>
            <a href={asset.asset}>{asset.name}</a>
          </li>;
      });

      return <div>
        <StatusBox message={this.state.message} />
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
