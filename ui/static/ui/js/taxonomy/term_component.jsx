define('term_component', ['react', 'lodash', 'jquery'],
  function (React, _, $) {
    'use strict';

    return React.createClass({
        mixins: [React.addons.LinkedStateMixin],
        getInitialState: function () {
          return {
            formatActionState: 'show',
            errorMessage: ''
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
              className='form-control edit-term-box'/>
              <button
                onClick={this.saveTerm} type="button"
                className="save-button btn btn-primary btn-sm editable-submit">
                <i
                  className="glyphicon glyphicon-ok"></i></button>
              <button type="button"
                      className="btn btn-default btn-sm editable-cancel"
                      onClick={this.cancelAction}><i
                className="glyphicon glyphicon-remove"></i>
              </button>
              {this.state.errorMessage}
            </label>;
            formatActionClassName = "fa fa-pencil no-select";
            editButtonClass = 'format-button disabled';
            deleteButtonClass = 'revert-button disabled';
          } else if (this.state.formatActionState === 'show') {
            label = <label className="term-title"
                           htmlFor="minimal-checkbox-1-11">
              {this.props.term.label}
            </label>;
            formatActionClassName = "fa fa-pencil no-select";
          }

          var listClassName = "form-group";
          if (this.state.errorMessage) {
            listClassName = "form-group has-error";
          }

          return <li className={listClassName}>
        <span className="utility-features">
          <a href="#" onClick={this.editTerm} className={editButtonClass}>
            <i className={formatActionClassName}></i>
          </a> <a className={deleteButtonClass} href="#"
                  onClick={this.deleteTerm}>
          <i className="fa fa-remove"></i>
        </a>
        </span>{label}</li>;
        },
        /**
         * If user selects edit button then open edit mode
         * Else call api to update term.
         */
        editTerm: function (e) {
          e.preventDefault();
          this.setState({
            formatActionState: 'edit',
            label: this.props.term.label
          }, function () {
            var $editText = $(React.findDOMNode(this.refs.editText));
            $editText.focus();
          });
        },
        saveTerm: function () {
          if (this.state.label !== this.props.term.label) {
            this.updateTermSubmit();
          } else {
            this.resetUtilityFeatures();
          }
        },
        /**
         * On Close button select reset term UI
         */
        cancelAction: function () {
          // user is in edit mode. Cancel edit if user presses cross icon.
          this.resetUtilityFeatures();
        },
        deleteTerm: function (e) {
          e.preventDefault();
          var options = {
            actionButtonName: "Delete",
            actionButtonClass: "btn btn-danger btn-ok",
            title: "Confirm Delete",
            message: "Are you sure you want to delete term '" +
            this.props.term.label + "'?",
            description: "Deleting this term will remove it from all " +
            "learning resources.",
            confirmationHandler: this.confirmedDeleteResponse
          };
          this.props.renderConfirmationDialog(options);
        },
        /**
         * Reset term edit UI
         */
        resetUtilityFeatures: function () {
          this.setState(this.getInitialState());
        },
        /**
         * Api call to save term and update parent component
         */
        updateTermSubmit: function () {
          if (_.isEmpty(this.state.label)) {
            this.setState({errorMessage: "Term cannot be empty."});
            return;
          }
          var API_ROOT_VOCAB_URL = '/api/v1/repositories/' +
            this.props.repoSlug + '/vocabularies/' +
            this.props.vocabulary.slug + '/terms/' +
            this.props.term.slug + "/";
          var thiz = this;
          var termData = {
            label: this.state.label,
            weight: this.props.term.weight
          };
          thiz.props.setLoadedState(false);
          $.ajax({
            type: 'PATCH',
            url: API_ROOT_VOCAB_URL,
            data: JSON.stringify(termData),
            contentType: "application/json"
          }).fail(function () {
            thiz.setState({
              errorMessage: 'Unable to update term'
            });
          }).then(function (term) {
            thiz.resetUtilityFeatures();
            thiz.props.updateTerm(thiz.props.vocabulary.id, term);
            thiz.props.refreshFromAPI();
          }).always(function () {
            thiz.props.setLoadedState(true);
          });
        },
        confirmedDeleteResponse: function (success) {
          var thiz = this;
          if (success) {
            var API_ROOT_VOCAB_URL = '/api/v1/repositories/' +
              this.props.repoSlug + '/vocabularies/' +
              this.props.vocabulary.slug + '/terms/' +
              this.props.term.slug + "/";
            thiz.props.setLoadedState(false);
            $.ajax({
              type: 'DELETE',
              url: API_ROOT_VOCAB_URL,
              contentType: "application/json"
            }).fail(function () {
              thiz.setState({
                errorMessage: 'Unable to delete term.'
              });
            }).then(function () {
              thiz.props.deleteTerm(thiz.props.vocabulary.id, thiz.props.term);
              thiz.props.refreshFromAPI();
            }).always(function () {
              thiz.props.setLoadedState(true);
            });
          }
        }
      }
    );
  }
);
