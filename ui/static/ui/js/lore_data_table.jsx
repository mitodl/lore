define("lore_data_table", ["lodash", "jquery", "react", "react_datagrid",
    "manage_taxonomies", "learning_resources", "static_assets"],
  function (_, $, React, DataGrid, ManageTaxonomies, LearningResources,
    StaticAssets) {

    var LoreDataTable = React.createClass({
      getDefaultProps: function() {
        return {
          pageSize: 20
        }
      },
      getInitialState: function() {
        return {
          sortInfo: [],
          page: 1,
          pageSize: this.props.pageSize,
          columns: this.props.columns,
          filterValues: {}
        }
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
          }
          else if (x.dir === -1) {
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
      onColumnResize: function(firstCol, firstSize, secondCol, secondSize) {
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

    var loader = function(repoSlug, data, container) {
      var columns = [
        {
          name: "lid",
          title: "Resource id",
          type: "number",
          render: function(lid) {
            var onclick = function(e) {
              LearningResources.loader(
                repoSlug, lid, function() {}, $("#tab-1")[0]);
              $('.cd-panel').addClass('is-visible');
              StaticAssets.loader(
                repoSlug, lid, $("#tab-3")[0]);
              e.preventDefault();
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
          title: "Description Path",
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
          title: "Number of Views",
          type: "number"
        },
        {
          name: "xa_nr_attempts",
          title: "Number of Attempts",
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
      $('.cd-panel').on('click', function (event) {
        if ($(event.target).is('.cd-panel') ||
          $(event.target).is('.cd-panel-close')) {
          $('.cd-panel').removeClass('is-visible');
          event.preventDefault();
        }
      });
    };
    return {
      loader: loader
    };
  }
);
