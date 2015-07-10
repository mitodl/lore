define(['QUnit', 'jquery', 'setup_manage_taxonomies', 'reactaddons',
  'test_utils'],
  function(QUnit, $, ManageTaxonomies, React, TestUtils) {
  'use strict';

  var VocabularyComponent = ManageTaxonomies.VocabularyComponent;
  var waitForAjax = TestUtils.waitForAjax;

  var addTermResponse = {
    "id": 9,
    "slug": "aa",
    "label": "aa",
    "weight": 1
  };
  var vocabulary = {
    "id": 1,
    "slug": "difficulty",
    "name": "difficulty",
    "description": "easy",
    "vocabulary_type": "f",
    "required": false,
    "weight": 2147483647,
    "terms": [
      {
        "id": 1,
        "slug": "easy",
        "label": "easy",
        "weight": 1
      },
      {
        "id": 2,
        "slug": "difficult",
        "label": "difficult",
        "weight": 1
      }
    ]
  };
  function reportError(msg) {
    if (msg) {
      console.error(msg);
    }
  }
  QUnit.module('Test taxonomies panel', {
    beforeEach: function() {
      TestUtils.setup();
      TestUtils.initMockjax({
        url: "/api/v1/repositories/*/vocabularies/*/terms/",
        responseText: addTermResponse,
        type: "POST"
      });
    },
    afterEach: function() {
      TestUtils.cleanup();
    }
  });

  QUnit.test('Assert that VocabularyComponent renders properly',
    function(assert) {
      assert.ok(VocabularyComponent, "class object not found");

      var done = assert.async();

      var addTermCalled = 0;
      var addTerm = function() {
        addTermCalled += 1;
      };

      var afterMount = function(component) {
        var node = React.findDOMNode(component);
        var textbox = $(node).find("input")[0];
        React.addons.TestUtils.Simulate.keyUp(textbox, {key: "x"});
        assert.equal(addTermCalled, 0);

        React.addons.TestUtils.Simulate.keyUp(textbox, {key: "Enter"});
        waitForAjax(1, function() {
          assert.equal(addTermCalled, 1);
          done();
        });
      };

      React.addons.TestUtils.
        renderIntoDocument(
          <VocabularyComponent
            vocabulary={vocabulary}
            terms={vocabulary.terms}
            reportError={reportError}
            addTerm={addTerm}
            repoSlug="repo"
            ref={afterMount}
          />
        );
    }
  );
});
