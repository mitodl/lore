define("select2_component", ["react", "jquery", "select2"],
  function (React, $) {
    'use strict';

    /**
     * Component for Select2 select elements.
     */
    return React.createClass({
      render: function () {
        return <span>
        <select {...this.props} onChange={function() {}}/>
      </span>;
      },
      handleChange: function (e) {
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
          tags: this.props.allowTags,
          theme: "bootstrap",
          dropdownAdapter: CustomAdapter
        }).val(this.props.values)
          .trigger('change')
          .on('change', function (e) {
            thiz.handleChange(e);
          });
      },
      componentDidMount: function () {
        this.applySelect2();
      },
      componentDidUpdate: function () {
        this.applySelect2();
      },
      componentWillUpdate: function () {
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

  }
);
