define('listing_resources', ['react', 'jquery', 'lodash', 'utils'],
  function (React, $, _, Utils) {
    'use strict';

    var ICheckbox = Utils.ICheckbox;

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

    var Facet = React.createClass({
      render: function() {
        var icon = null;
        if (this.props.facetId === 'resource_type') {
          var src = this.props.imageDir + "/" + getImageFile(this.props.id);
          icon = <span className="min-width">
            <img src={src} className="ic-custom"/>
            </span>;
        }

        return <li>
          <ICheckbox
            id={"check-" + this.props.id}
            tabIndex="add"
            className="icheck-11" onChange={this.handleChange}
            checked={this.props.selected} />
          {icon}
          <label htmlFor={"check-" + this.props.id}>
            {this.props.label}
          </label>
          <span className="badge">
            {this.props.count}
          </span>
        </li>;
      },
      handleChange: function(e) {
        this.props.updateFacets(
          this.props.facetId, this.props.id, e.target.checked);
      }
    });

    var FacetGroup = React.createClass({
      render: function() {
        var thiz = this;
        var facets = _.map(this.props.values, function(value) {
          var selected = thiz.props.selectedFacets[value.key];

          return <Facet label={value.label}
                        id={value.key}
                        count={value.count}
                        key={value.key}
                        facetId={thiz.props.id}
                        imageDir={thiz.props.imageDir}
                        updateFacets={thiz.props.updateFacets}
                        selected={selected}
            />;
        });

        var collapseId = "collapse-" + this.props.id;

        return <div className="panel panel-default">
          <div className="panel-heading">
            <h4 className="panel-title">
              <a className="accordion-toggle"
                 href={"#" + collapseId}
                 data-parent="#accordion"
                 data-toggle="collapse"
                >
                {this.props.label}
              </a>
            </h4>
          </div>
          <div className="panel-collapse collapse in" id={collapseId}>
            <div className="panel-body">
              <ul className="icheck-list">
                {facets}
              </ul>
            </div>
          </div>
        </div>;
      }
    });

    var Facets = React.createClass({
      render: function() {
        var thiz = this;
        var facets = [];

        var makeFacetGroup = function(values) {
          if (!values.values.length) {
            return null;
          }
          var selectedFacets = {};
          if (thiz.props.selectedFacets[values.facet.key] !== undefined) {
            selectedFacets = thiz.props.selectedFacets[values.facet.key];
          }

          return <FacetGroup
            values={values.values}
            label={values.facet.label}
            id={values.facet.key}
            key={values.facet.key}
            updateFacets={thiz.props.updateFacets}
            imageDir={thiz.props.imageDir}
            selectedFacets={selectedFacets}
            />;
        };

        _.each(["course", "run", "resource_type"], function(key) {
          facets.push(makeFacetGroup(thiz.props.facetCounts[key]));
        });

        _.each(this.props.facetCounts, function(values) {
          var key = values.facet.key;
          if (key !== "course" && key !== "run" && key !== "resource_type") {
            facets.push(makeFacetGroup(values));
          }
        });

        return <div className="panel-group lore-panel-group">{facets}</div>;
      }
    });

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

    var ListingPage = React.createClass({
      render: function() {
        return <div>
          <div className="col-md-3">
            <div className="panel-group lore-panel-group">
              <Facets facetCounts={this.props.facetCounts}
                      updateFacets={this.props.updateFacets}
                      selectedFacets={this.props.selectedFacets}
                      imageDir={this.props.imageDir} />
            </div>
          </div>
          <div className="col-md-9 col-results">
            <Listing {...this.props} />
          </div>
        </div>;
      }
    });

    return {
      loader: function(listingOptions, container, openExportsPanel,
                       openResourcePanel, updateFacets, selectedFacets) {
        return React.render(
          <ListingPage {...listingOptions}
                   openExportsPanel={openExportsPanel}
                   openResourcePanel={openResourcePanel}
                   updateFacets={updateFacets}
                   selectedFacets={selectedFacets}
            />,
          container
        );
      },
      getImageFile: getImageFile,
      ExportButton: ExportButton,
      ExportLink: ExportLink,
      SortingDropdown: SortingDropdown,
      ListingResource: ListingResource,
      Listing: Listing,
      ListingPage: ListingPage,
      FacetGroup: FacetGroup,
      Facet: Facet,
      Facets: Facets
    };
  }
);
