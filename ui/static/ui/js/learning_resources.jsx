define('learning_resources', [
  'reactaddons', 'jquery', 'lodash', 'utils'], function (React, $, _, Utils) {
  'use strict';

  var VocabularyOption = React.createClass({
    render: function () {
      var options = _.map(this.props.terms, function (term) {
        return <option key={term.slug}
                       value={term.slug}>
          {term.label}
        </option>;
      });

      return <div className="form-group">
        <label className="col-sm-6 control-label">
        {this.props.vocabulary.name}
          </label>
        <div className="col-sm-6">
          <select className="form-control" value={this.props.selectedTerm}
            onChange={this.handleChange}>
            <option key="" value=""></option>
            {options}
          </select>
        </div>
      </div>;
    },
    handleChange: function(e) {
      this.props.updateTerm(this.props.vocabulary.slug, e.target.value);
    }
  });

  var LearningResourcePanel = React.createClass({
    mixins: [React.addons.LinkedStateMixin],
    render: function () {
      var thiz = this;
      var vocabulariesAndTerms = this.state.vocabulariesAndTerms;
      var options = _.map(vocabulariesAndTerms, function (pair) {
        var updateTerm = function(vocabSlug, newTermSlug) {
          var newVocabulariesAndTerms = _.map(vocabulariesAndTerms,
            function(tuple) {
              if (vocabSlug === tuple.vocabulary.slug) {
                return {
                  vocabulary: tuple.vocabulary,
                  terms: tuple.terms,
                  selectedTerm: newTermSlug
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
          selectedTerm={pair.selectedTerm}
          key={pair.vocabulary.slug}
          updateTerm={updateTerm}
          />;
      });

      var errorBox = null;
      if (this.state.errorText !== undefined) {
        errorBox = <div className="alert alert-danger alert-dismissible">
          {this.state.errorText}
        </div>;
      }
      var messageBox = null;
      if (this.state.messageText !== undefined) {
        messageBox = <div className="alert alert-success alert-dismissible">
          {this.state.messageText}
          </div>;
      }
      return <div>
        <form className="form-horizontal">
          {errorBox}
          {messageBox}
          <textarea className="form-control textarea-xml"
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
          return tuple.selectedTerm;
        });
      terms = _.filter(terms, function(selectedTerm) {
        return selectedTerm;
      });

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
          errorText: undefined,
          messageText: "Form saved successfully!"
        });
      }).fail(function () {
        thiz.setState({
          errorText: "Unable to save form",
          messageText: undefined
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
          messageText: undefined,
          errorText: undefined,
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

              var selectedTerm = _.result(_.find(terms, function(term) {
                return _.includes(selectedTerms, term.slug);
              }), 'slug');

              return {
                vocabulary: vocabulary,
                terms: terms,
                selectedTerm: selectedTerm
              };
            });

          thiz.setState({
            vocabulariesAndTerms: vocabulariesAndTerms
          });
        }).fail(function () {
          thiz.setState({
            errorText: "Unable to read information about learning resource.",
            messageText: undefined
          });
        });

      }).fail(function () {
          thiz.setState({
            errorText: "Unable to read information about learning resource.",
            messageText: undefined
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
