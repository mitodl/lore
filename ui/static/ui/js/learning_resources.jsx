define('learning_resources', [
  'reactaddons', 'jquery', 'lodash', 'utils', 'select2'], function (
  React, $, _, Utils) {
  'use strict';

  var StatusBox = Utils.StatusBox;

  var VocabularyOption = React.createClass({
    applySelect2: function () {
      //this function can be used only if the component has been mounted
      var options = _.map(this.props.terms, function (term) {
        return {
          id: term.slug,
          text: term.label
        };
      });
      var thiz = this;
      var isMultiTerms = this.props.vocabulary.multi_terms;
      //not allowing the clear for the multi terms dropdown
      var allowClear = !isMultiTerms;
      //apply select2 to the right elements
      $(React.findDOMNode(this)).find('select').select2({
        multiple: isMultiTerms,
        data: options,
        placeholder: "Select a value for " + this.props.vocabulary.name,
        allowClear: allowClear,
        theme: "bootstrap",
      })
      .val(this.props.selectedTerms)
      .trigger('change')
      .on('change', function () {
        var selectValues = [].concat($(this).val());
        //if there are single select dropdowns, .val() can return null
        selectValues = _.filter(selectValues, function(value) {
          return value !== null;
        });
        thiz.props.updateTerms(thiz.props.vocabulary.slug, selectValues);
      });
    },
    render: function () {
      return <div className="form-group">
        <label className="col-sm-6 control-label">
        {this.props.vocabulary.name}
          </label>
        <div className="col-sm-6">
          <select className="form-control">
          </select>
        </div>
      </div>;
    },
    componentDidMount: function() {
      this.applySelect2();
    },
    componentDidChange: function() {
      this.applySelect2();
    },
    componentWillChange: function() {
      //before react applies the changes need to detach the event handler
      //from the select node
      $(React.findDOMNode(this)).find('select').off('change');
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
