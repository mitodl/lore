define("term_list_item", ["react"],
  function (React) {
    'use strict';

    return React.createClass({
      render: function () {
        return (
          <li className="applied-term list-group-item">
            <strong>{this.props.label}: </strong> {this.props.terms}
          </li>
        );
      }
    });
  }
);
