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

      return $.get(url)
        .then(function (data) {
          // some point soon we won't need this extra call
          var promises = _.map(data.results, function (vocabulary) {
            return $.get("/api/v1/repositories/" + repoSlug +
              "/vocabularies/" + vocabulary.slug + "/terms/")
              .then(function (result) {
                return {terms: result.results, vocabulary: vocabulary};
              });
          });

          return $.when.apply($, promises).then(function () {
            var args;
            if (promises.length === 1) {
              args = [arguments[0]];
            } else {
              args = arguments;
            }
            return _.map(args, function (obj) {
              var terms = obj.terms;
              var vocabulary = obj.vocabulary;

              return {
                vocabulary: vocabulary,
                terms: terms
              };
            });
          });
        });
    }
  };
});
