define('add_terms_component', ['react', 'lodash', 'jquery', 'uri',
    'utils', 'status_box', 'vocabulary_component'],
  function (React, _, $, URI, Utils, StatusBox, VocabularyComponent) {
    'use strict';

    return React.createClass({
      render: function () {
        var repoSlug = this.props.repoSlug;
        var thiz = this;
        var items = _.map(this.props.vocabularies, function (obj) {
          return <VocabularyComponent
            deleteTerm={thiz.props.deleteTerm}
            updateTerm={thiz.props.updateTerm}
            vocabulary={obj.vocabulary}
            deleteVocabulary={thiz.props.deleteVocabulary}
            editVocabulary={thiz.props.editVocabulary}
            terms={obj.terms}
            key={obj.vocabulary.id}
            repoSlug={repoSlug}
            reportMessage={thiz.reportMessage}
            addTerm={thiz.props.addTerm}
            renderConfirmationDialog={thiz.props.renderConfirmationDialog}
            refreshFromAPI={thiz.props.refreshFromAPI}
            setLoadedState={thiz.props.setLoadedState}
            />;
        });
        return <div className="panel-group lore-panel-group">
          <div className="panel panel-default">
          </div>
          <StatusBox message={this.props.message}/>
          {items}
        </div>;

      },
      reportMessage: function (message) {
        this.props.reportMessage(message);
      },
      getInitialState: function () {
        return {
          message: undefined
        };
      }
    });

  }
);
