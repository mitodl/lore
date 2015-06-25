define('setup_manage_taxonomies', ['react', 'lodash'], function (React, _) {
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
            <input type="text" value={this.state.newTermLabel} className="form-control"
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
      ).fail(function(e) {
          thiz.props.reportError("Error occurred while adding new term.");
        })
      .done(function(newTerm) {
          thiz.setState({
            newTermLabel: null,
            terms: thiz.state.terms.concat([newTerm])
          });
        });
    },
    updateAddTermText: function(e) {
      this.setState({newTermLabel: e.target.value})
    },
    getInitialState: function() {
      return {
        newTermLabel: "",
        terms: this.props.terms
      }
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
      console.error(msg);
      this.setState({errorText: msg});
    },
    getInitialState: function() {
      return {
        errorText: ""
      };
    }
  });

  return function (repoSlug) {
    API_ROOT_VOCAB_URL = '/api/v1/repositories/' + repoSlug + '/vocabularies/'
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
          }
          else {
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
          <AddTermsComponent vocabularies={vocabularies} repoSlug={repoSlug}/>,
          $('#tab-taxonomies')[0]);
      });
  };

});
