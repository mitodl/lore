define(['QUnit', 'jquery', 'setup_manage_taxonomies', 'reactaddons',
  'jquery_mockjax'], function(QUnit, $, ManageTaxonomies, React) {
  'use strict';

  var VocabularyComponent = ManageTaxonomies.VocabularyComponent;
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
        "slug": "ease",
        "label": "ease",
        "weight": 1
      },
      {
        "id": 2,
        "slug": "ease2",
        "label": "ease2",
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
      $.mockjax({
        url: "/api/v1/repositories/*/vocabularies/*/terms/",
        contentType: "application/json; charset=utf-8",
        responseText: addTermResponse,
        responseTime: 0,
        dataType: 'json'
      });
      $.ajaxSetup({async: false});
    },
    afterEach: function() {
      $.mockjax.clear();
      $.ajaxSetup({async: true});
    }
  });
  QUnit.test('Assert that VocabularyComponent renders properly',
    function(assert) {
      assert.ok(VocabularyComponent, "class object not found");
      //assert.async();
      var vocabularyComponentRendered = React.addons.TestUtils.
        renderIntoDocument(
          <VocabularyComponent
            vocabulary={vocabulary}
            terms={vocabulary.terms}
            reportError={reportError}
            repoSlug="repo"
          />
        );
      var randomEvent = $.Event("keyup", {keyCode: 64});
      var eventEnter = $.Event("keyup", {keyCode: 13});

      vocabularyComponentRendered.onEnterPress(randomEvent);
      assert.equal(vocabularyComponentRendered.state.terms.length, 2);

      vocabularyComponentRendered.onEnterPress(eventEnter);
      assert.equal(vocabularyComponentRendered.state.terms.length, 3);
      assert.equal(
        addTermResponse.id,
        vocabularyComponentRendered.state.terms[2].id
      );
    }
  );
});
