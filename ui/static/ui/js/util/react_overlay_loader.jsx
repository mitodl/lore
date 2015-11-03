define("react_overlay_loader", ["react", "spin"],
  function (React, Spinner) {
    'use strict';

    /**
     * Adapted from react-loader
     * https://github.com/quickleft/react-loader
     */
    return React.createClass({
      componentDidUpdate: function () {
        this.spin();
      },
      componentDidMount: function () {
        this.spin();
      },
      spin: function () {
        if (this.isMounted() && !this.props.loaded) {
          var target = React.findDOMNode(this.refs.loader);

          var spinner = new Spinner({zIndex: 0});
          spinner.spin(target);
        }
      },
      render: function () {
        var loader;
        var opacity = 1;

        if (!this.props.loaded) {
          loader = <div ref="loader"/>;
          opacity = 0.6;
        }
        var children;
        if (!this.props.hideChildrenOnLoad || this.props.loaded) {
          children = <div style={{opacity: opacity}}>
            {this.props.children}
          </div>;
        }
        return <div>{loader}
          {children}
        </div>;
      }
    });

  }
);
