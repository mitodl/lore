define('vocabulary_component', ['react', 'lodash', 'jquery', 'term_component'],
  function (React, _, $, TermComponent) {
    'use strict';

    return React.createClass({
      mixins: [React.addons.LinkedStateMixin],
      render: function () {
        var thiz = this;
        var sortedTerms = _.sortBy(this.props.terms, function(term) {
          return term.label.trim().toLowerCase();
        });
        var items = _.map(sortedTerms, function (term) {
          return <TermComponent
            deleteTerm={thiz.props.deleteTerm}
            updateTerm={thiz.props.updateTerm}
            vocabulary={thiz.props.vocabulary}
            repoSlug={thiz.props.repoSlug}
            term={term}
            key={term.id}
            renderConfirmationDialog={thiz.props.renderConfirmationDialog}
            refreshFromAPI={thiz.props.refreshFromAPI}
            setLoadedState={thiz.props.setLoadedState}
            />;
        });

        return <div className="panel panel-default">
          <div className="panel-heading">
            <h4 className="panel-title">
              <span className="utility-features">
                <a href="#" onClick={this.onEdit}>
                  <i className="fa fa-pencil"></i>
                </a> <a href="#"
                        data-toggle="modal" data-target="#confirm-delete"
                        onClick={this.onDeleteHandler}
                        className="delete-vocabulary">
                <i className="fa fa-remove"></i>
              </a>
              </span> <a className="accordion-toggle vocab-title"
                         data-toggle="collapse"
                         data-parent="#accordion"
                         href={'#collapse-vocab-' + this.props.vocabulary.id}>
              {this.props.vocabulary.name}
            </a>
            </h4>
          </div>
          <div id={'collapse-vocab-' + this.props.vocabulary.id}
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
                        <a href="#" className="btn btn-white"
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
      onDeleteHandler: function () {
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
      confirmedDeleteResponse: function (success) {
        var thiz = this;
        if (success) {
          this.props.setLoadedState(false);
          var vocab = this.props.vocabulary;
          var API_ROOT_VOCAB_URL = '/api/v1/repositories/' +
            this.props.repoSlug + '/vocabularies/' + vocab.slug + '/';
          $.ajax({
            type: "DELETE",
            url: API_ROOT_VOCAB_URL
          }).fail(function () {
            var message = "Unable to delete vocabulary '" + vocab.name + "'";
            thiz.props.reportMessage({error: message});
          }).then(function () {
            thiz.props.deleteVocabulary(vocab.id);

            thiz.props.refreshFromAPI();
          }).always(function () {
            thiz.props.setLoadedState(true);
          });
        }
      },
      onEdit: function (e) {
        e.preventDefault();
        this.props.editVocabulary(this.props.vocabulary.id);
      },
      onKeyUp: function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          this.handleAddTerm();
        }
      },
      handleAddTermClick: function (e) {
        e.preventDefault();
        this.handleAddTerm();
      },
      handleAddTerm: function () {
        var thiz = this;
        var API_ROOT_VOCAB_URL = '/api/v1/repositories/' + this.props.repoSlug +
          '/vocabularies/';
        this.props.setLoadedState(false);
        $.ajax({
            type: "POST",
            url: API_ROOT_VOCAB_URL + this.props.vocabulary.slug + "/terms/",
            data: JSON.stringify({
              label: this.state.newTermLabel,
              weight: 1
            }),
            contentType: "application/json; charset=utf-8"
          }
        ).fail(function () {
            thiz.props.reportMessage({
              error: "Error occurred while adding new term."
            });
          })
          .then(function (newTerm) {
            thiz.props.addTerm(thiz.props.vocabulary.id, newTerm);
            thiz.setState({
              newTermLabel: null
            });

            // clear errors
            thiz.props.reportMessage(null);
            thiz.props.refreshFromAPI();
          }).always(function () {
            thiz.props.setLoadedState(true);
          });
      },
      getInitialState: function () {
        return {
          newTermLabel: ""
        };
      },
    });
  }
);
