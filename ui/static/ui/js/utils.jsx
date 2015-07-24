define("utils", ["jquery", "lodash", "reactaddons"], function ($, _, React) {
  'use strict';

  /**
   * Get a collection from the REST API
   * @param {string} url The URL of the collection (may be part way through)
   * @param {array} [previousItems] If defined, the items previously collected
   * @returns {Promise} A promise evaluting to the array of items
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

  /**
   * Component for message divs. This takes one property. Use like:
   *   <StatusBox message={{error: "Error message"}} />
   * or for a regular message:
   *   <StatusBox message="Hello, world!" />
   */
  var StatusBox = React.createClass({
    render: function() {
      if (!this.props || !this.props.message) {
        return null;
      }

      if (this.props.message.error !== undefined) {
        return <div className="alert alert-danger alert-dismissible">
          {this.props.message.error}
        </div>;
      }

      if (this.props.message !== undefined) {
        return <div className="alert alert-success alert-dismissible">
          {this.props.message}
          </div>;
      }

      return null;
    }
  });

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
    StatusBox: StatusBox
  };
});
