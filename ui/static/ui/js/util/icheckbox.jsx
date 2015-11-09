define("icheckbox", ["react", "jquery", "icheck"],
  function (React, $) {
    'use strict';

    /**
     * Component for checkboxes using ICheckbox and integrating with React
     * appropriately.
     */
    return React.createClass({
      // onChange is set here to silence React warnings. We're using
      // ifToggled instead.
      render: function () {
        return <span><input {...this.props}
          onChange={this.handleChange}
          type="checkbox"
          /></span>;
      },
      handleChange: function (e) {
        if (this.props.onChange !== undefined) {
          this.props.onChange(e);
        }
      },
      attachHandler: function () {
        var node = React.findDOMNode(this);
        var thiz = this;
        $(node).on('ifToggled', function (e) {
          thiz.handleChange(e);
        });
        $(node).iCheck({
          checkboxClass: 'icheckbox_square-blue',
          radioClass: 'iradio_square-blue'
        });
      },
      componentWillUpdate: function () {
        var node = React.findDOMNode(this);
        $(node).off('ifToggled');
      },
      componentDidMount: function () {
        this.attachHandler();
      },
      componentDidUpdate: function () {
        this.attachHandler();
      }
    });
  }
);
