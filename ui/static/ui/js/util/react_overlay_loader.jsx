define("react_overlay_loader", ["react", "react_spinner"],
  function (React, ReactSpinner) {
    'use strict';

    /**
     * Adapted from react-loader
     * https://github.com/quickleft/react-loader
     */
    return React.createClass({
      render: function () {
        var loader;
        var opacity = 1;

        if (!this.props.loaded) {
          loader = <ReactSpinner />;
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
