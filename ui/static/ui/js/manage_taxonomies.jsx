define('manage_taxonomies', ['react', 'lodash', 'jquery', 'utils', 'bootstrap'],
  function (React, _, $, Utils) {
  'use strict';

  var StatusBox = Utils.StatusBox;
  var ICheckbox = Utils.ICheckbox;

  var TermComponent = React.createClass({
    mixins: [React.addons.LinkedStateMixin],
    getInitialState: function() {
      return {
        formatActionState: 'show',
        label: this.props.term.label,
        errorMessage: '',
        showError: false
      };
    },
    render: function () {
      var label = null;
      var formatActionClassName = null;
      var editButtonClass = 'format-button';
      var deleteButtonClass = 'revert-button';
      if (this.state.formatActionState === 'edit') {
        label = <label className="help-inline control-label"> <input
          ref="editText" type="text" valueLink={this.linkState('label')}
          className='form-control edit-term-box' /> <button
          onClick={this.saveTerm}  type="button"
          className="save-button btn btn-primary btn-sm editable-submit"><i
          className="glyphicon glyphicon-ok"></i></button> <button type="button"
          className="btn btn-default btn-sm editable-cancel"
          onClick={this.cancelAction}><i
          className="glyphicon glyphicon-remove"></i>
          </button> {this.state.errorMessage}
        </label>;
        formatActionClassName = "fa fa-pencil no-select";
        editButtonClass = 'format-button disabled';
        deleteButtonClass = 'revert-button disabled';
      } else if (this.state.formatActionState === 'show') {
        label = <label className="term-title"
          htmlFor="minimal-checkbox-1-11">{this.state.label}</label>;
        formatActionClassName = "fa fa-pencil no-select";
      }

      var listClassName = "form-group";
      if (this.state.showError) {
        listClassName = "form-group has-error";
      }

      return <li className={listClassName}>
        <span className="utility-features">
          <a onClick={this.editTerm} className={editButtonClass}>
            <i className={formatActionClassName}></i>
          </a> <a className={deleteButtonClass}>
            <i className="fa fa-remove"></i>
          </a>
        </span>{label}</li>;
    },
    /**
     * If user selects edit button then open edit mode
     * Else call api to update term.
     */
    editTerm: function() {
      this.setState({
          formatActionState: 'edit'
        }, function() {
        var $editText = $(React.findDOMNode(this.refs.editText));
        $editText.focus();
      });
    },
    saveTerm: function() {
      if (this.state.label !== this.props.term.label) {
        this.updateTermSubmit();
      } else {
        this.resetUtilityFeatures();
      }
    },
    /**
     * On Close button select reset term UI
    */
    cancelAction : function() {
      var formatActionState = this.state.formatActionState;
      if (formatActionState === 'edit') {
        // user is in edit mode. Cancel edit if user presses cross icon.
        this.resetUtilityFeatures();
      }
    },
    /**
     * Reset term edit UI
     */
    resetUtilityFeatures: function() {
      this.setState(this.getInitialState());
    },
    /**
     * Api call to save term and update parent component
     */
    updateTermSubmit: function() {
      if (_.isEmpty(this.state.label)) {
        this.setState({showError: true});
        return;
      }
      var API_ROOT_VOCAB_URL = '/api/v1/repositories/' + this.props.repoSlug +
        '/vocabularies/' + this.props.vocabularySlug + '/terms/' +
        this.props.term.slug + "/";
      var thiz = this;
      var termData = {
        label: this.state.label,
        weight: this.props.term.weight
      };
      $.ajax({
        type: 'PATCH',
        url: API_ROOT_VOCAB_URL,
        data: JSON.stringify(termData),
        contentType: "application/json"
      }).fail(function() {
        thiz.setState({
          showError: true,
          errorMessage: 'Unable to update term'
        });
      }).done(function(term) {
        thiz.resetUtilityFeatures();
        thiz.props.updateTerm(thiz.props.vocabularySlug, term);
        thiz.props.refreshFromAPI();
      });
    }
  });

  var VocabularyComponent = React.createClass({
    mixins: [React.addons.LinkedStateMixin],
    render: function () {
      var thiz = this;
      var items = _.map(this.props.terms, function (term) {
        return <TermComponent
          updateTerm={thiz.props.updateTerm}
          vocabularySlug={thiz.props.vocabulary.slug}
          repoSlug={thiz.props.repoSlug}
          term={term}
          key={term.slug}
          refreshFromAPI={thiz.props.refreshFromAPI}
          />;
      });

      return <div className="panel panel-default">
          <div className="panel-heading">
            <h4 className="panel-title">
              <span className="utility-features">
                <a href="#" onClick={this.onEdit}>
                  <i className="fa fa-pencil"></i>
                </a>
                <a data-toggle="modal" data-target="#confirm-delete"
                  onClick={this.onDeleteHandler} className="delete-vocabulary">
                  <i className="fa fa-remove"></i>
                </a>
              </span> <a className="accordion-toggle vocab-title"
                         data-toggle="collapse"
                         data-parent="#accordion"
                         href={'#collapse-' + this.props.vocabulary.slug}>
                {this.props.vocabulary.name}
              </a>
            </h4>
          </div>
          <div id={'collapse-' + this.props.vocabulary.slug}
               className="panel-collapse collapse in">
            <div className="panel-body">
              <ul className="icheck-list with-utility-features">
                {items}
                <li>
                  <div className="input-group">
                    <input type="text"
                           valueLink={this.linkState('newTermLabel')}
                      className="form-control" onKeyUp={this.onKeyUp}
                      placeholder="Add new term..."
                      />
                      <span className="input-group-btn">
                        <a className="btn btn-white"
                          type="button" onClick={this.handleAddTermClick}><i
                          className="fa fa-plus-circle"
                        ></i></a>
                      </span>
                  </div>
                </li>
              </ul>
            </div>
          </div>
      </div>;
    },
    onDeleteHandler: function() {
      var options = {
        actionButtonName: "Delete",
        actionButtonClass: "btn btn-danger btn-ok",
        title: "Confirm Delete",
        message: "Are you sure you want to delete vocabulary '" +
          this.props.vocabulary.name + "'? ",
        description: "Deleting this vocabulary will remove it from all " +
          "learning resources.",
        confirmationHandler: this.confirmedDeleteResponse
      };
      this.props.renderConfirmationDialog(options);
    },
    confirmedDeleteResponse: function(success) {
      var thiz = this;
      if (success) {
        var vocab = this.props.vocabulary;
        var API_ROOT_VOCAB_URL = '/api/v1/repositories/' + this.props.repoSlug +
          '/vocabularies/' + vocab.slug + '/';
        $.ajax({
          type: "DELETE",
          url: API_ROOT_VOCAB_URL
        }).fail(function () {
          var message = "Unable to delete vocabulary '" + vocab.name + "'";
          thiz.props.reportMessage({error: message});
        }).then(function () {
          thiz.props.deleteVocabulary(vocab.slug);

          thiz.props.refreshFromAPI();
        });
      }
    },
    onEdit: function(e) {
      e.preventDefault();
      this.props.editVocabulary(this.props.vocabulary);
    },
    onKeyUp: function(e) {
      if (e.key === "Enter") {
        e.preventDefault();
        this.handleAddTermClick();
      }
    },
    handleAddTermClick: function() {
      var thiz = this;
      var API_ROOT_VOCAB_URL = '/api/v1/repositories/' + this.props.repoSlug +
        '/vocabularies/';
      $.ajax({
          type: "POST",
          url: API_ROOT_VOCAB_URL + this.props.vocabulary.slug + "/terms/",
          data: JSON.stringify({
            label: this.state.newTermLabel,
            weight: 1
          }),
          contentType: "application/json; charset=utf-8"
        }
      ).fail(function() {
          thiz.props.reportMessage({
            error: "Error occurred while adding new term."
          });
        })
      .then(function(newTerm) {
          thiz.props.addTerm(thiz.props.vocabulary.slug, newTerm);
          thiz.setState({
            newTermLabel: null
          });

          // clear errors
          thiz.props.reportMessage(null);
          thiz.props.refreshFromAPI();
        });
    },
    getInitialState: function() {
      return {
        newTermLabel: ""
      };
    },
  });

  var AddTermsComponent = React.createClass({
    render: function () {
      var repoSlug = this.props.repoSlug;
      var thiz = this;
      var items = _.map(this.props.vocabularies, function (obj) {
        return <VocabularyComponent
          updateTerm={thiz.props.updateTerm}
          vocabulary={obj.vocabulary}
          deleteVocabulary={thiz.props.deleteVocabulary}
          editVocabulary={thiz.props.editVocabulary}
          terms={obj.terms}
          key={obj.vocabulary.slug}
          repoSlug={repoSlug}
          reportMessage={thiz.reportMessage}
          addTerm={thiz.props.addTerm}
          renderConfirmationDialog={thiz.props.renderConfirmationDialog}
          refreshFromAPI={thiz.props.refreshFromAPI}
          />;
      });
      return <div className="panel-group lore-panel-group">
        <div className="panel panel-default">
        </div>
        <StatusBox message={this.state.message} />
        {items}
      </div>;

    },
    reportMessage: function(message) {
      this.setState({message: message});
    },
    getInitialState: function() {
      return {
        message: undefined
      };
    }
  });

  var AddVocabulary = React.createClass({
    mixins: [React.addons.LinkedStateMixin],
    getInitialState: function() {
      return this.makeState(this.props.vocabulary);
    },
    updateLearningResourceType: function(e) {
      var checkedType = e.target.value;
      var newTypes;
      if (e.target.checked) {
        if (!_.includes(this.state.learningResourceTypes, checkedType)) {
          newTypes = this.state.learningResourceTypes.concat([checkedType]);
        } else {
          // else already includes new type
          console.error("Type " + checkedType + " is already selected");
          throw "";
        }
      } else {
        newTypes = _.filter(this.state.learningResourceTypes, function(type) {
          return type !== checkedType;
        });
      }

      this.setState({learningResourceTypes: newTypes});
    },
    updateVocabularyType: function(e) {
      this.setState({vocabularyType: e.target.value});
    },
    updateMultiTerms: function(e) {
      this.setState({multiTerms: e.target.checked});
    },
    showErrorMessage: function(errorText) {
      this.setState({
        message: {
          error: errorText
        }
      });
    },
    submitForm: function(e) {
      e.preventDefault();
      if (_.isEmpty(this.state.name)) {
        this.showErrorMessage('Please enter vocabulary name.');
        return;
      }

      if (_.isEmpty(this.state.description)) {
        this.showErrorMessage('Please enter vocabulary description.');
        return;
      }

      var API_ROOT_VOCAB_URL;
      var method = "POST";
      if (this.isEditModeOpen()) {
        API_ROOT_VOCAB_URL = '/api/v1/repositories/' + this.props.repoSlug +
        '/vocabularies/' + this.state.slug + "/";
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

      $.ajax({
        type: method,
        url: API_ROOT_VOCAB_URL,
        data: JSON.stringify(vocabularyData),
        contentType: "application/json"
      }).fail(function(data) {
        var jsonData = data.responseJSON;
        var i = 0;
        if (jsonData && jsonData.non_field_errors) {
          for (i = 0; i < jsonData.non_field_errors.length ; i++) {
            if (jsonData.non_field_errors[i] ===
              'The fields repository, name must make a unique set.') {
              thiz.showErrorMessage('A Vocabulary named "' +
                vocabularyData.name + '" already exists.' +
                ' Please choose a different name.');
              break;
            }
          }
        } else {
          var message = 'There was a problem adding the Vocabulary.';
          if (thiz.isEditModeOpen()) {
            message = 'There was a problem with updating the Vocabulary.';
          }
          thiz.showErrorMessage(message);
        }
      }).then(function(data) {
        // Reset state (and eventually update the vocab tab
        thiz.props.updateParent(data);
        thiz.resetForm();
        if (!thiz.isEditModeOpen()) {
          var scrollableDiv = $(
           ".cd-panel-2 .cd-panel-container .cd-panel-content"
          );
          scrollableDiv.animate(
            {scrollTop: scrollableDiv.prop('scrollHeight')},
            500
          );
        }
        thiz.props.refreshFromAPI();
      });
    },
    isEditModeOpen: function() {
      return !!this.state.slug;
    },
    onReset: function(e) {
      e.preventDefault();
      this.resetForm();
    },
    resetForm: function() {
      this.replaceState(this.makeState(undefined));
      this.props.editVocabulary(undefined); //reset vocabulary in edit mode
    },
    componentWillReceiveProps: function(nextProps) {
      // Note that this is only triggered on prop updates which will send
      // new values that we need to store in the state.
      this.replaceState(this.makeState(nextProps.vocabulary));
    },
    makeState: function(newVocab) {
      if (newVocab) {
        return {
          name: newVocab.name,
          description: newVocab.description,
          vocabularyType: newVocab.vocabulary_type,
          learningResourceTypes: newVocab.learning_resource_types,
          multiTerms: newVocab.multi_terms,
          slug: newVocab.slug
        };
      }
      else {
        return {
          name: '',
          description: '',
          vocabularyType: 'm',
          learningResourceTypes: [],
          multiTerms: false,
          slug: ''
        };
      }
    },
    render: function() {
      var thiz = this;
      var cancelButton = null;
      var submitButtonText = "Save";

      if (this.props.vocabulary) {
        cancelButton = <button className="btn btn-lg btn-primary"
                               onClick={this.onReset}>Cancel</button>;
        submitButtonText = "Update";
      }
      var checkboxes = _.map(this.props.learningResourceTypes, function(type) {
        var checked = _.includes(thiz.state.learningResourceTypes, type);
        return (
            <li key={type}>
              <div className="checkbox">
                <label>
                  <ICheckbox
                    value={type}
                    checked={checked}
                    onChange={thiz.updateLearningResourceType} /> {type}
                </label>
              </div>
            </li>
        );
      });

      return (
        <form className="form-horizontal">
          <StatusBox message={this.state.message} />
          <p>
            <input type="text" valueLink={this.linkState('name')}
              className="form-control"
              placeholder="Name" />
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
                  onChange={this.updateVocabularyType} />
                    Managed
              </label>
            </div>
            <div className="radio">
              <label>
                <input id="free_vocabulary_type" type="radio"
                  name="vocabulary_type" value="f"
                  checked={this.state.vocabularyType === 'f'}
                  onChange={this.updateVocabularyType} />
                    Tag Style (on the fly)
              </label>
            </div>
          </p>
          <p>
            <div className="checkbox-add-vocabulary">
              <label>
                <ICheckbox
                  checked={this.state.multiTerms}
                  onChange={thiz.updateMultiTerms} />
                  Allow multiple terms per learning resource
              </label>
            </div>
          </p>
          <p>
            <button className="btn btn-lg btn-primary"
                    onClick={this.submitForm}>{submitButtonText}
            </button>  {cancelButton}
          </p>
        </form>
      );
    }
  });

  var TaxonomyComponent = React.createClass({
    getInitialState: function() {
      return {
        vocabularies: [],
        learningResourceTypes: [],
        vocabularyInEdit: undefined
      };
    },
    editVocabulary: function(vocab) {
      this.setState({vocabularyInEdit: vocab});
      if (vocab) {
        this.props.setTabName('tab-vocab', 'Edit Vocabulary');
        this.props.showTab('tab-vocab');
      } else {
        this.props.setTabName('tab-vocab', 'Add Vocabulary');
        this.props.showTab('tab-taxonomies');
      }
    },
    addOrUpdateVocabulary: function(newOrUpdatedVocab) {
      var found = false;
      var vocabularies = _.map(this.state.vocabularies, function(tuple) {
        if (tuple.vocabulary.slug === newOrUpdatedVocab.slug) {
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
    addTerm: function(vocabSlug, newTerm) {
      var vocabularies = _.map(this.state.vocabularies, function(tuple) {
        if (tuple.vocabulary.slug === vocabSlug) {
          return {
            terms: tuple.terms.concat(newTerm),
            vocabulary: tuple.vocabulary
          };
        }
        return tuple;
      });
      this.setState({vocabularies: vocabularies});
    },
    deleteVocabulary: function(vocabSlug) {
      var vocabularies = _.filter(this.state.vocabularies, function (tuple) {
        return tuple.vocabulary.slug !== vocabSlug;
      });
      this.setState({
        vocabularies: vocabularies
      });
      this.editVocabulary(undefined);
    },
    updateTerm: function(vocabSlug, term) {
      var vocabularies = _.map(this.state.vocabularies, function(tuple) {
        if (tuple.vocabulary.slug === vocabSlug) {
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
    render: function() {
      return (
        <div className="tab-content drawer-tab-content">
          <div className="tab-pane active" id="tab-taxonomies">
            <AddTermsComponent
              updateTerm={this.updateTerm}
              editVocabulary={this.editVocabulary}
              vocabularies={this.state.vocabularies}
              repoSlug={this.props.repoSlug}
              deleteVocabulary={this.deleteVocabulary}
              refreshFromAPI={this.props.refreshFromAPI}
              renderConfirmationDialog={this.props.renderConfirmationDialog}
              addTerm={this.addTerm}
              />
          </div>
          <div className="tab-pane drawer-tab-content" id="tab-vocab">
            <AddVocabulary
              editVocabulary={this.editVocabulary}
              updateParent={this.addOrUpdateVocabulary}
              vocabulary={this.state.vocabularyInEdit}
              learningResourceTypes={this.state.learningResourceTypes}
              repoSlug={this.props.repoSlug}
              refreshFromAPI={this.props.refreshFromAPI}
              />
          </div>
        </div>
      );
    },
    componentDidMount: function() {
      var thiz = this;

      Utils.getCollection("/api/v1/learning_resource_types/").then(
        function(learningResourceTypes) {
        if (!thiz.isMounted()) {
          return;
        }

        var types = _.map(learningResourceTypes, function(type) {
          return type.name;
        });
        thiz.setState({learningResourceTypes: types});
        Utils.getVocabulariesAndTerms(thiz.props.repoSlug).then(
          function(vocabularies) {
            if (!thiz.isMounted()) {
              return;
            }

            thiz.setState({vocabularies: vocabularies});
          }
        );
      });
    }
  });

  return {
    'VocabularyComponent': VocabularyComponent,
    'TermComponent': TermComponent,
    'AddTermsComponent': AddTermsComponent,
    'AddVocabulary': AddVocabulary,
    'TaxonomyComponent': TaxonomyComponent,
    'loader': function (repoSlug, container, showConfirmationDialog,
                        showTab, setTabName, refreshFromAPI
    ) {
      // Unmount and remount the component to ensure that its state
      // is always up to date with the rest of the app.
      React.unmountComponentAtNode(container);
      React.render(
        <TaxonomyComponent
          repoSlug={repoSlug}
          refreshFromAPI={refreshFromAPI}
          renderConfirmationDialog={showConfirmationDialog}
          showTab={showTab}
          setTabName={setTabName}
          />,
        container
      );
    }
  };

});
