define('add_vocabulary', ['react', 'lodash', 'jquery', 'uri',
    'status_box', 'icheckbox'],
  function (React, _, $, URI, StatusBox, ICheckbox) {
    'use strict';

    return React.createClass({
      mixins: [React.addons.LinkedStateMixin],
      getInitialState: function () {
        return this.makeState(this.props.vocabularyInEdit);
      },
      updateLearningResourceType: function (e) {
        var checkedType = e.target.value;
        var newTypes;
        if (e.target.checked) {
          if (!_.includes(this.state.learningResourceTypes, checkedType)) {
            newTypes = this.state.learningResourceTypes.concat([checkedType]);
          } else {
            // else already includes new type
            console.error("Type " + checkedType + " is already selected");
          }
        } else {
          newTypes = _.filter(this.state.learningResourceTypes,
            function (type) {
              return type !== checkedType;
            }
          );
        }

        this.setState({learningResourceTypes: newTypes});
      },
      updateVocabularyType: function (e) {
        this.setState({vocabularyType: e.target.value});
      },
      updateMultiTerms: function (e) {
        this.setState({multiTerms: e.target.checked});
      },
      submitForm: function (e) {
        e.preventDefault();
        if (_.isEmpty(this.state.name)) {
          this.props.reportMessage({error: 'Please enter vocabulary name.'});
          return;
        }

        if (_.isEmpty(this.state.description)) {
          this.props.reportMessage({
            error: 'Please enter vocabulary description.'
          });
          return;
        }

        var API_ROOT_VOCAB_URL;
        var method = "POST";
        if (this.isEditModeOpen()) {
          API_ROOT_VOCAB_URL = '/api/v1/repositories/' + this.props.repoSlug +
            '/vocabularies/' + this.props.vocabularyInEdit.slug + "/";
          method = "PATCH";
        } else {
          API_ROOT_VOCAB_URL = '/api/v1/repositories/' + this.props.repoSlug +
            '/vocabularies/';
        }
        var thiz = this;
        var vocabularyData = {
          name: this.state.name,
          description: this.state.description,
          vocabulary_type: this.state.vocabularyType,
          required: false,
          weight: 2147483647,
          learning_resource_types: this.state.learningResourceTypes,
          multi_terms: this.state.multiTerms
        };

        thiz.props.setLoadedState(false);

        // User wants to submit the form. First we need to see if any
        // resource term links would be deleted by this action. If so we need
        // a confirmation dialog to move forward. This uses a promise (deferred)
        // which will fail to indicate a cancellation and success to say we should
        // move forward.
        var confirmationPromise;
        if (method === 'PATCH') {
          var removedTypes = _.difference(
            this.props.vocabularyInEdit.learning_resource_types,
            this.state.learningResourceTypes
          );

          // Check if there are any learning resources which may get deleted
          if (removedTypes.length === 0) {
            // No need for confirmation dialog
            confirmationPromise = $.Deferred().resolve();
          } else {
            var uri = URI("/api/v1/repositories/" + this.props.repoSlug +
              "/learning_resources/").search({
              vocab_slug: this.props.vocabularyInEdit.slug,
              type_name: removedTypes
            }).toString();

            // Get list of resources with links to a term that would be deleted.
            // If this count is > 0 require a confirmation to make the promise
            // resolved.
            confirmationPromise = $.get(uri).then(function (collection) {
              var result = $.Deferred();

              if (collection.count !== 0) {
                var resourcesWord = "resources";
                if (collection.count === 1) {
                  resourcesWord = "resource";
                }
                var options = {
                  actionButtonName: "Delete",
                  actionButtonClass: "btn btn-danger btn-ok",
                  title: "Confirm Update",
                  message: "Do you want to proceed with the resource update?",
                  description: "After this update " + collection.count + " " +
                    resourcesWord + " will not be linked to" +
                    " this vocabulary's terms anymore due to" +
                    " some resource types being unselected. ",
                  confirmationHandler: function (success) {
                    // continue with the next promise in the chain
                    if (success) {
                      result.resolve();
                    }
                  }
                };
                thiz.props.renderConfirmationDialog(options);
              } else {
                result.resolve();
              }

              // The next promise in line will be executed when if we resolve
              // `result`.
              return result;
            });
          }
        } else {
          // No need for confirmation, proceed.
          confirmationPromise = $.Deferred().resolve();
        }

        confirmationPromise.then(function () {
          return $.ajax({
            type: method,
            url: API_ROOT_VOCAB_URL,
            data: JSON.stringify(vocabularyData),
            contentType: "application/json"
          });
        }).then(function (data) {
          // Reset state (and eventually update the vocab tab
          thiz.props.updateParent(data);
          thiz.resetForm();
          return thiz.props.refreshFromAPI();
        }).fail(function (data) {
          var jsonData = data && data.responseJSON;
          var i = 0;
          if (jsonData && jsonData.non_field_errors) {
            for (i = 0; i < jsonData.non_field_errors.length; i++) {
              if (jsonData.non_field_errors[i] ===
                'The fields repository, name must make a unique set.') {
                thiz.props.reportMessage({
                  error: 'A Vocabulary named "' + vocabularyData.name +
                  '" already exists. Please choose a different name.'
                });
                break;
              }
            }
          } else {
            var error = 'There was a problem adding the Vocabulary.';
            if (thiz.isEditModeOpen()) {
              error = 'There was a problem with updating the Vocabulary.';
            }
            thiz.props.reportMessage({error: error});
          }
        }).always(function () {
          thiz.props.setLoadedState(true);
        });
      },
      isEditModeOpen: function () {
        return !!this.props.vocabularyInEdit;
      },
      onReset: function (e) {
        e.preventDefault();
        this.resetForm();
      },
      resetForm: function () {
        this.replaceState(this.makeState(undefined));
        this.props.editVocabulary(undefined); //reset vocabulary in edit mode
      },
      componentWillReceiveProps: function (nextProps) {
        // Note that this is only triggered on prop updates which will send
        // new values that we need to store in the state.
        this.replaceState(this.makeState(nextProps.vocabularyInEdit));
      },
      makeState: function (newVocab) {
        if (newVocab !== undefined) {
          return {
            name: newVocab.name,
            description: newVocab.description,
            vocabularyType: newVocab.vocabulary_type,
            learningResourceTypes: newVocab.learning_resource_types,
            multiTerms: newVocab.multi_terms
          };
        } else {
          return {
            name: '',
            description: '',
            vocabularyType: 'm',
            learningResourceTypes: [],
            multiTerms: false
          };
        }
      },
      render: function () {
        var thiz = this;
        var cancelButton = null;
        var submitButtonText = "Save";

        if (this.props.vocabularyInEdit !== undefined) {
          cancelButton = <button className="btn btn-lg btn-primary"
                                 onClick={this.onReset}>Cancel</button>;
          submitButtonText = "Update";
        }
        var checkboxes = _.map(this.props.learningResourceTypes,
          function (type) {
            var checked = _.includes(thiz.state.learningResourceTypes, type);
            return (
              <li key={type}>
                <div className="checkbox">
                  <label>
                    <ICheckbox
                      value={type}
                      checked={checked}
                      onChange={thiz.updateLearningResourceType}/> {type}
                  </label>
                </div>
              </li>
            );
          }
        );

        return (
          <form className="form-horizontal">
            <StatusBox message={this.props.message}/>

            <p>
              <input type="text" valueLink={this.linkState('name')}
                     className="form-control"
                     placeholder="Name"/>
            </p>

            <p>
              <input type="text" valueLink={this.linkState('description')}
                     className="form-control"
                     placeholder="Description"/>
            </p>

            <p>
              <ul className="icheck-list">
                {checkboxes}
              </ul>
            </p>
            <p>
              <div className="radio">
                <label>
                  <input id="managed_vocabulary_type" type="radio"
                         name="vocabulary_type" value="m"
                         checked={this.state.vocabularyType === 'm'}
                         onChange={this.updateVocabularyType}/>
                  Managed
                </label>
              </div>
              <div className="radio">
                <label>
                  <input id="free_vocabulary_type" type="radio"
                         name="vocabulary_type" value="f"
                         checked={this.state.vocabularyType === 'f'}
                         onChange={this.updateVocabularyType}/>
                  Tag Style (on the fly)
                </label>
              </div>
            </p>
            <p>
              <div className="checkbox-add-vocabulary">
                <label>
                  <ICheckbox
                    checked={this.state.multiTerms}
                    onChange={thiz.updateMultiTerms}/>
                  Allow multiple terms per learning resource
                </label>
              </div>
            </p>
            <p>
              <button className="btn btn-lg btn-primary"
                      onClick={this.submitForm}>{submitButtonText}
              </button>
              {cancelButton}
            </p>
          </form>
        );
      }
    });
  }
);
