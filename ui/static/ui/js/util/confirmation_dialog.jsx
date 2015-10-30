define("confirmation_dialog", ["react", "jquery"],
  function (React, $) {
    'use strict';

    /**
     * Callback to send confirmation status.
     *
     * @callback confirmationResponse - Call back that sends confirmation status
     * @param {bool} status - Confirmation status
     */

    /**
     * Generic confirmation dialog.
     * <ConfirmationDialog
     *       actionButtonName={confirmationDialogActionButtonName}
     *       title={confirmationDialogTitle}
     *       message={confirmationDialogMessage}
     *       description={description}
     *       confirmationSuccess={confirmationSuccess} />,
     *
     * @param {String} actionButtonName - Name of action button can be any of delete, remove, ok etc
     * @param {String} actionButtonClass - Class(es) for action button
     * @param {String} title - Title/heading of confirmation dialog
     * @param {String} message - Content of dialog
     * @param {String} description - Description of message
     * @param {confirmationResponse} confirmationSuccess - Call back that sends confirmation status
     */
    return React.createClass({
      getDefaultProps: function () {
        return {
          actionButtonName: 'Confirm',
          actionButtonClass: 'btn btn-ok'
        };
      },
      render: function () {
        var title = '';
        var description = '';
        if (this.props.title) {
          title = <h4 className="modal-title">{this.props.title}</h4>;
        }

        if (this.props.description) {
          description = <p className="confirmation-description">
            {this.props.description}
          </p>;
        }
        return (
          <div className="modal fade">
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <button type="button" className="close"
                          data-dismiss="modal"><i className="fa fa-remove"/>
                  </button>
                  {title}
                </div>
                <div className="modal-body">
                  <p>{this.props.message}</p>
                  {description}
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-default"
                          data-dismiss="modal"
                          onClick={this.confirmationFailure}>Cancel
                  </button>
                  <button className={this.props.actionButtonClass}
                          data-dismiss="modal"
                          onClick={this.confirmationSuccess}
                    >{this.props.actionButtonName}</button>
                </div>
              </div>
            </div>
          </div>
        );
      },
      componentDidMount: function () {
        $(React.findDOMNode(this)).modal('show');
      },
      confirmationSuccess: function () {
        this.props.confirmationHandler(true, this.props.tag);
      },
      confirmationFailure: function () {
        this.props.confirmationHandler(false, this.props.tag);
      }
    });
  }
);
