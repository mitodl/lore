define("lore_data_table", ["lodash", "jquery", "react", "react_datagrid",
    "learning_resources", "static_assets"],
  function (_, $, React, DataGrid, LearningResources,
    StaticAssets) {
    'use strict';

    var LoreDataTable = React.createClass({
      getDefaultProps: function() {
        return {
          pageSize: 20
        };
      },
      getInitialState: function() {
        return {
          sortInfo: [],
          page: 1,
          pageSize: this.props.pageSize,
          columns: this.props.columns,
          filterValues: {}
        };
      },
      calculateDataSlice: function() {
        // filter
        var thiz = this;
        var filteredData = _.filter(this.props.data, function(row) {
          return _.all(thiz.state.filterValues, function(v, k) {
            var uppercaseValue = v.toString().toUpperCase();
            var uppercaseCell = row[k].toString().toUpperCase();
            if (uppercaseCell.indexOf(uppercaseValue) !== -1) {
              return true;
            }
          });
        });

        // sort
        var info = this.state.sortInfo;
        var sortNames = _.map(info, function (x) {
          return x.name;
        });
        var orders = _.map(info, function (x) {
          if (x.dir === 1) {
            return true;
          } else if (x.dir === -1) {
            return false;
          }
          return x.dir;
        });
        var sortedData = _.sortByOrder(filteredData, sortNames, orders);

        // paginate
        var offset = (this.state.page - 1) * this.state.pageSize;
        return [
          sortedData.slice(offset, offset + this.state.pageSize),
          sortedData.length
        ];
      },
      render: function() {
        var pair = this.calculateDataSlice();
        var slice = pair[0];
        var count = pair[1];

        return <DataGrid
          idProperty="lid"
          dataSource={slice}
          columns={this.state.columns}
          sortInfo={this.state.sortInfo}
          onSortChange={this.onSortChange}
          dataSourceCount={count}
          page={this.state.page}
          onPageChange={this.onPageChange}
          pageSize={this.state.pageSize}
          onPageSizeChange={this.onPageSizeChange}
          onColumnResize={this.onColumnResize}
          onFilter={this.handleFilter}
          liveFilter={true}
          />;
      },
      handleFilter: function(column, value, allFilterValues) {
        this.setState({filterValues: allFilterValues});
      },
      onPageChange: function(page) {
        this.setState({page: page});
      },
      onPageSizeChange: function(pageSize) {
        this.setState({pageSize: pageSize});
      },
      onSortChange: function(info) {
        this.setState({sortInfo: info});
      },
      onColumnResize: function(firstCol, firstSize) {
        var columns = _.map(this.state.columns, function(column) {
          if (firstCol.name === column.name) {
            var copy = $.extend({}, column);
            copy.width = firstSize;
            return copy;
          }
          return column;
        });
        this.setState({columns: columns});
      }
    });

    var closeLearningResourcePanel = function() {
      $('.cd-panel').removeClass('is-visible');
    };

    var loader = function(repoSlug, data, container) {
      var columns = [
        {
          name: "lid",
          title: "Resource id",
          type: "number",
          render: function(lid) {
            var onclick = function(e) {
              e.preventDefault();
              // Unmount and remount the component to ensure that its state
              // is always up to date with the rest of the app.
              var resourcePanelDiv = $("#tab-1")[0];
              React.unmountComponentAtNode(resourcePanelDiv);
              React.render(<LearningResources.LearningResourcePanel
                repoSlug={repoSlug}
                learningResourceId={lid}
                refreshFromAPI={function() {}}
                closeLearningResourcePanel={closeLearningResourcePanel}
                />, resourcePanelDiv);
              var staticAssetDiv = $("#tab-3")[0];
              React.unmountComponentAtNode(staticAssetDiv);
              $('.cd-panel').addClass('is-visible');
              React.unmountComponentAtNode(staticAssetDiv);
              React.render(<StaticAssets.StaticAssetsPanel
                repoSlug={repoSlug} learningResourceId={lid}
                key={[repoSlug, lid]}
                />, staticAssetDiv);
            };
            return <a target="_blank" onClick={onclick}>{lid}</a>;
          }
        },
        {
          name: "title",
          title: "Title",
        },
        {
          name: "description",
          title: "Description"
        },
        {
          name: "description_path",
          title: "Path",
        },
        {
          name: "course",
          title: "Course"
        },
        {
          name: "run",
          title: "Run"
        },
        {
          name: "xa_nr_views",
          title: "Views",
          type: "number"
        },
        {
          name: "xa_nr_attempts",
          title: "Attempts",
          type: "number"
        },
        {
          name: "xa_avg_grade",
          title: "Average Grade",
          type: "number"
        },
        {
          name: "preview_url",
          title: "Preview URL",
          render: function(url) {
            return <a href={url} target="_blank">Preview</a>;
          }
        }
      ];

      React.render(<LoreDataTable data={data} columns={columns} />, container);

      //close the lateral panel
      $('.cd-panel').click(function (event) {
        if ($(event.target).is('.cd-panel') ||
          $(event.target).is('.cd-panel-close')) {
          event.preventDefault();
          closeLearningResourcePanel();
        }
      });
    };
    return {
      loader: loader
    };
  }
);
