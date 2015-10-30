define('static_assets', [
  'react', 'jquery', 'lodash', 'status_box', 'infinite_list'],
  function (React, $, _, StatusBox, InfiniteList) {
  'use strict';

  // Guess at a good value for the height of each element. Infinite requires
  // an elementHeight for each item. If we wanted to do a per item elementHeight
  // we could make this a list instead.
  var elementHeight = 50;

  var StaticAssetsPanel = React.createClass({
    getInitialState: function() {
      return {
        results: []
      };
    },
    makeElement: function(asset) {
      return <li className="list-group-item" key={asset.asset}
                 style={{height: elementHeight}}>
        <a href={asset.asset}>{asset.name}</a>
      </li>;
    },
    render: function () {
      var url = "/api/v1/repositories/" + this.props.repoSlug +
          "/learning_resources/" +
          this.props.learningResourceId + "/static_assets/";

      // Infinite requires you to specify a containerHeight. This value
      // is a guess at how big the area should be relative to the height.
      var containerHeight = $(window).height() - 200;

      return <div>
        <StatusBox message={this.state.message} />
        <ul className="list-group">
          <InfiniteList
            onError={this.onError}
            url={url}
            makeElement={this.makeElement}
            containerHeight={containerHeight}
            elementHeight={elementHeight}
            />
        </ul>
      </div>;
    },
    onError: function() {
      this.setState({
        message: {
          error: "Unable to read information about static assets."
        }
      });
    }
  });

  return {
    StaticAssetsPanel: StaticAssetsPanel,
    loader: function (repoSlug, learningResourceId, container) {
      // Unmount and remount the component to ensure that its state
      // is always up to date with the rest of the app.
      React.unmountComponentAtNode(container);
      React.render(<StaticAssetsPanel
        repoSlug={repoSlug}
        learningResourceId={learningResourceId}
        key={[repoSlug, learningResourceId]}
        />, container);
    }
  };
});
