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
      var afterMount = function(component) {
        var randomEvent = $.Event("keyup", {keyCode: 64});
        var enterEvent = $.Event("keyup", {keyCode: 13});

        component.onEnterPress(randomEvent);
        assert.equal(component.state.terms.length, 2);

        component.onEnterPress(enterEvent);
        waitForAjax(1, function() {
          assert.equal(component.state.terms.length, 3);
          assert.equal(
            addTermResponse.id,
            component.state.terms[2].id);
          done();
        });
      };

      React.addons.TestUtils.
        renderIntoDocument(
          <VocabularyComponent
            vocabulary={vocabulary}
            terms={vocabulary.terms}
            reportError={reportError}
            repoSlug="repo"
            ref={afterMount}
          />
        );
    }
  );
});
