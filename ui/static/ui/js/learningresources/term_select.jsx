define("term_select", ["react", "lodash", "jquery", "select2_component"],
  function (React, _, $, Select2) {
    'use strict';

    return React.createClass({
      render: function () {
        var options = _.map(this.props.selectedVocabulary.terms,
          function (term) {
            return {
              id: term.slug,
              text: term.label
            };
          }
        );

        var currentVocabulary = {};
        var selectedVocabulary = this.props.selectedVocabulary;

        _.forEach(this.props.vocabs, function (vocab) {
          if (vocab.vocabulary.slug === selectedVocabulary.slug) {
            currentVocabulary = vocab;
            return false;
          }
        });

        var name = this.props.selectedVocabulary.name;
        var allowTags = false;
        if (this.props.selectedVocabulary.vocabulary_type === 'f') {
          allowTags = true;
        }
        var termId = "term-" + name;
        return <div className="form-group">
          <label htmlFor={termId}
                 className="col-sm-4 control-label">Terms</label>

          <div className="col-sm-6">
            <Select2
              key={name}
              id={termId}
              className="form-control"
              placeholder={"Select a value for " + name}
              options={options}
              onChange={this.handleChange}
              values={currentVocabulary.selectedTerms}
              multiple={this.props.selectedVocabulary.multi_terms}
              allowTags={allowTags}
              />
          </div>
        </div>;
      },

      handleChange: function (e) {
        var selectedValues = _.pluck(
          _.filter(e.target.options, function (option) {
            return option.selected && option.value !== null;
          }), 'value');

        // clear messages
        this.props.reportMessage(undefined);

        // check if the current vocabulary allows free tagging and in case add
        // the new tags before proceeding
        if (this.props.selectedVocabulary.vocabulary_type === 'f') {
          // extract the list of terms not in the vocabulary existing terms
          var termsSlugs = _.pluck(this.props.selectedVocabulary.terms, 'slug');
          var termsToCreate = _.filter(selectedValues, function (slug) {
            return !_.includes(termsSlugs, slug);
          });
          // if there are no new terms to create, set the state
          if (!termsToCreate.length) {
            this.props.setValues(
              this.props.selectedVocabulary.slug, selectedValues
            );
          } else {
            // otherwise create the terms and update the vocabularies
            // create the term
            var thiz = this;
            var API_ROOT_TERMS_URL = '/api/v1/repositories/' +
              thiz.props.repoSlug + '/vocabularies/' +
              thiz.props.selectedVocabulary.slug + "/terms/";
            thiz.props.setLoadedState(false);
            _.forEach(termsToCreate, function (termLabel) {
              $.ajax({
                  type: "POST",
                  url: API_ROOT_TERMS_URL,
                  data: JSON.stringify({
                    label: termLabel,
                    weight: 1
                  }),
                  contentType: "application/json; charset=utf-8"
                }
              )
                .fail(function () {
                  thiz.props.reportMessage({
                    error: "Error occurred while adding new term \"" +
                    termLabel + "\"."
                  });
                })
                .then(function (newTerm) {
                  //append the new term to the list of newly created terms
                  // replace che current label in the selected values
                  // with the newly created slug
                  selectedValues.splice(
                    _.indexOf(selectedValues, termLabel),
                    1,
                    newTerm.slug
                  );
                  // change the state
                  thiz.props.appendTermSelectedVocabulary(newTerm);
                  // finally set the current selected values
                  thiz.props.setValues(
                    thiz.props.selectedVocabulary.slug, selectedValues
                  );
                }).always(function () {
                  thiz.props.setLoadedState(true);
                });
            });

          }
        } else {
          this.props.setValues(
            this.props.selectedVocabulary.slug, selectedValues
          );
        }
      }
    });

  }
);
