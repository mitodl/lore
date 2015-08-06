define('learning_resources', [
  'reactaddons', 'jquery', 'lodash', 'utils'], function (
  React, $, _, Utils) {
  'use strict';

  var StatusBox = Utils.StatusBox;
  var Select2 = Utils.Select2;

  var VocabularyOption = React.createClass({
    render: function () {
      var options = _.map(this.props.terms, function (term) {
        return {
          id: term.slug,
          text: term.label
        };
      });

      return <div className="form-group">
        <label className="col-sm-6 control-label">
        {this.props.vocabulary.name}
          </label>
        <div className="col-sm-6">
          <Select2
            className="form-control"
            placeholder={"Select a value for " + this.props.vocabulary.name}
            options={options}
            onChange={this.handleChange}
            values={this.props.selectedTerms}
            multiple={this.props.vocabulary.multi_terms}
            />
        </div>
      </div>;
    },
    handleChange: function(e) {
      var selectValues = _.pluck(
        _.filter(e.target.options, function(option) {
          return option.selected && option.value !== null;
        }), 'value');
      this.props.updateTerms(this.props.vocabulary.slug, selectValues);
    }
  });

  var LearningResourcePanel = React.createClass({
    mixins: [React.addons.LinkedStateMixin],
    render: function () {
      var thiz = this;
      var vocabulariesAndTerms = this.state.vocabulariesAndTerms;
      var options = _.map(vocabulariesAndTerms, function (pair) {
        var updateTerms = function(vocabSlug, newTermsSlug) {
          var newVocabulariesAndTerms = _.map(vocabulariesAndTerms,
            function(tuple) {
              if (vocabSlug === tuple.vocabulary.slug) {
                return {
                  vocabulary: tuple.vocabulary,
                  terms: tuple.terms,
                  selectedTerms: newTermsSlug
                };
              } else {
                return tuple;
              }
            });

          thiz.setState({
            vocabulariesAndTerms: newVocabulariesAndTerms
          });
        };

        return <VocabularyOption
          vocabulary={pair.vocabulary}
          terms={pair.terms}
          selectedTerms={pair.selectedTerms}
          key={pair.vocabulary.slug}
          updateTerms={updateTerms}
          />;
      });

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

          {options}
          <div className="form-group form-desc">
            <label className="col-sm-12 control-label">Description</label>
              <textarea
                className="form-control col-sm-12 textarea-desc"
                valueLink={this.linkState('description')}>
              </textarea>
          </div>
          <p>
            <button className="btn btn-lg btn-primary"
                    onClick={this.saveForm}>
              Save
            </button>
          </p>
        </form>
      </div>;
    },
    selectXml: function (event) {
      event.preventDefault();
      $('.textarea-xml').select();
    },
    saveForm: function (event) {
      event.preventDefault();
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
            vocabulariesAndTerms: vocabulariesAndTerms
          });
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
        vocabulariesAndTerms: []
      };
    }
  });

  return {
    VocabularyOption: VocabularyOption,
    LearningResourcePanel: LearningResourcePanel,
    loader: function (repoSlug, learningResourceId, container) {
      // Unmount and remount the component to ensure that its state
      // is always up to date with the rest of the app.
      React.unmountComponentAtNode(container);
      React.render(<LearningResourcePanel
        repoSlug={repoSlug} learningResourceId={learningResourceId}
        />, container);
    }
  };
});
