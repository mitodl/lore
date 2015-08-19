define("utils", ["jquery", "lodash", "react", "select2"],
  function ($, _, React) {
  'use strict';

  /**
   * Get a collection from the REST API
   * @param {string} url The URL of the collection (may be part way through)
   * @param {array} [previousItems] If defined, the items previously collected
   * @returns {Promise} A promise evaluting to the array of items
   * in the collection
   */
  var _getCollection = function(url, previousItems) {
    if (previousItems === undefined) {
      previousItems = [];
    }

    return $.get(url).then(function (results) {
      if (results.next !== null) {
        return _getCollection(
          results.next, previousItems.concat(results.results));
      }

      return previousItems.concat(results.results);
    });
  };

  /**
   * Component for message divs. This takes one property. Use like:
   *   <StatusBox message={{error: "Error message"}} />
   * or for a regular message:
   *   <StatusBox message="Hello, world!" />
   */
  var StatusBox = React.createClass({
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

  /**
   * Component for checkboxes using ICheckbox and integrating with React
   * appropriately.
   */
  var ICheckbox = React.createClass({
    // onChange is set here to silence React warnings. We're using
    // ifToggled instead.
    render: function() {
      return <span><input {...this.props}
                    onChange={this.handleChange}
                    type="checkbox"
        /></span>;
    },
    handleChange: function(e) {
      if (this.props.onChange !== undefined) {
        this.props.onChange(e);
      }
    },
    attachHandler: function() {
      var node = React.findDOMNode(this);
      var thiz = this;
      $(node).off('ifToggled');
      $(node).on('ifToggled', function(e) {
        thiz.handleChange(e);
      });
      $(node).iCheck({
        checkboxClass: 'icheckbox_square-blue',
        radioClass: 'iradio_square-blue'
      });
      $(node).iCheck(this.props.checked ? "check" : "uncheck");
    },
    componentDidMount: function() {
      this.attachHandler();
    },
    componentDidUpdate: function() {
      this.attachHandler();
    }
  });

  /**
   * Component for Select2 select elements.
   */
  var Select2 = React.createClass({
    render: function() {
      return <span>
        <select {...this.props} onChange={function() {}} />
      </span>;
    },
    handleChange: function(e) {
      if (this.props.onChange !== undefined) {
        this.props.onChange(e);
      }
    },
    applySelect2: function () {
      // This function can be used only if the component has been mounted
      var thiz = this;
      var isMultiTerms = this.props.multiple;

      // Either use the value set when the component is instantiated, or set a default.
      var allowClear = this.props.allowClear;
      if (this.props.allowClear === undefined) {
        allowClear = !isMultiTerms;
      }

      // Apply select2 to the right elements
      var parent = React.findDOMNode(this);
      var $select = $(parent).find('select').first();

      // HACK to position dropdown below select in DOM so that
      // it won't attach event handlers all the way up and prevent
      // correct operation of the scrollbar.
      var Select2Utils = $.fn.select2.amd.require("select2/utils");
      var DropdownAdapter = $.fn.select2.amd.require("select2/dropdown");
      var AttachContainer = $.fn.select2.amd.require(
        "select2/dropdown/attachContainer");
      var DropdownSearch = $.fn.select2.amd.require(
        "select2/dropdown/search");
      var CustomAdapter = Select2Utils.Decorate(
        Select2Utils.Decorate(DropdownAdapter, DropdownSearch),
        AttachContainer
      );

      $select.select2({
        multiple: isMultiTerms,
        data: this.props.options,
        placeholder: this.props.placeholder,
        allowClear: allowClear,
        theme: "bootstrap",
        dropdownAdapter: CustomAdapter
      }).val(this.props.values)
        .trigger('change')
        .on('change', function (e) {
          thiz.handleChange(e);
        });
    },
    componentDidMount: function() {
      this.applySelect2();
    },
    componentDidUpdate: function() {
      this.applySelect2();
    },
    componentWillUpdate: function() {
      var node = React.findDOMNode(this);
      var $select = $(node).find('select').first();
      $select.off('change');

      var select2 = $select.data('select2');
      // HACK: workaround to prevent unselect and related events
      // from executing.
      select2.$container.removeClass('select2-container--open');
      if (select2 !== null && select2 !== undefined) {
        // HACK: workaround to prevent toggleDropdown from executing on
        // destroyed object.
        select2.options.set('disabled', true);
        select2.destroy();
      }

      // The select2 widget should get recreated in applySelect2 so
      // it shouldn't matter that we just made these modifications.
    }
  });

  return {
    getCollection: _getCollection,
    /**
     * Get vocabularies and terms from API
     * @param {string} repoSlug Repository slug
     * @param {string} [learningResourceType] Optional filter
     * @returns {Promise} A promise evaluating to vocabularies and terms
     */
    getVocabulariesAndTerms: function (repoSlug, learningResourceType) {
      var url = '/api/v1/repositories/' + repoSlug + '/vocabularies/';
      if (learningResourceType) {
        url += "?type_name=" + encodeURIComponent(learningResourceType);
      }

      return _getCollection(url).then(function(vocabs) {
        return _.map(vocabs, function(vocab) {
          return {
            vocabulary: vocab,
            terms: vocab.terms
          };
        });
      });
    },
    StatusBox: StatusBox,
    ICheckbox: ICheckbox,
    Select2: Select2
  };
});
