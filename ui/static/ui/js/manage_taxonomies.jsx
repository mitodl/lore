define('manage_taxonomies', ['react', 'lodash', 'jquery', 'utils', 'bootstrap'],
  function (React, _, $, Utils) {
  'use strict';

  var StatusBox = Utils.StatusBox;
  var ICheckbox = Utils.ICheckbox;

  var TermComponent = React.createClass({
    render: function () {
      return <li>
        <span className="utility-features">
          <a href="#">
            <i className="fa fa-pencil"></i>
          </a> <a href="#">
            <i className="fa fa-remove"></i>
          </a>
        </span> <label className="term-title"
        htmlFor="minimal-checkbox-1-11">{this.props.term.label}</label></li>;
    }
  });

  var VocabularyComponent = React.createClass({
    mixins: [React.addons.LinkedStateMixin],
    render: function () {
      var items = _.map(this.props.terms, function (term) {
        return <TermComponent term={term} key={term.slug} />;
      });

      return <div className="panel panel-default">
          <div className="panel-heading">
            <h4 className="panel-title">
              <span className="utility-features">
                <a href="#">
                  <i className="fa fa-pencil"></i>
                </a> <a href="#">
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
    onKeyUp: function(e) {
      if (e.key === "Enter") {
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
      .done(function(newTerm) {
          thiz.props.addTerm(thiz.props.vocabulary.slug, newTerm);
          thiz.setState({
            newTermLabel: null
          });

          // clear errors
          thiz.props.reportMessage(null);
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
          vocabulary={obj.vocabulary}
          terms={obj.terms}
          key={obj.vocabulary.slug}
          repoSlug={repoSlug}
          reportMessage={thiz.reportMessage}
          addTerm={thiz.props.addTerm}
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
      return {
        name: '',
        description: '',
        vocabularyType: 'm',
        learningResourceTypes: [],
        multiTerms: false,
      };
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
      e.target.isChecked = true;
    },
    updateMultiTerms: function(e) {
      this.setState({multiTerms: e.target.checked});
    },
    submitForm: function(e) {
      var API_ROOT_VOCAB_URL = '/api/v1/repositories/' + this.props.repoSlug +
        '/vocabularies/';
      e.preventDefault();
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
        type: "POST",
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
              thiz.setState({
                message: {
                  error: 'A Vocabulary named "' + vocabularyData.name +
                  '" already exists. Please choose a different name.'
                }
              });
              break;
            }
          }
        } else {
          thiz.setState({
            message: {
              error: 'There was a problem adding the Vocabulary.'
            }
          });
        }
      }).done(function(data) {
        // Reset state (and eventually update the vocab tab
        thiz.props.updateParent(data);
        thiz.replaceState(thiz.getInitialState());
        // Switch to taxonomy panel and scroll to new vocab (bottom)
        $('[href=#tab-taxonomies]').tab('show');
        var scrollableDiv = $(
          ".cd-panel-2 .cd-panel-container .cd-panel-content"
        );
        scrollableDiv.animate(
          {scrollTop: scrollableDiv.prop('scrollHeight')},
          500
        );
      });
    },
    render: function() {
      var thiz = this;

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
        <form className="form-horizontal" onSubmit={this.submitForm}>
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
            <button className="btn btn-lg btn-primary">Save</button>
          </p>
        </form>
      );
    }
  });

  var TaxonomyComponent = React.createClass({
    getInitialState: function() {
      return {
        vocabularies: [],
        learningResourceTypes: []
      };
    },
    addVocabulary: function(vocab) {
      // Wrap vocab in expected structure
      var newVocab = {
        terms: [],
        vocabulary: vocab
      };
      var vocabularies = this.state.vocabularies;
      this.setState({vocabularies: vocabularies.concat([newVocab])});
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
    render: function() {
      return (
        <div className="tab-content drawer-tab-content">
          <div className="tab-pane active" id="tab-taxonomies">
            <AddTermsComponent
              vocabularies={this.state.vocabularies}
              repoSlug={this.props.repoSlug}
              addTerm={this.addTerm} />
          </div>
          <div className="tab-pane drawer-tab-content" id="tab-vocab">
            <AddVocabulary
              updateParent={this.addVocabulary}
              learningResourceTypes={this.state.learningResourceTypes}
              repoSlug={this.props.repoSlug}/>
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
    'loader': function (repoSlug, container) {
      React.render(
        <TaxonomyComponent repoSlug={repoSlug}/>,
        container
      );
    }
  };

});
