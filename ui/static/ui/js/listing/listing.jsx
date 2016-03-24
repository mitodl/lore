define('listing',
  ['csrf', 'react', 'jquery', 'lodash', 'uri', 'history', 'manage_taxonomies',
    'learning_resources', 'static_assets', 'utils',
    'lr_exports', 'listing_resources', 'xml_panel', 'import_status',
    'bootstrap', 'icheck'],
  function (CSRF, React, $, _, URI, History,
            ManageTaxonomies, LearningResources, StaticAssets,
            Utils, Exports, ListingResources, XmlPanel, ImportStatus) {
    'use strict';

    var EMAIL_EXTENSION = '@mit.edu';

    function formatGroupName(string) {
      string = string.charAt(0).toUpperCase() + string.slice(1);
      return string.substring(0, string.length - 1);
    }

    /* This is going to grow up to check whether
     * the name is a valid Kerberos account
     */
    function isEmail(email) {
      var regex = /^[-a-z0-9~!$%^&*_=+}{\'?]+(\.[-a-z0-9~!$%^&*_=+}{\'?]+)*@([a-z0-9_][-a-z0-9_]*(\.[-a-z0-9_]+)*\.(aero|arpa|biz|com|coop|edu|gov|info|int|mil|museum|name|net|org|pro|travel|mobi|[a-z][a-z])|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,5})?$/i;
      return regex.test(email);
    }

    function formatUserGroups(userList, dest) {
      var $dest = $(dest);
      for (var i = 0; i < userList.length; i++) {
        $dest.append(
          '<div class="row">' +
          '<div class="col-sm-7">' +
          '<div class="cd-panel-members-list-username">' +
          userList[i].username + EMAIL_EXTENSION + '</div>' +
          '</div>\n' +
          '<div class="col-sm-3">' +
          '<div class="cd-panel-members-list-group_type">' +
          formatGroupName(userList[i].group_type) + '</div>' +
          '</div>\n' +
          '<div class="col-sm-2">' +
          '<button ' +
          'class="btn btn-default cd-panel-members-remove" ' +
          'data-username="' + userList[i].username + '" ' +
          'data-group_type="' + userList[i].group_type + '">' +
          '<i class="fa fa-minus"></i>' +
          '</button>' +
          '</div>' +
          '</div>\n');
      }
    }

    function resetUserGroupForm() {
      $('input[name=\'members-username\']').val('');
      $('select[name=\'members-group_type\']').prop('selectedIndex', 0);
    }

    function showMembersAlert(message, mtype) {
      //default value for mtype
      mtype = typeof mtype !== 'undefined' ? mtype : 'success';
      //reset all the classes
      $('#members-alert').html(
        '<div class="alert alert-' + mtype +
        ' fade in out" data-alert="alert">' +
        '<a href="#" class="close" data-dismiss="alert" ' +
        'aria-label="close">&times;</a>\n' + message +
        '</div>');
    }

    function showUpdateAllMembers() {
      //retrieve all the members
      var url = $('.cd-panel-members').data('members-url');
      return Utils.getCollection(url)
        .then(function (results) {
          $('#cd-panel-members-list').empty();
          formatUserGroups(results, '#cd-panel-members-list');
        })
        .fail(function () {
          var message = 'Unable to retrieve list of members.';
          showMembersAlert(message, 'danger');
        });
    }

    var hideTaxonomyPanel = function () {
      $('.cd-panel-2').removeClass('is-visible');
    };

    var showTab = function (tabId) {
      $("a[href='#" + tabId + "']").tab('show');
    };

    var setTabName = function (tabId, newTabName) {
      $("a[href='#" + tabId + "']").find("span").text(newTabName);
    };

    var showConfirmationDialog = function (options) {
      var container = $("#confirmation-container")[0];
      Utils.showConfirmationDialog(
        options,
        container
      );
    };

    var ListingContainer = React.createClass({
      displayName: 'ListingContainer',
      // make data structure to store query parameters
      makeQueryMap: function() {
        var queryMap = {};
        // Populate queryMap with query string key value pairs.
        _.each(URI(this.props.getQueryString()).query(true), function (v, k) {
          if (!Array.isArray(v)) {
            // URI().query(true) will put two or more values with the same
            // key in an array and not use an array for single values.
            // Put everything into arrays for consistency's sake.
            queryMap[k] = [v];
          } else {
            queryMap[k] = v;
          }
        });
        return queryMap;
      },
      // Return query portion of URL
      makeQueryString: function(queryMap) {
        var newQuery = "?" + URI().search(queryMap).query();
        if (newQuery === "?") {
          newQuery = "";
        }
        return newQuery;
      },
      // Update URL in browser
      updateQuery: function(queryMap) {
        var newQuery = this.makeQueryString(queryMap);
        this.props.updateQueryString(newQuery);
      },
      getPageNum: function() {
        var queryMap = this.makeQueryMap();
        var pageNum = 1;
        if (queryMap.page !== undefined) {
          pageNum = parseInt(queryMap.page[0]);
        }
        return pageNum;
      },
      getInitialState: function () {
        return {
          // empty resources and facetCounts to start with
          resources: [],
          facetCounts: {},
          // Controls the loader on the listing page.
          pageLoaded: false,
          allExports: this.props.allExports,
          sortingOptions: this.props.sortingOptions,
          // This should get updated after the first API call
          numPages: 0,
          // Will be set on refresh
          selectedFacets: {},
          selectedMissingFacets: {},
          // Keep track of resource id so we can lazy load panels.
          currentResourceId: undefined,
          // What panels are already loaded
          loadedPanels: {},
          isLearningResourcePanelDirty: false
        };
      },
      render: function () {
        var options = {
          repoSlug: this.props.repoSlug,
          allExports: this.state.allExports,
          sortingOptions: this.state.sortingOptions,
          loggedInUsername: this.props.loggedInUsername,
          imageDir: this.props.imageDir,
          pageSize: this.props.pageSize,
          openExportsPanel: this.openExportsPanel,
          openResourcePanel: this.openResourcePanel,
          updateFacets: this.updateFacets,
          updateMissingFacets: this.updateMissingFacets,
          selectedFacets: this.state.selectedFacets,
          selectedMissingFacets: this.state.selectedMissingFacets,
          updateSort: this.updateSort,
          pageNum: this.getPageNum(),
          numPages: this.state.numPages,
          updatePage: this.updatePage,
          loaded: this.state.pageLoaded,
          resources: this.state.resources,
          facetCounts: this.state.facetCounts,
          ref: "listingResources"
        };
        return React.DOM.div(null,
          React.createElement(ImportStatus, {
            repoSlug: this.props.repoSlug,
            refreshFromAPI: this.refreshFromAPI
          }),
          React.createElement(ListingResources.ListingPage, options)
        );
      },
      /**
       * Use by close learning resource confirmation popup.
       */
      resetAndHideLearningResourcePanel: function() {
        $('.cd-panel').removeClass('is-visible');
        this.setState({
          currentResourceId: undefined,
          isLearningResourcePanelDirty: false
        });
      },
      confirmCloseLearningResourcePanel: function(status) {
        if (status) {
          this.resetAndHideLearningResourcePanel();
        }
      },
      closeLearningResourcePanel: function() {
        if (!this.state.isLearningResourcePanelDirty) {
          this.resetAndHideLearningResourcePanel();
        } else {
          var options = {
            actionButtonName: "Close",
            actionButtonClass: "btn btn-danger btn-ok",
            title: "Confirm Exit",
            message: "Are you sure you want to close this panel?",
            description: "You have unsaved changes once you click close " +
            "all changes will be lost.",
            confirmationHandler: this.confirmCloseLearningResourcePanel
          };
          this.props.showConfirmationDialog(options);
        }
      },
      /**
       * Clears exports on page. Assumes DELETE to clear on server already
       * happened.
       */
      clearExports: function () {
        // Clear export links.
        this.setState({allExports: []});

        // TODO: we shouldn't need a ref here, state should be moved up here
        this.refs.listingResources.clearSelectedExports();
      },
      loadManageTaxonomies: function () {
        ManageTaxonomies.loader(
          this.props.repoSlug,
          $('#taxonomy-component')[0],
          this.props.showConfirmationDialog,
          showTab,
          setTabName,
          this.refreshFromAPI
        );
      },
      openExportsPanel: function (exportCount) {
        $('.cd-panel-exports').addClass('is-visible');
        Exports.loader(
          this.props.repoSlug,
          this.props.loggedInUsername,
          this.clearExports,
          $("#exports_content")[0]
        );
        Exports.loadExportsHeader(exportCount, $("#exports_heading")[0]);
      },
      getPanelLoaders: function() {
        return {
          "tab-1": this.loadResourceTab,
          "tab-2": this.loadXmlTab,
          "tab-3": this.loadStaticAssetsTab
        };
      },
      /**
       * When called, query search API using query parameters of this URL
       * and update listing with updated resources.
       *
       * @returns {jQuery.Deferred} A promise that's resolved or rejected when
       * the AJAX call completes and the rerender is triggered.
       */
      refreshFromAPI: function() {
        this.setState({pageLoaded: false});

        var queryMap = this.makeQueryMap();
        var newQuery = this.makeQueryString(queryMap);

        // Query string for repository page is the same used for the search API
        var url = "/api/v1/repositories/" +
          this.props.repoSlug + "/search/" + newQuery;

        var thiz = this;
        return $.get(url).then(function (collection) {
          thiz.setState({
            resources: collection.results,
            facetCounts: collection.facet_counts,
            selectedFacets: collection.selected_facets,
            selectedMissingFacets: collection.selected_missing_facets
          });

          var numPages = Math.ceil(collection.count / thiz.props.pageSize);
          var oldPageNum = thiz.getPageNum();
          var pageNum = oldPageNum;
          if (pageNum > numPages) {
            pageNum = numPages - 1;
            if (pageNum < 1) {
              pageNum = 1;
            }
          }
          thiz.setState({
            numPages: numPages
          });
          if (pageNum !== oldPageNum) {
            queryMap.page = pageNum;
            // Update URL string again for different pageNum
            thiz.updateQuery(queryMap);
          }
        }).fail(function (error) {
          // Propagate error
          return $.Deferred().reject(error);
        }).always(function() {
          thiz.setState({pageLoaded: true});
        });
      },
      markDirtyLearningResourcePanel: function (isDirty) {
        this.setState({isLearningResourcePanelDirty: isDirty});
      },
      loadResourceTab: function (resourceId) {
        var options = {
          "repoSlug": this.props.repoSlug,
          "learningResourceId": resourceId,
          "refreshFromAPI": this.refreshFromAPI,
          "markDirty": this.markDirtyLearningResourcePanel,
          "closeLearningResourcePanel": this.closeLearningResourcePanel
        };
        LearningResources.loader(
          options,
          $("#tab-1")[0]
        );
      },
      loadXmlTab: function (resourceId) {
        XmlPanel.loader(this.props.repoSlug, resourceId, $("#tab-2")[0]);
      },
      loadStaticAssetsTab: function (resourceId) {
        StaticAssets.loader(this.props.repoSlug, resourceId, $("#tab-3")[0]);
      },
      openResourcePanel: function (resourceId) {
        // Reset loaded panels
        var loadedPanels = {};
        this.setState({currentResourceId: resourceId});

        // Load the resource tab
        showTab("tab-1");
        this.loadResourceTab(resourceId);
        loadedPanels["tab-1"] = true;
        this.setState({loadedPanels: loadedPanels});
        $('.cd-panel').addClass('is-visible');
      },
      updateFacetParam: function (param, selected) {
        var queryMap = this.makeQueryMap();
        queryMap.page = undefined;

        if (!queryMap.selected_facets) {
          queryMap.selected_facets = [];
        }

        // Remove facet. If selected we'll add it back again with a push().
        queryMap.selected_facets = _.filter(
          queryMap.selected_facets, function (facet) {
            return facet !== param;
          }
        );

        if (selected) {
          queryMap.selected_facets = queryMap.selected_facets.concat(param);
        }

        this.updateQuery(queryMap);
        return this.refreshFromAPI();
      },
      /**
       * Update queryMap with updated facet information, then refresh from API.
       *
       * @param facetId {String} Facet key
       * @param valueId {String} Facet value
       * @param selected {bool} Value for facet checkbox
       *
       * @returns {jQuery.Deferred} Promise which is resolved or rejected after
       * refresh occurs.
       */
      updateFacets: function (facetId, valueId, selected) {
        var param = facetId + "_exact:" + valueId;

        return this.updateFacetParam(param, selected);
      },
      updateMissingFacets: function (facetId, selected) {
        var param = "_missing_:" + facetId + "_exact";

        return this.updateFacetParam(param, selected);
      },
      /**
       * Update sorting and refresh from API.
       *
       * @param value {String} Sort parameter
       * @return {jQuery.Deferred} A promise which is resolved or rejected after
       * refresh has occurred.
       */
      updateSort: function (value) {
        var queryMap = this.makeQueryMap();
        queryMap.sortby = value;

        var sortingOptions = this.state.sortingOptions;
        var allOptions = sortingOptions.all.concat([
          sortingOptions.current
        ]);
        var current = _.filter(allOptions, function (pair) {
          return pair[0] === value;
        });
        var all = _.filter(allOptions, function (pair) {
          return pair[0] !== value;
        });
        this.setState({
          sortingOptions: {
            all: all,
            current: current[0]
          }
        });

        this.updateQuery(queryMap);
        return this.refreshFromAPI();
      },
      /**
       * Update search parameter then refresh from API.
       *
       * @param search {String} The search phrase
       * @returns {jQuery.Deferred} Promise which evalutes after refresh occurs.
       */
      updateSearch: function (search) {
        var queryMap = this.makeQueryMap();
        queryMap.page = undefined;
        if (search !== '') {
          queryMap.q = [search];
        } else {
          queryMap.q = undefined;
        }

        // clear facets
        queryMap.selected_facets = undefined;

        this.updateQuery(queryMap);
        return this.refreshFromAPI();
      },
      /**
       * Update page number and refresh from API.
       * @param newPageNum {Number} New page number
       * @return {jQuery.Deferred} Promise which resolves or rejects after
       * refresh has occurred.
       */
      updatePage: function (newPageNum) {
        var queryMap = this.makeQueryMap();
        queryMap.page = [newPageNum.toString()];

        this.updateQuery(queryMap);
        return this.refreshFromAPI();
      },

      componentDidMount: function () {
        CSRF.setupCSRF();

        var thiz = this;

        $('[data-toggle=popover]').popover();
        //Close panels on escape keypress
        $(document).keyup(function (event) {
          if (event.keyCode === 27) { // escape key maps to keycode `27`
            if (!_.isUndefined(thiz.state.currentResourceId)) {
              thiz.closeLearningResourcePanel();
            }
            if ($('.cd-panel-2').hasClass('is-visible')) {
              hideTaxonomyPanel();
            }
            if ($('.cd-panel-exports').hasClass('is-visible')) {
              $('.cd-panel-exports').removeClass('is-visible');
            }
            if ($('.cd-panel-members').hasClass('is-visible')) {
              $('.cd-panel-members').removeClass('is-visible');
            }
            event.preventDefault();
          }
        });

        //close the lateral panel
        $('.cd-panel').on('click', function (event) {
          if ($(event.target).is('.cd-panel') ||
            $(event.target).is('.cd-panel-close')) {
            if (!_.isUndefined(thiz.state.currentResourceId)) {
              thiz.closeLearningResourcePanel();
            }
            event.preventDefault();
          }
        });

        //open the lateral panel
        $('.btn-taxonomies').on('click', function (event) {
          event.preventDefault();
          thiz.loadManageTaxonomies();
          $('.cd-panel-2').addClass('is-visible');
        });

        //close the lateral panel
        $('.cd-panel-2').on('click', function (event) {
          if ($(event.target).is('.cd-panel-2') ||
            $(event.target).is('.cd-panel-close')) {
            hideTaxonomyPanel();
            event.preventDefault();
          }
        });

        _.each(this.getPanelLoaders(), function (loader, tag) {
          $("a[href='#" + tag + "']").click(function () {
            // If tab not already loaded, load it now
            if (!thiz.state.loadedPanels[tag]) {
              loader(thiz.state.currentResourceId);
              var loadedPanels = $.extend({}, thiz.state.loadedPanels);
              loadedPanels[tag] = true;
              thiz.setState({
                loadedPanels: loadedPanels
              });
            }
          });
        });

        // If search is executed update query parameter and refresh from API.
        $("#search_button").click(function (e) {
          e.preventDefault();

          var search = $("#id_q").val();
          thiz.updateSearch(search);
        });

        // Close exports panel.
        $('.cd-panel-exports').on('click', function (event) {
          if ($(event.target).is('.cd-panel-exports') ||
            $(event.target).is('.cd-panel-close')) {
            $('.cd-panel-exports').removeClass('is-visible');
            event.preventDefault();
          }
        });

        //open the lateral panel for members
        $('.btn-members').on('click', function (event) {
          event.preventDefault();
          //remove any alert
          $('#members-alert').empty();
          //reset the form values
          resetUserGroupForm();
          //make panel visible
          $('.cd-panel-members').addClass('is-visible');
          //retrieve all the members
          showUpdateAllMembers();
        });

        //close the lateral panel for members
        $('.cd-panel-members').on('click', function (event) {
          if ($(event.target).is('.cd-panel-members') ||
            $(event.target).is('.cd-panel-close')) {
            $('.cd-panel-members').removeClass('is-visible');
            event.preventDefault();
          }
        });

        //add button for the members
        $(document).on('click', '.cd-panel-members-add', function () {
          var url = $('.cd-panel-members').data('members-url');
          var username = $('input[name=\'members-username\']').val();
          var groupType = $('select[name=\'members-group_type\']').val();
          // /api/v1/repositories/my-rep/members/groups/<group_type>/users/
          url += 'groups/' + groupType + '/users/';
          //test that username is not an email
          if (isEmail(username)) {
            var message = 'Please type only your username before the @';
            showMembersAlert(message, 'warning');
            return;
          }
          var email = username + EMAIL_EXTENSION;
          if (!isEmail(email)) {
            var emailMessage = '<strong>' + email +
              '</strong> does not seem to be a valid email';
            showMembersAlert(emailMessage, 'danger');
            return;
          }
          $.ajax({
            url: url,
            type: 'POST',
            data: {username: username}
          })
            .then(function () {
              //retrieve the members lists
              return showUpdateAllMembers();
            })
            .then(function () {
              //reset the values
              resetUserGroupForm();
              //show alert
              var message = '<strong>' + email +
                '</strong> added to group <strong>' +
                formatGroupName(groupType) + '</strong>';
              showMembersAlert(message);
            })
            .fail(function (data) {
              //show alert
              var message = 'Error adding user ' + email +
                ' to group ' + formatGroupName(groupType);
              if (data && data.responseJSON && data.responseJSON.username) {
                message = message + '<br>' + data.responseJSON.username[0];
              }
              showMembersAlert(message, 'danger');
            });
        });

        //remove button for the members
        $(document).on('click', '.cd-panel-members-remove', function () {
          var url = $('.cd-panel-members').data('members-url');
          var username = $(this).data('username');
          var groupType = $(this).data('group_type');
          var email = username + EMAIL_EXTENSION;
          // /api/v1/repositories/my-rep/members/groups/<group_type>/users/<username>/
          url += 'groups/' + groupType + '/users/' + username + '/';
          $.ajax({
            url: url,
            type: 'DELETE'
          })
            .then(function () {
              //retrieve the members lists
              return showUpdateAllMembers();
            })
            .then(function () {
              //show alert
              var message = '<strong>' + email +
                '</strong> deleted from group <strong>' +
                formatGroupName(groupType) + '</strong>';
              showMembersAlert(message);
            })
            .fail(function (data) {
              //show alert
              var message = 'Error deleting user <strong>' +
                email + '</strong> from group <strong>' +
                formatGroupName(groupType) + '</strong>';
              if (data && data.responseJSON && data.responseJSON.detail) {
                message += '<br>' + data.responseJSON.detail;
              }
              showMembersAlert(message, 'danger');
            });
        });

        // Initial refresh to populate page.
        thiz.refreshFromAPI();
      }
    });

    var updateQueryString = function(newQuery) {
      if (newQuery.length === 0) {
        History.replaceState(null, document.title, ".");
      } else {
        History.replaceState(null, document.title, newQuery);
      }
    };

    var getQueryString = function() {
      return URI(window.location).search();
    };

    var loader = function (listingOptions, container) {
      var options = {
        allExports: listingOptions.allExports,
        sortingOptions: listingOptions.sortingOptions,
        imageDir: listingOptions.imageDir,
        pageSize: listingOptions.pageSize,
        repoSlug: listingOptions.repoSlug,
        loggedInUsername: listingOptions.loggedInUsername,
        updateQueryString: updateQueryString,
        getQueryString: getQueryString,
        showConfirmationDialog: showConfirmationDialog

      };

      React.render(
        React.createElement(ListingContainer, options),
        container
      );
    };

    return {
      ListingContainer: ListingContainer,
      isEmail: isEmail,
      formatGroupName: formatGroupName,
      loader: loader
    };
  });
