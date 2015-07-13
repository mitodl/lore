define("utils", ["jquery", "lodash"], function ($, _) {
  'use strict';
  return {
    /**
     * Get vocabularies and terms from API
     * @param {string} repoSlug Repository slug
     * @param {string} [learningResourceType] Optional filter
     * @returns {Promise} A promise evaluating to vocabularies and terms
     */
    getVocabulariesAndTerms: function (repoSlug, learningResourceType) {
      var url = '/api/v1/repositories/' + repoSlug + '/vocabularies/';
      if (learningResourceType) {
        url += "?type_name=" + encodeURI(learningResourceType);
      }

      return $.get(url).then(function(results) {
        return _.map(results.results, function(result) {
          return {
            vocabulary: result,
            terms: result.terms
          };
        });
      });
    }
  };
});
