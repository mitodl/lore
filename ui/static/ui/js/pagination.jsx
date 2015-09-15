define('pagination', ['jquery', 'lodash', 'react'], function ($, _, React) {
  'use strict';

  var Pagination = React.createClass({
    mixins: [React.addons.LinkedStateMixin],
    getInitialState: function() {
      return {
        isEditing: false,
        textPageNum: this.props.pageNum
      };
    },
    render: function() {
      if (this.props.numPages <= 1) {
        // No pages to display
        return null;
      }

      var previousLink = null;
      if (this.props.pageNum > 1) {
        previousLink = <a href="#" onClick={this.goToPrevious}>
          <i className="fa fa-angle-left" />
        </a>;
      }

      var center = null;
      if (this.state.isEditing) {
        center = <input
          type="number"
          ref={this.focusHandler}
          size="10"
          className="form-control repo-page-status"
          valueLink={this.linkState('textPageNum')}
          onKeyUp={this.handleKeyup}
          />;
      } else {
        center = <a className="repo-page-status" href="#"
                    onClick={this.startEditing}>
          Page {this.props.pageNum} of {this.props.numPages}
        </a>;
      }
      var nextLink = null;
      if (this.props.pageNum <= this.props.numPages - 1) {
        nextLink = <a href="#" onClick={this.goToNext}>
          <i className="fa fa-angle-right" />
        </a>;
      }

      return <span>
        {previousLink}
        {center}
        {nextLink}
      </span>;
    },
    focusHandler: function(component) {
      var $node = $(React.findDOMNode(component));
      $node.focus();
      var thiz = this;
      $node.focusout(function() {
        thiz.goTo(thiz.state.textPageNum);
      });
    },
    goToPrevious: function(e) {
      e.preventDefault();
      this.goTo(this.props.pageNum - 1);
    },
    goToNext: function(e) {
      e.preventDefault();
      this.goTo(this.props.pageNum + 1);
    },
    goTo: function(pageNum) {
      if (!this.isMounted()) {
        return;
      }
      this.setState({
        isEditing: false
      });
      if (pageNum >= 1 && pageNum <= this.props.numPages &&
        pageNum !== this.props.pageNum) {
        this.props.updatePage(pageNum);
      } else {
        // Reset page number
        this.setState({
          textPageNum: this.props.pageNum
        });
      }
    },
    startEditing: function(e) {
      e.preventDefault();
      this.setState({
        isEditing: true
      });
    },
    handleKeyup: function(e) {
      if (e.key === "Enter") {
        e.preventDefault();
        this.goTo(this.state.textPageNum);
      }
    }
  });

  var loader = function(pageNum, numPages, updatePage, container) {
    React.render(<Pagination
      numPages={numPages}
      pageNum={pageNum}
      updatePage={updatePage}
      />, container);
  };

  return {
    Pagination: Pagination,
    loader: loader
  };
});
