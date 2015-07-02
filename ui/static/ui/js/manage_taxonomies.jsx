define('setup_manage_taxonomies', ['reactaddons', 'lodash', 'jquery'],
  function (React, _, $) {
  'use strict';
  var API_ROOT_VOCAB_URL;

  var TermComponent = React.createClass({
    render: function () {
      return <li><label
        htmlFor="minimal-checkbox-1-11">{this.props.term.label}</label></li>;
    }
  });

  var VocabularyComponent = React.createClass({
    render: function () {
      var items = _.map(this.state.terms, function (term) {
        return <TermComponent term={term} key={term.label} />;
      });

      return <ul className="icheck-list">
          <div className="panel-heading">
            <h4 className="panel-title">
              <a className="accordion-toggle" data-toggle="collapse"
                 data-parent="#accordion"
                 href={'#collapse-' + this.props.vocabulary.slug}>
                {this.props.vocabulary.name}
              </a>
            </h4>
          </div>
          <div id={'collapse-' + this.props.vocabulary.slug}
               className="panel-collapse collapse in">
            <div className="panel-body">
              <ul>
                {items}
              </ul>
            </div>
          </div>
        <li>
          <div className="input-group">
            <input type="text" value={this.state.newTermLabel}
              className="form-control"
              placeholder="Add new term..." onChange={this.updateAddTermText}/>
              <span className="input-group-btn">
                <a className="btn btn-white"
                  type="button" onClick={this.handleAddTermClick}><i
                  className="fa fa-plus-circle"
                ></i></a>
              </span>
          </div>
        </li>
      </ul>;
    },
    handleAddTermClick: function() {
      var thiz = this;
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
          thiz.props.reportError("Error occurred while adding new term.");
        })
      .done(function(newTerm) {
          thiz.setState({
            newTermLabel: null,
            terms: thiz.state.terms.concat([newTerm])
          });

          // clear errors
          thiz.props.reportError(null);
        });
    },
    updateAddTermText: function(e) {
      this.setState({newTermLabel: e.target.value});
    },
    getInitialState: function() {
      return {
        newTermLabel: "",
        terms: this.props.terms
      };
    }
  });

  var AddTermsComponent = React.createClass({
    render: function () {
      var repoSlug = this.props.repoSlug;
      var reportError = this.reportError;
      var items = _.map(this.props.vocabularies, function (obj) {
        return <VocabularyComponent
          vocabulary={obj.vocabulary}
          terms={obj.terms}
          key={obj.vocabulary.slug}
          repoSlug={repoSlug}
          reportError={reportError}
          />;
      });
      return <div className="panel-group lore-panel-group">
        <div className="panel panel-default">
        </div>
        <span style={{color: "red"}}>
          {this.state.errorText}
        </span>
        {items}
      </div>;

    },
    reportError: function(msg) {
      if (msg) {
        console.error(msg);
      }
      this.setState({errorText: msg});
    },
    getInitialState: function() {
      return {
        errorText: ""
      };
    }
  });

  var AddVocabulary = React.createClass({
    mixins: [React.addons.LinkedStateMixin],
    getInitialState: function() {
      return {
        name: '',
        description: '',
        vocabulary_type: 'm',
        required: false,
        weight: 2147483647
      };
    },
    updateVocabularyType: function(e) {
      this.setState({vocabulary_type: e.target.value});
      e.target.isChecked = true;
    },
    submitForm: function(e) {
      e.preventDefault();
      var thiz = this;
      var vocabularyData = {
        name: this.state.name,
        description: this.state.description,
        vocabulary_type: this.state.vocabulary_type,
        required: this.state.required,
        weight: this.state.weight
      };
      $.ajax({
        type: "POST",
        url: API_ROOT_VOCAB_URL,
        data: vocabularyData
      }).fail(function(data) {
        thiz.setState({
          errorMessage: 'There was a problem adding the Vocabulary'
        });
        console.error(data);
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
      var errorBox = null;
      if (this.state.errorMessage !== undefined) {
        errorBox = <div className="alert alert-danger alert-dismissible">
                     {this.state.errorMessage}
                   </div>;
      }
      return (
        <form className="form-horizontal" onSubmit={this.submitForm}>
          {errorBox}
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
            <div className="radio">
              <label htmlFor="managed_vocabulary_type">
                <input id="managed_vocabulary_type" type="radio"
                  name="vocabulary_type" value="m"
                  onChange={this.updateVocabularyType} />
                    Managed
              </label>
            </div>
            <div className="radio">
              <label htmlFor="managed_vocabulary_type">
                <input id="free_vocabulary_type" type="radio"
                  name="vocabulary_type" value="f"
                  onChange={this.updateVocabularyType} />
                    Tag Style (on the fly)
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
        vocabularies: this.props.vocabularies
      };
    },
    addVocabulary: function(vocab) {
      // Wrap vocab in expected structure
      var newVocab = {
        terms: [],
        vocabulary: vocab
      };
      var vocabularies = this.state.vocabularies;
      vocabularies.push(newVocab);
      this.setState({vocabularies: vocabularies});
    },
    render: function() {
      return (
        <div className="tab-content drawer-tab-content">
          <div className="tab-pane active" id="tab-taxonomies">
            <AddTermsComponent
              vocabularies={this.state.vocabularies}
              repoSlug={this.props.repoSlug}/>
          </div>
          <div className="tab-pane drawer-tab-content" id="tab-vocab">
            <AddVocabulary updateParent={this.addVocabulary}
              repoSlug={this.props.repoSlug}/>
          </div>
        </div>
      );
    }
  });

  return function (repoSlug) {
    API_ROOT_VOCAB_URL = '/api/v1/repositories/' + repoSlug + '/vocabularies/';
    $.get(API_ROOT_VOCAB_URL)
      .then(function (data) {
        var promises = _.map(data.results, function (vocabulary) {
          return $.get("/api/v1/repositories/" + repoSlug +
            "/vocabularies/" + vocabulary.slug + "/terms/")
            .then(function (result) {
              return {terms: result.results, vocabulary: vocabulary};
            }).fail(function(obj) {
              throw obj;
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
      })
      .then(function (vocabularies) {
        React.render(
          <TaxonomyComponent vocabularies={vocabularies} repoSlug={repoSlug}/>,
          $('#taxonomy-component')[0]);
      });
  };

});
