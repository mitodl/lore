/**
 * Facet handling javascript module
 * @module facets
 */
define('facets', ['jquery', 'bootstrap', 'icheck'], function($) {
  'use strict';
  /**
     Takes a dom element and returns the string
     that makes up a facet querystring parameter
     @memberOf module:facets
     @param {Element} facetCheckbox - `<input type="checkbox">` checkbox with data about
       it's facet.
     @returns {string} Returns the querystring parameter for the facet.
   */
  var constructFacetQuery = function(facetCheckbox) {
    // Takes a dom element and returns the string
    // that makes up a facet querystring parameter
    var facet = $(facetCheckbox).data('facet-name');
    var facetValue = $(facetCheckbox).data('facet-value');
    return 'selected_facets=' + facet +  ':' + facetValue;
  };
  /**
     Checks all facets for ones that turned on, and sets their state
     to checked.
     @memberOf module:facets
     @param {string} currentQueryset - Current pages querystring
   */
  var checkFacets = function(currentQueryset) {
    // Check if a facet is enabled and check the box
    $('input.icheck-11').each(function() {
      if (currentQueryset.indexOf(constructFacetQuery(this)) > -1) {
        $(this).iCheck('check');
      }
    });
  };
  /**
     Add icheck and click handlers for all the checkboxes
     @memberOf module:facets
     @param {string} currentQueryset - Current pages querystring
   */
  var setupFacets = function(window) {
    var currentQueryset = $('#facet-panel').data('current-queryset');
    $('input.icheck-11').iCheck({
      checkboxClass: 'icheckbox_square-blue',
      radioClass: 'iradio_square-blue'
    });
    // Check facets before adding event handlers
    checkFacets(currentQueryset);
    $('input.icheck-11').on('ifChecked', function() {
      $('#progress-modal').modal();
      window.location = currentQueryset + constructFacetQuery(this);
    });
    $('input.icheck-11').on('ifUnchecked', function() {
      $('#progress-modal').modal();
      window.location = currentQueryset.replace(
        constructFacetQuery(this), ''
      );
    });
  };
  return {
    constructFacetQuery: constructFacetQuery,
    checkFacets: checkFacets,
    setupFacets: setupFacets
  };
});
