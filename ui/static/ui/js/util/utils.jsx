define("utils", ["jquery", "lodash", "react", "confirmation_dialog"],
  function ($, _, React, ConfirmationDialog) {
  'use strict';

  /**
   * Get a collection from the REST API all at once. Provides a promise
   * of all items in collection.
   *
   * @param {string} url The URL of the collection (may be part way through)
   * @param {array} [previousItems] If defined, the items previously collected
   * @returns {Promise} A promise evaluating to the array of items
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
    showConfirmationDialog: function(options, container) {
      React.unmountComponentAtNode(container);
      React.render(
        <ConfirmationDialog {...options} />,
        container
      );
    }
  };
});
