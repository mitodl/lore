define("infinite_list", ["react", "react_infinite", "lodash", "jquery"],
  function(React, Infinite, _, $) {
    'use strict';

    /**
     * A list which connects to our collection APIs and grows as the user
     * scrolls down.
     */
    return React.createClass({
      getInitialState: function () {
        return {
          elements: [],
          isInfiniteLoading: false,
          next: this.props.url
        };
      },
      componentDidMount: function () {
        this.loadPage();
      },
      loadPage: function () {
        var thiz = this;

        if (this.state.next === null) {
          this.setState({
            isInfiniteLoading: false
          });
          return;
        }

        $.get(this.state.next).then(function (results) {
          thiz.setState({
            elements: thiz.state.elements.concat(results.results),
            next: results.next,
            isInfiniteLoading: false
          });
        }).fail(function (err) {
          thiz.setState({
            isInfiniteLoading: false
          });
          thiz.props.onError(err);
        });
      },
      handleInfiniteLoad: function () {
        this.setState({
          isInfiniteLoading: true
        });
        this.loadPage();
      },
      render: function () {
        var spinner = <div className="infinite-item-list">Loading...</div>;
        var elements = _.map(this.state.elements, this.props.makeElement);

        return <div className="infinite-list">
          <Infinite
            onInfiniteLoad={this.handleInfiniteLoad}
            loadingSpinnerDelegate={spinner}
            isInfiniteLoading={this.state.isInfiniteLoading}
            infiniteLoadBeginBottomOffset={this.props.containerHeight - 50}
            {...this.props}>
            {elements}
          </Infinite>
        </div>;
      }
    });
  }
);
