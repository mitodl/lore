define('xml_panel',
  ['react', 'jquery'],
  function (React, $) {
  'use strict';

  var XmlPanel = React.createClass({
    render: function () {
      return <div>
          <textarea className="form-control textarea-xml"
                    readOnly="true"
                    value={this.state.contentXml}
          />
          <p className="text-right">
            <a id="copy-textarea-xml" href="#"
               className="btn btn-white"
               onClick={this.selectXml}>Select XML</a>
          </p>
      </div>;
    },

    selectXml: function (event) {
      event.preventDefault();
      $(React.findDOMNode(this)).find(".textarea-xml").select();
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
        var title = data.title;
        thiz.setState({
          contentXml: contentXml,
          title: title,
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
      };
    }
  });

  return {
    XmlPanel: XmlPanel,
    loader: function (repoSlug, learningResourceId, container) {
      // Unmount and remount the component to ensure that its state
      // is always up to date with the rest of the app.
      React.unmountComponentAtNode(container);
      React.render(<XmlPanel
        repoSlug={repoSlug}
        learningResourceId={learningResourceId}
        key={[repoSlug, learningResourceId]}
        />, container);
    }
  };
});
