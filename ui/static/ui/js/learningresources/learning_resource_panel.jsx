define("learning_resource_panel", ['react', 'jquery', 'lodash',
    'vocab_select', 'term_select', 'term_list', 'status_box',
    'react_overlay_loader', 'utils'],
  function (React, $, _, VocabSelect, TermSelect, TermList,
            StatusBox, ReactOverlayLoader, Utils) {
    'use strict';

    return React.createClass({
      mixins: [React.addons.LinkedStateMixin],

      setSelectedVocabulary: function (vocabs, selectedValue) {
        var selectedVocabulary = _.find(
          vocabs, _.matchesProperty('slug', selectedValue)
        );
        this.setState({
          selectedVocabulary: selectedVocabulary
        });
      },

      setSelectedTerms: function (vocabSlug, selectedTerms) {
        var vocabulariesAndTerms = this.state.vocabulariesAndTerms;
        var newVocabulariesAndTerms = _.map(vocabulariesAndTerms,
          function (tuple) {
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
        var selectedVocabulary = $.extend({}, this.state.selectedVocabulary);
        selectedVocabulary.terms = selectedVocabulary.terms.concat(termObj);
        this.setState({
          selectedVocabulary: selectedVocabulary,
          message: undefined
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
              reportMessage={this.reportMessage}
              />;

          termSelector =
            <TermSelect
              vocabs={vocabulariesAndTerms}
              selectedVocabulary={this.state.selectedVocabulary}
              setValues={this.setSelectedTerms}
              appendTermSelectedVocabulary={this.appendTermSelectedVocabulary}
              repoSlug={this.props.repoSlug}
              setLoadedState={this.setLoadedState}
              reportMessage={this.reportMessage}
              />;

          termList =
            <TermList
              vocabs={vocabulariesAndTerms}
              />;
        }

        return <div>
          <StatusBox message={this.state.message}/>
          <ReactOverlayLoader
            loaded={this.state.loaded}
            hideChildrenOnLoad={!this.state.showChildrenOnLoad}>
            <form className="form-horizontal">

              <div id="vocabularies" className="form-group">
                {vocabSelector} {termSelector}
              </div>

              {termList}

              <div className="form-group form-desc">
                <label className="col-sm-12 control-label">Description</label>
              <textarea
                className="form-control col-sm-12 textarea-desc"
                value={this.state.description}
                onChange={this.handleDescription}>
              </textarea>
              </div>
              <p className="text-right">
                <a className="btn btn-lg btn-primary pull-right"
                   href={this.state.previewUrl} target="_blank">Preview</a>
              </p>

              <p>
                <button className="btn btn-lg btn-primary"
                        onClick={this.saveLearningResourcePanel}>
                  Save
                </button>
                <button className="btn btn-lg btn-success"
                        onClick={this.saveAndCloseLearningResourcePanel}>
                  Save and Close
                </button>
              </p>
            </form>
          </ReactOverlayLoader>
        </div>;
      },
      setLoadedState: function (loaded) {
        this.setState({loaded: loaded});
      },
      handleDescription: function (event) {
        event.preventDefault();
        this.setState({
          description: event.target.value,
          message: undefined
        });
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

        this.setState({loaded: false});
        $.ajax({
          url: "/api/v1/repositories/" + this.props.repoSlug +
          "/learning_resources/" +
          this.props.learningResourceId + "/",
          type: "PATCH",
          contentType: 'application/json',
          data: JSON.stringify(data)
        }).then(function () {
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
        }).always(function () {
          thiz.setState({loaded: true});
        });
      },
      componentDidMount: function () {
        var thiz = this;

        this.setState({
          loaded: false,
          showChildrenOnLoad: false
        });
        $.get("/api/v1/repositories/" + this.props.repoSlug +
          "/learning_resources/" +
          this.props.learningResourceId + "/?remove_content_xml=true")
          .then(function (data) {
            if (!thiz.isMounted()) {
              // In time AJAX call happens component may become unmounted
              return;
            }

            var learningResourceType = data.learning_resource_type;
            var description = data.description;
            var selectedTerms = data.terms;
            var previewUrl = data.preview_url;

            thiz.setState({
              message: undefined,
              description: description,
              previewUrl: previewUrl,
            });
            return Utils.getVocabulariesAndTerms(
              thiz.props.repoSlug, learningResourceType)
              .then(function (results) {
                if (!thiz.isMounted()) {
                  // In time AJAX call happens component may become unmounted
                  return;
                }

                var vocabulariesAndTerms = _.map(results,
                  function (tuple) {
                    var vocabulary = tuple.vocabulary;
                    var terms = tuple.terms;
                    var selectedTermsInVocab = _.pluck(
                      _.filter(terms, function (term) {
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
              });
          }).fail(function () {
            thiz.setState({
              message: {
                error: "Unable to read information about learning resource."
              }
            });
          }).always(function () {
            thiz.setState({
              loaded: true,
              showChildrenOnLoad: true
            });
          });
      },
      getInitialState: function () {
        return {
          description: "",
          vocabulariesAndTerms: [],
          selectedVocabulary: {}
        };
      }
    });
  }
);
