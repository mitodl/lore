define("react_spinner", ["react", "spin", "jquery"],
  function (React, Spinner, $) {
    'use strict';

    return React.createClass({
      spin: function () {
        if (this.isMounted()) {
          var target = React.findDOMNode(this);
          target.innerHTML = '';

          var spinner = this.makeSpinner();
          spinner.spin(target);
        }
      },
      makeSpinner: function() {
        var props = $.extend({}, this.props);
        if (props.zIndex === undefined) {
          props.zIndex = 0;
        }
        return new Spinner(props);
      },
      componentDidUpdate: function () {
        this.spin();
      },
      componentDidMount: function () {
        this.spin();
      },
      render: function() {
        var radius = this.makeSpinner().opts.radius;

        return <div style={{
          width: radius * 2,
          left: radius
        }}>
          </div>;
      }
    });
  }
);
