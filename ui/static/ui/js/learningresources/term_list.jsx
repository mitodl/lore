define("term_list", ["react", "lodash", "term_list_item"],
  function (React, _, TermListItem) {
    'use strict';

    return React.createClass({
      render: function () {
        var appliedVocabularies = this.props.vocabs.map(function (vocab) {
          var selectedTermsLabels = _.pluck(
            _.filter(vocab.terms, function (term) {
              return _.indexOf(vocab.selectedTerms, term.slug) !== -1;
            }),
            'label'
          );
          var vocabularyName = vocab.vocabulary.name;

          if (selectedTermsLabels.length) {
            return (
              <TermListItem
                key={vocab.vocabulary.id}
                label={vocabularyName}
                terms={selectedTermsLabels.join(", ")}
                />
            );
          }
        });
        return (
          <div id="term-list-container" className="panel panel-default">
            <div className="panel-heading">
              Terms applied to this Learning Resource
            </div>
            <ul id="term-list" className="list-group">
              {appliedVocabularies}
            </ul>
          </div>
        );
      }
    });
  }
);
