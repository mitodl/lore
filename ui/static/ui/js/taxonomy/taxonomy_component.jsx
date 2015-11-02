define('taxonomy_component', ['react', 'lodash', 'jquery',
    'utils', 'react_overlay_loader', 'add_vocabulary', 'add_terms_component'],
  function (React, _, $, Utils, ReactOverlayLoader, AddVocabulary,
    AddTermsComponent) {
    'use strict';
    return React.createClass({
      getInitialState: function () {
        return {
          vocabularies: [],
          learningResourceTypes: [],
          editVocabId: undefined,
          vocabMessage: undefined,
          termsMessage: undefined
        };
      },
      editVocabulary: function (vocabId) {
        if (vocabId !== undefined) {
          this.props.setTabName('tab-vocab', 'Edit Vocabulary');
          this.props.showTab('tab-vocab');
        } else {
          this.props.setTabName('tab-vocab', 'Add Vocabulary');
          this.props.showTab('tab-taxonomies');
        }
        this.setState({
          editVocabId: vocabId,
          vocabMessage: undefined,
          termsMessage: undefined
        });
      },
      addOrUpdateVocabulary: function (newOrUpdatedVocab) {
        var found = false;
        var vocabularies = _.map(this.state.vocabularies, function (tuple) {
          if (tuple.vocabulary.id === newOrUpdatedVocab.id) {
            found = true;

            var copy = $.extend({}, tuple);
            copy.vocabulary = newOrUpdatedVocab;
            return copy;
          } else {
            return tuple;
          }
        });

        if (!found) {
          var newVocab = {
            terms: [],
            vocabulary: newOrUpdatedVocab
          };
          vocabularies = vocabularies.concat([newVocab]);
        }
        this.setState({vocabularies: vocabularies});
      },
      addTerm: function (vocabId, newTerm) {
        var vocabularies = _.map(this.state.vocabularies, function (tuple) {
          if (tuple.vocabulary.id === vocabId) {
            return {
              terms: tuple.terms.concat(newTerm),
              vocabulary: tuple.vocabulary
            };
          }
          return tuple;
        });
        this.setState({vocabularies: vocabularies});
      },
      deleteVocabulary: function (vocabId) {
        var vocabularies = _.filter(this.state.vocabularies, function (tuple) {
          return tuple.vocabulary.id !== vocabId;
        });
        this.setState({
          vocabularies: vocabularies
        });
        this.editVocabulary(undefined);
      },
      updateTerm: function (vocabId, term) {
        var vocabularies = _.map(this.state.vocabularies, function (tuple) {
          if (tuple.vocabulary.id === vocabId) {
            var terms = _.map(tuple.terms, function (tupleTerm) {
              if (tupleTerm.id === term.id) {
                return term;
              }
              return tupleTerm;
            });
            return {
              terms: terms,
              vocabulary: tuple.vocabulary
            };
          }
          return tuple;
        });
        this.setState({vocabularies: vocabularies});
      },
      deleteTerm: function (vocabId, term) {
        var vocabularies = _.map(this.state.vocabularies, function (tuple) {
          if (tuple.vocabulary.id === vocabId) {
            var terms = _.filter(tuple.terms, function (tupleTerm) {
              return tupleTerm.id !== term.id;
            });
            return {
              terms: terms,
              vocabulary: tuple.vocabulary
            };
          } else {
            return tuple;
          }
        });
        this.setState({vocabularies: vocabularies});
      },
      render: function () {
        var editVocabulary;
        var thiz = this;
        if (this.state.editVocabId !== undefined) {
          editVocabulary = _.find(this.state.vocabularies, function (vocab) {
            return vocab.vocabulary.id === thiz.state.editVocabId;
          }).vocabulary;
        }
        return (
          <div>
            <ul className="nav nav-tabs drawer-tabs nav-tabs-justified">
              <li className="tab-long active">
                <a href="#tab-taxonomies" data-toggle="tab"
                   aria-expanded="true">
                  <span className="hidden-xs">Vocabularies</span>
                </a>
              </li>
              <li className="tab-long">
                <a href="#tab-vocab" data-toggle="tab" aria-expanded="false">
              <span className="hidden-xs add-edit-vocabulary-tab">
                Add Vocabulary
              </span>
                </a>
              </li>
            </ul>
            <div className="tab-content drawer-tab-content">
              <div className="tab-pane active" id="tab-taxonomies">
                <ReactOverlayLoader
                  loaded={this.state.loaded}
                  hideChildrenOnLoad={!this.state.showChildrenOnLoad}>
                  <AddTermsComponent
                    deleteTerm={this.deleteTerm}
                    updateTerm={this.updateTerm}
                    editVocabulary={this.editVocabulary}
                    vocabularies={this.state.vocabularies}
                    repoSlug={this.props.repoSlug}
                    deleteVocabulary={this.deleteVocabulary}
                    refreshFromAPI={this.props.refreshFromAPI}
                    renderConfirmationDialog={
                      this.props.renderConfirmationDialog
                    }
                    addTerm={this.addTerm}
                    message={this.state.termsMessage}
                    reportMessage={this.termsReport}
                    setLoadedState={this.setLoadedState}
                    />
                </ReactOverlayLoader>
              </div>
              <div className="tab-pane drawer-tab-content" id="tab-vocab">
                <ReactOverlayLoader loaded={this.state.loaded}
                                    hideChildrenOnLoad={
                                      !this.state.showChildrenOnLoad
                                    }>
                  <AddVocabulary
                    editVocabulary={this.editVocabulary}
                    updateParent={this.addOrUpdateVocabulary}
                    vocabularyInEdit={editVocabulary}
                    learningResourceTypes={this.state.learningResourceTypes}
                    renderConfirmationDialog={
                      this.props.renderConfirmationDialog
                    }
                    repoSlug={this.props.repoSlug}
                    refreshFromAPI={this.props.refreshFromAPI}
                    message={this.state.vocabMessage}
                    reportMessage={this.vocabReport}
                    setLoadedState={this.setLoadedState}
                    />
                </ReactOverlayLoader>
              </div>
            </div>
          </div>
        );
      },
      vocabReport: function (message) {
        this.setState({vocabMessage: message});
      },
      termsReport: function (message) {
        this.setState({termsMessage: message});
      },
      setLoadedState: function (loaded) {
        this.setState({loaded: loaded});
      },
      componentDidMount: function () {
        var thiz = this;

        this.setState({
          loaded: false,
          showChildrenOnLoad: false
        });
        Utils.getCollection("/api/v1/learning_resource_types/").then(
          function (learningResourceTypes) {
            if (!thiz.isMounted()) {
              return;
            }

            var types = _.map(learningResourceTypes, function (type) {
              return type.name;
            });
            thiz.setState({learningResourceTypes: types});
            return Utils.getVocabulariesAndTerms(thiz.props.repoSlug).then(
              function (vocabularies) {
                if (!thiz.isMounted()) {
                  return;
                }

                thiz.setState({
                  vocabularies: vocabularies
                });
              }
            );
          }).always(function () {
            thiz.setState({
              loaded: true,
              showChildrenOnLoad: true
            });
          });
      }
    });
  }
);
