define('learning_resources', [
  'react', 'jquery', 'lodash', 'utils'], function (
  React, $, _, Utils) {
  'use strict';

  var StatusBox = Utils.StatusBox;
  var Select2 = Utils.Select2;

  var TermListItem = React.createClass({
    render: function () {
      return (
        <li className="applied-term list-group-item">
          <strong>{this.props.label}: </strong> {this.props.terms}
        </li>
      );
    }
  });

  var TermList = React.createClass({
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
              Taxonomy Terms applied to this Learning Resource
          </div>
          <ul id="term-list" className="list-group">
            {appliedVocabularies}
          </ul>
        </div>
      );
    }
  });

  var VocabSelect = React.createClass({
    render: function () {
      var options;
      options = _.map(this.props.vocabs, function(vocab) {
        return {
          id: vocab.vocabulary.slug,
          text: vocab.vocabulary.name,
        };
      });

      var slug = this.props.selectedVocabulary.slug;

      return <div className="col-sm-6">
          <Select2
            key="vocabChooser"
            className="form-control"
            placeholder={"Select a vocabulary"}
            options={options}
            allowClear={false}
            onChange={this.handleChange}
            values={slug}
            multiple={false}
            allowTags={false}
            />
        </div>;
    },
    handleChange: function(e) {
      var selectedValue = _.pluck(
        _.filter(e.target.options, function(option) {
          return option.selected && option.value !== null;
        }), 'value');
      this.props.setValues(
        _.pluck(this.props.vocabs, 'vocabulary'), selectedValue[0]
      );
    }
  });

  var TermSelect = React.createClass({
    render: function () {
      var options = [];
      options = _.map(this.props.selectedVocabulary.terms, function (term) {
        return {
          id: term.slug,
          text: term.label
        };
      });

      var currentVocabulary = {};
      var selectedVocabulary = this.props.selectedVocabulary;

      _.forEach(this.props.vocabs, function(vocab) {
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
      return <div className="col-sm-6">
          <Select2
            key={name}
            className="form-control"
            placeholder={"Select a value for " + name}
            options={options}
            onChange={this.handleChange}
            values={currentVocabulary.selectedTerms}
            multiple={this.props.selectedVocabulary.multi_terms}
            allowTags={allowTags}
            />
        </div>;
    },

    handleChange: function(e) {
      var selectedValues = _.pluck(
        _.filter(e.target.options, function(option) {
          return option.selected && option.value !== null;
        }), 'value');
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
          _.forEach(termsToCreate, function (termLabel) {
            $.ajax({
                type: "POST",
                url: API_ROOT_TERMS_URL ,
                data: JSON.stringify({
                  label: termLabel,
                  weight: 1
                }),
                contentType: "application/json; charset=utf-8"
              }
            )
            .fail(function() {
                thiz.props.reportMessage({
                  error: "Error occurred while adding new term \"" +
                    termLabel + "\"."
                });
              })
            .done(function(newTerm) {
              //append the new term to the list of newly created terms
              // replace che current label in the selected values with the newly created slug
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

  var LearningResourcePanel = React.createClass({
    mixins: [React.addons.LinkedStateMixin],

    setSelectedVocabulary: function(vocabs, selectedValue) {
      var selectedVocabulary = _.find(
        vocabs, _.matchesProperty('slug', selectedValue)
      );
      this.setState({
        selectedVocabulary: selectedVocabulary
      });
    },

    setSelectedTerms: function(vocabSlug, selectedTerms) {
      var vocabulariesAndTerms = this.state.vocabulariesAndTerms;
      var newVocabulariesAndTerms = _.map(vocabulariesAndTerms,
        function(tuple) {
          if (vocabSlug === tuple.vocabulary.slug) {
            var newTuple = {
              vocabulary: tuple.vocabulary,
              terms: tuple.terms,
              selectedTerms: selectedTerms
            };
            return newTuple;
          } else {
            return tuple;
          }
        });

      this.setState({
        vocabulariesAndTerms: newVocabulariesAndTerms
      });
    },

    appendTermSelectedVocabulary: function (termObj) {
      var selectedVocabulary = this.state.selectedVocabulary;
      selectedVocabulary.terms.push(termObj);
      this.setState({
        selectedVocabulary: selectedVocabulary
      });
    },

    reportMessage: function (messageObj) {
      this.setState({
        message: messageObj
      });
    },

    render: function () {

      var vocabulariesAndTerms = this.state.vocabulariesAndTerms;
      var vocabSelector = "There are no terms for this resource";
      var termSelector = "";
      var termList = "";

      if (vocabulariesAndTerms.length) {
        vocabSelector =
          <VocabSelect
            vocabs={vocabulariesAndTerms}
            selectedVocabulary={this.state.selectedVocabulary}
            setValues={this.setSelectedVocabulary}
          />;

        termSelector =
          <TermSelect
            vocabs={vocabulariesAndTerms}
            selectedVocabulary={this.state.selectedVocabulary}
            setValues={this.setSelectedTerms}
            appendTermSelectedVocabulary={this.appendTermSelectedVocabulary}
            repoSlug={this.props.repoSlug}
            reportMessage={this.reportMessage}
          />;

        termList =
        <TermList
          vocabs={vocabulariesAndTerms}
        />;
      }

      return <div>
        <form className="form-horizontal">
          <StatusBox message={this.state.message} />
          <textarea className="form-control textarea-xml"
                    readOnly="true"
                    valueLink={this.linkState('contentXml')}
            />

          <p className="text-right">
            <a id="copy-textarea-xml" href="#"
               className="btn btn-white"
               onClick={this.selectXml}>Select XML</a>
            <a className="btn btn-primary pull-left"
               href={this.state.previewUrl} target="_blank">Preview</a>
          </p>

          <div id="vocabularies" className="form-group">
              {vocabSelector} {termSelector}
          </div>

          {termList}

          <div className="form-group form-desc">
            <label className="col-sm-12 control-label">Description</label>
              <textarea
                className="form-control col-sm-12 textarea-desc"
                valueLink={this.linkState('description')}>
              </textarea>
          </div>
          <p>
            <button className="btn btn-lg btn-primary"
                    onClick={this.saveLearningResourcePanel} >
              Save
            </button> <button className="btn btn-lg btn-success"
                    onClick={this.saveAndCloseLearningResourcePanel} >
              Save and Close
            </button>
          </p>
        </form>
      </div>;
    },
    selectXml: function (event) {
      event.preventDefault();
      $('.textarea-xml').select();
    },
    saveLearningResourcePanel: function (event) {
      event.preventDefault();
      this.saveForm(false);
    },
    saveAndCloseLearningResourcePanel: function (event) {
      event.preventDefault();
      this.saveForm(true);
    },
    saveForm: function (closePanel) {
      var thiz = this;

      var terms = _.map(this.state.vocabulariesAndTerms, function (tuple) {
          return tuple.selectedTerms;
        });
      terms = _.flatten(terms);
      var data = {
        terms: terms,
        description: this.state.description
      };

      $.ajax({
        url: "/api/v1/repositories/" + this.props.repoSlug +
        "/learning_resources/" +
        this.props.learningResourceId + "/",
        type: "PATCH",
        contentType: 'application/json',
        data: JSON.stringify(data)
      }).done(function () {
        thiz.setState({
          message: "Form saved successfully!"
        });
        if (closePanel) {
          thiz.props.closeLearningResourcePanel();
        }
        thiz.props.refreshFromAPI();
      }).fail(function () {
        thiz.setState({
          message: {error: "Unable to save form"}
        });
      });
    },
    componentDidMount: function () {
      var thiz = this;

      $.get("/api/v1/repositories/" + this.props.repoSlug +
        "/learning_resources/" +
        this.props.learningResourceId + "/").done(function (data) {
        if (!thiz.isMounted()) {
          // In time AJAX call happens component may become unmounted
          return;
        }

        var contentXml = data.content_xml;
        var learningResourceType = data.learning_resource_type;
        var description = data.description;
        var selectedTerms = data.terms;
        var previewUrl = data.preview_url;

        thiz.setState({
          contentXml: contentXml,
          message: undefined,
          description: description,
          previewUrl: previewUrl,
        });
        Utils.getVocabulariesAndTerms(
          thiz.props.repoSlug, learningResourceType)
          .then(function (results) {
          if (!thiz.isMounted()) {
            // In time AJAX call happens component may become unmounted
            return;
          }

          var vocabulariesAndTerms = _.map(results,
            function(tuple) {
              var vocabulary = tuple.vocabulary;
              var terms = tuple.terms;
              var selectedTermsInVocab = _.pluck(
                _.filter(terms, function(term) {
                  return _.includes(selectedTerms, term.slug);
                }), 'slug');
              return {
                vocabulary: vocabulary,
                terms: terms,
                selectedTerms: selectedTermsInVocab
              };
            });

          thiz.setState({
            vocabulariesAndTerms: vocabulariesAndTerms,
          });

          if (vocabulariesAndTerms.length) {
            thiz.setState({
              selectedVocabulary: vocabulariesAndTerms[0].vocabulary
            });
          }

        }).fail(function () {
          thiz.setState({
            message: {
              error: "Unable to read information about learning resource."
            }
          });
        });

      }).fail(function () {
          thiz.setState({
            message: {
              error: "Unable to read information about learning resource."
            }
          });
        });
    },
    getInitialState: function () {
      return {
        contentXml: "",
        description: "",
        vocabulariesAndTerms: [],
        selectedVocabulary: {}
      };
    }
  });

  return {
    TermList: TermList,
    TermSelect: TermSelect,
    VocabSelect: VocabSelect,
    LearningResourcePanel: LearningResourcePanel,
    loader: function (
      repoSlug, learningResourceId, refreshFromAPI,
      closeLearningResourcePanel, container
    ) {
      // Unmount and remount the component to ensure that its state
      // is always up to date with the rest of the app.
      React.unmountComponentAtNode(container);
      React.render(<LearningResourcePanel
        repoSlug={repoSlug}
        learningResourceId={learningResourceId}
        refreshFromAPI={refreshFromAPI}
        closeLearningResourcePanel={closeLearningResourcePanel}
        />, container);
    }
  };
});
