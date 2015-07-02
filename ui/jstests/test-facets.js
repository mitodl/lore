define(['QUnit', 'jquery', 'facets', 'icheck'], function(QUnit, $, facets) {
  'use strict';
  var testQueryString = 'selected_facets=foo:bar';
  QUnit.test(
    'Test constructFacetQuery with given input element',
    function(assert) {
      var testData = $(
        '<input data-facet-name="foo" type="checkbox" data-facet-value="bar">'
      )[0];
      var facetQuery = facets.constructFacetQuery(testData);
      assert.equal(testQueryString, facetQuery);
    }
  );
  QUnit.test(
    'Test checkFacets with given input element',
    function(assert) {
      $(
        '<input id="foobar" type="checkbox"' +
          'class="icheck-11" data-facet-name="foo" data-facet-value="bar">'
      ).appendTo($('body'));
      $('#foobar').iCheck();
      facets.checkFacets(testQueryString);
      assert.ok($('#foobar').prop('checked'));
      $('#foobar').remove();
    }
  );
  QUnit.test(
    'Test setupFacets is working',
    function(assert) {
      $(
        '<div id="facet-panel" data-current-queryset="foobar"></div>'
      ).appendTo($('body'));

      $(
        '<input id="foobar" type="checkbox" class="icheck-11">'
      ).appendTo($('body'));
      // Make mock window for location changing
      var testWindow = {
        location: ''
      };
      testWindow.window = testWindow;
      facets.setupFacets(testWindow);
      assert.notEqual($('#foobar').find('ins'));
      // Check and assert
      $('#foobar').iCheck('check');
      assert.equal(
        testWindow.window.location,
        'foobarselected_facets=undefined:undefined'
      );
      $('#foobar').iCheck('uncheck');
      assert.equal(
        testWindow.window.location,
        'foobar'
      );
      $('#facet-panel').remove();
      $('#foobar').remove();
    }
  );
});
