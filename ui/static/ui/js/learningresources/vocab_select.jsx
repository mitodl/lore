define("vocab_select", ["react", "lodash", "select2_component"],
  function (React, _, Select2) {
    'use strict';

    return React.createClass({
      render: function () {
        var options;
        options = _.map(this.props.vocabs, function (vocab) {
          return {
            id: vocab.vocabulary.slug,
            text: vocab.vocabulary.name,
          };
        });

        var slug = this.props.selectedVocabulary.slug;

        var vocabId = "vocab-" + slug;
        return <div className="form-group">
          <label htmlFor={vocabId}
                 className="col-sm-4 control-label">
            Vocabularies</label>

          <div className="col-sm-6">
            <Select2
              key="vocabChooser"
              id={vocabId}
              className="form-control"
              placeholder={"Select a vocabulary"}
              options={options}
              allowClear={false}
              onChange={this.handleChange}
              values={slug}
              multiple={false}
              allowTags={false}
              />
          </div>
        </div>;
      },
      handleChange: function (e) {
        var selectedValue = _.pluck(
          _.filter(e.target.options, function (option) {
            return option.selected && option.value !== null;
          }), 'value');
        this.props.setValues(
          _.pluck(this.props.vocabs, 'vocabulary'), selectedValue[0]
        );

        // clear message
        this.props.reportMessage(undefined);
      }
    });
  }
);
