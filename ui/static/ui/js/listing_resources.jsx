define('listing_resources', ['react', 'jquery', 'lodash'],
  function (React, $, _) {
    'use strict';

    var SortingDropdown = React.createClass({
      render: function() {
        var thiz = this;

        var sortingLinks = _.map(this.props.sortingOptions.all,
          function (sortingOption) {
            var url = "/repositories/" + thiz.props.repoSlug +
              "/" + thiz.props.qsPrefix + "sortby=" +
              encodeURIComponent(sortingOption[0]);
            return <li key={sortingOption[0]}>
              <a href={url}>{sortingOption[1]}</a>
            </li>;
          }
        );

        return <div>
          <span>Sort by</span>: <div className="btn-group">
            <button type="button" className="btn btn-default">
              {this.props.sortingOptions.current[1]}
            </button>
            <button type="button" className="btn btn-default dropdown-toggle"
                    data-toggle="dropdown" aria-haspopup="true"
                    aria-expanded="false">
              <span className="caret"></span>
              <span className="sr-only">Toggle Dropdown</span>
            </button>
            <ul className="dropdown-menu">
              {sortingLinks}
            </ul>
          </div>
        </div>;
      }
    });

    var ExportButton = React.createClass({
      render: function() {
        var badge = null;
        if (this.props.count > 0) {
          badge = <span> <span className='badge'>
            {this.props.count}
            </span></span>;
        }

        return <button className="btn btn-primary"
                       onClick={this.props.openExportsPanel}>
          Export{badge}
        </button>;
      }
    });

    var ExportLink = React.createClass({
      render: function() {
        var className = "fa fa-arrow-right";
        if (this.props.selected) {
          className = "fa fa-check";
        }

        return <a className="link-export" href="#"
                  onClick={this.props.onClick}>
          <i className={className} /> Export</a>;
      }
    });

    var getImageFile = function(resourceType) {
      if (resourceType === 'chapter') {
        return 'ic-book.png';
      } else if (resourceType === 'sequential') {
        return 'ic-sequential.png';
      } else if (resourceType === 'vertical') {
        return 'ic-vertical.png';
      } else if (resourceType === 'problem') {
        return 'ic-pieces.png';
      } else if (resourceType === 'video') {
        return 'ic-video.png';
      } else {
        return 'ic-code.png';
      }
    };

    var ListingResource = React.createClass({
      render: function() {
        // Select image based on type.
        var resource = this.props.resource;

        var imageUrl = this.props.imageDir + "/" +
          getImageFile(resource.resource_type);

        var title = "No Title";
        if (resource.title !== "") {
          title = resource.title;
        }

        var description = "No description provided.";
        if (resource.description !== "") {
          description = resource.description;
        }

        return <div className="row">
          <div className="col-md-10">
            <div className="tile">
              <div className="tile-icon tile-color-1">
                <img className="ic-custom" src={imageUrl} />
              </div>
              <div className="tile-content">
                <h2>
                  <a href="#" className="cd-btn"
                     data-learningresource-id={resource.lid}
                    onClick={this.handleResourceClick}>{title}</a>
                </h2>

                <div className="tile-meta">
                  <span className="meta-item">{resource.description_path}</span>
                </div>

                <div className="tile-blurb">{description}</div>
                <div className="tile-meta">
                  <span className="meta-item">{resource.course}</span>
                  <span className="meta-item">{resource.run}</span>
                  <span className="sub-meta">
                    <span className="meta-item mi-col-1">
                      <i className="fa fa-eye"></i> {resource.xa_nr_views}
                    </span>
                    <span className="meta-item mi-col-2">
                      <i className="fa fa-edit"></i> {resource.xa_nr_attempts}
                    </span>
                    <span className="meta-item mi-col-3">
                      <i className="fa fa-graduation-cap">
                      </i> {resource.xa_avg_grade}
                    </span>
                    <span className="meta-item mi-col-4">
                      <a href={resource.preview_url} target="_blank">Preview</a>
                    </span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="col-md-2 col-export">
            <ExportLink selected={this.props.exportSelected}
                        onClick={this.handleExportLinkClick} />
          </div>
        </div>;
      },
      handleExportLinkClick: function(e) {
        e.preventDefault();
        this.props.updateExportLinkClick(
          this.props.resource.lid, !this.props.exportSelected
        );
      },
      handleResourceClick: function(e) {
        e.preventDefault();
        this.props.openResourcePanel(this.props.resource.lid);
      }
    });

    var Listing = React.createClass({
      getInitialState: function() {
        var exportSelection = {};
        _.each(this.props.resources, function(resource) {
          exportSelection[resource.lid] = false;
        });

        _.each(this.props.allExports, function(resourceId) {
          // allExports contains every export for the repo
          // but exportSelection should only contain exports on the current
          // page.
          if (_.has(exportSelection, resourceId)) {
            exportSelection[resourceId] = true;
          }
        });

        return {
          exportSelection: exportSelection
        };
      },
      render: function() {
        var thiz = this;
        var resources = _.map(this.props.resources, function(resource) {
          var exportSelected = thiz.state.exportSelection[resource.lid];
          return <ListingResource
            resource={resource}
            key={resource.lid}
            exportSelected={exportSelected}
            imageDir={thiz.props.imageDir}
            repoSlug={thiz.props.repoSlug}
            openResourcePanel={thiz.props.openResourcePanel}
            updateExportLinkClick={thiz.updateExportLinkClick} />;
        });

        var sortingDropdown = null;
        if (this.props.resources.length > 0) {
          sortingDropdown = <SortingDropdown
            repoSlug={this.props.repoSlug}
            qsPrefix={this.props.qsPrefix}
            sortingOptions={this.props.sortingOptions} />;
        }

        var exportButton = null;
        var count = 0;
        _.each(this.props.allExports, function(resourceId) {
          if (!_.has(thiz.state.exportSelection, resourceId)) {
            // exportSelection only contains info about exports on the current
            // page, so if it's not in there we can safely count it.
            count++;
          }
        });
        _.each(thiz.state.exportSelection, function(selected) {
          if (selected) {
            // If it is on the current page count it if it is checked.
            count++;
          }
        });

        if (count > 0) {
          exportButton = <ExportButton
            count={count}
            openExportsPanel={thiz.props.openExportsPanel}/>;
        }

        return <div>
          <div className="row grid-row-top">
            <div className="col-md-5">
              {sortingDropdown}
            </div>
            <div className="col-md-7 text-right"></div>
            <div className="col-md-5"></div>
            <div className="col-md-7 text-right">
              {exportButton}
            </div>
          </div>
          {resources}
        </div>;
      },
      updateExportLinkClick: function(resourceId, selected) {
        var thiz = this;
        var updateCheck = function() {
          var exportSelection = $.extend({}, thiz.state.exportSelection);
          exportSelection[resourceId] = selected;
          thiz.setState({exportSelection: exportSelection});
        };

        if (!selected) {
          // Remove an item from export cart.
          $.ajax({
            type: "DELETE",
            url: "/api/v1/repositories/" + this.props.repoSlug +
            "/learning_resource_exports/" + this.props.loggedInUsername + "/" +
            resourceId + "/"
          }).then(function () {
            updateCheck();
          });
        } else {
          // Add an item to export cart.
          $.post("/api/v1/repositories/" + this.props.repoSlug +
            "/learning_resource_exports/" + this.props.loggedInUsername + "/", {
            id: resourceId
          }).then(function () {
            updateCheck();
          });
        }
      }
    });

    return {
      loader: function(listingOptions, container, openExportsPanel,
                       openResourcePanel) {
        React.render(
          <Listing {...listingOptions}
                   openExportsPanel={openExportsPanel}
                   openResourcePanel={openResourcePanel}
            />,
          container
        );
      },
      getImageFile: getImageFile,
      ExportButton: ExportButton,
      ExportLink: ExportLink,
      SortingDropdown: SortingDropdown,
      ListingResource: ListingResource,
      Listing: Listing
    };
  }
);
