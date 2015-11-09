define("exports_header", ["react"], function(React) {
  'use strict';

  return React.createClass({
    render: function() {
      if (this.props.exportCount > 0) {
        return <h1>Export ({this.props.exportCount}) </h1>;
      }
      return <h1>Export</h1>;
    }
  });
});
