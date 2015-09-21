define(['QUnit', 'jquery', 'react', 'lodash', 'learning_resources', 'xml_panel',
  'test_utils', 'jquery_mockjax'], function(
  QUnit, $, React, _, LearningResources, XmlPanel, TestUtils) {
  'use strict';

  var waitForAjax = TestUtils.waitForAjax;

  var learningResourceResponse = {
    "id": 1,
    "learning_resource_type": "course",
    "static_assets": [],
    "title": "title",
    "materialized_path": "/course",
    "content_xml": "<course />",
    "url_path": "",
    "parent": null,
    "copyright": "",
    "xa_nr_views": 0,
    "xa_nr_attempts": 0,
    "xa_avg_grade": 0.0,
    "xa_histogram_grade": 0.0,
    "terms": ["required"]
  };

  QUnit.test(
    'Textarea should be selected',
    function(assert) {
      var done = assert.async();

      var afterMount = function(component) {
        var $node = $(React.findDOMNode(component));

        // wait for calls to populate form
        waitForAjax(1, function () {
          var $selectLink = $node.find("#copy-textarea-xml");
          var textarea = $node.find(".textarea-xml")[0];

          textarea.value = learningResourceResponse.content_xml;

          textarea.selectionEnd = 0;

          assert.equal(textarea.selectionStart, 0);
          assert.equal(textarea.selectionEnd, 0);

          React.addons.TestUtils.Simulate.click($selectLink[0]);

          assert.equal(textarea.selectionStart, 0);
          assert.equal(textarea.selectionEnd, 10);

          $("#testingDiv").remove();
          done();
        });
      };

      // for selection testing to work this needs to be in the DOM
      $("body").append($("<div id='testingDiv'>TEST</div>"));

      React.render(<XmlPanel.XmlPanel repoSlug="repo"
        learningResourceId="1"
        ref={afterMount} />, $("#testingDiv")[0]);
    }
  );

});
