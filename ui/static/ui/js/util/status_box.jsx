define("status_box", ["react"], function(React) {
  'use strict';

  /**
   * Component for message divs. This takes one property. Use like:
   *   <StatusBox message={{error: "Error message"}} />
   * or for a regular message:
   *   <StatusBox message="Hello, world!" />
   */
  return React.createClass({
    render: function() {
      if (!this.props || !this.props.message) {
        return null;
      }

      if (this.props.message.error !== undefined) {
        return <div className="alert alert-danger alert-dismissible">
          {this.props.message.error}
        </div>;
      }

      if (this.props.message !== undefined) {
        return <div className="alert alert-success alert-dismissible">
          {this.props.message}
          </div>;
      }

      return null;
    }
  });

});
