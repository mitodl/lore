define('listing',
  ['csrf', 'jquery', 'lodash', 'uri', 'history', 'manage_taxonomies',
    'learning_resources', 'static_assets', 'utils',
    'lr_exports', 'listing_resources', 'pagination',
    'bootstrap', 'icheck'],
  function (CSRF, $, _, URI, History,
            ManageTaxonomies, LearningResources, StaticAssets,
            Utils, Exports, ListingResources, Pagination) {
    'use strict';

    var loader = function (listingOptions, container) {
      var repoSlug = listingOptions.repoSlug;
      var loggedInUsername = listingOptions.loggedInUsername;

      CSRF.setupCSRF();

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

      $('[data-toggle=popover]').popover();
      //Close panels on escape keypress
      $(document).keyup(function(event) {
        if (event.keyCode === 27) { // escape key maps to keycode `27`
          if ($('.cd-panel').hasClass('is-visible')) {
            $('.cd-panel').removeClass('is-visible');
          }
          if ($('.cd-panel-2').hasClass('is-visible')) {
            $('.cd-panel-2').removeClass('is-visible');
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
          $('.cd-panel').removeClass('is-visible');
          event.preventDefault();
        }
      });

      //open the lateral panel
      $('.btn-taxonomies').on('click', function (event) {
        event.preventDefault();
        $('.cd-panel-2').addClass('is-visible');
      });

      //close the lateral panel
      $('.cd-panel-2').on('click', function (event) {
        if ($(event.target).is('.cd-panel-2') ||
          $(event.target).is('.cd-panel-close')) {
          $('.cd-panel-2').removeClass('is-visible');
          event.preventDefault();
        }
      });

      /**
       * Render resource items in the UI
       *
       * @returns {ReactElement} The rendered resource items
       */
      var renderListingResources;
      /**
       * Render pagination in the UI
       *
       * @returns {ReactElement} The rendered pagination
       */
      var renderPagination;

      // queryMap is the canonical place to manage query parameters for the UI.
      // The URL in the browser will be updated with these changes in
      // refreshFromAPI.
      var queryMap = {};
      // Populate queryMap with query string key value pairs.
      _.each(URI(window.location).query(true), function(v, k) {
        if (!Array.isArray(v)) {
          // URI().query(true) will put two or more values with the same
          // key in an array and not use an array for single values.
          // Put everything into arrays for consistency's sake.
          queryMap[k] = [v];
        } else {
          queryMap[k] = v;
        }
      });

      // This should get updated after the first API call
      var numPages = 0;
      var pageNum = 1;
      if (queryMap.page !== undefined) {
        pageNum = queryMap.page[0];
      }

      /**
       * Clears exports on page. Assumes DELETE to clear on server already
       * happened.
       */
      var clearExports = function () {
        // Clear export links.
        listingOptions = $.extend({}, listingOptions);
        listingOptions.allExports = [];

        var listingResources = renderListingResources();
        listingResources.clearSelectedExports();
      };

      var openExportsPanel = function(exportCount) {
        $('.cd-panel-exports').addClass('is-visible');
        Exports.loader(repoSlug, loggedInUsername, clearExports,
          $("#exports_content")[0]);
        Exports.loadExportsHeader(exportCount, $("#exports_heading")[0]);
      };

      /**
       * When called, query search API using query parameters of this URL
       * and update listing with updated resources.
       *
       * @returns {jQuery.Deferred} A promise that's resolved or rejected when
       * the AJAX call completes and the rerender is triggered.
       */
      var refreshFromAPI;

      // Will be set in refreshFromAPI
      var selectedFacets;
      var selectedMissingFacets;

      var openResourcePanel = function(resourceId) {
        LearningResources.loader(
          repoSlug, resourceId, refreshFromAPI, $("#tab-1")[0]);
        $('.cd-panel').addClass('is-visible');
        StaticAssets.loader(
          repoSlug, resourceId, $("#tab-3")[0]);
      };

      refreshFromAPI = function() {
        var newQuery = "?" + URI().search(queryMap).query();
        History.replaceState(null, document.title, newQuery);

        var url = "/api/v1/repositories/" +
          listingOptions.repoSlug + "/search/" + newQuery;

        var setOpacity = function(opacity) {
          $("#listing").css({opacity: opacity});
        };

        setOpacity(0.6);
        return $.get(url).then(function(collection) {
          listingOptions = $.extend({}, listingOptions);
          listingOptions.resources = collection.results;
          listingOptions.facetCounts = collection.facet_counts;
          selectedFacets = collection.selected_facets;
          selectedMissingFacets = collection.selected_missing_facets;

          numPages = Math.ceil(collection.count / listingOptions.pageSize);
          if (pageNum > numPages) {
            pageNum = numPages - 1;
            if (pageNum < 1) {
              pageNum = 1;
            }
          }

          renderListingResources();
          renderPagination();

          setOpacity(1);
        }).fail(function(error) {
          setOpacity(1);

          // Propagate error
          return $.Deferred().reject(error);
        });
      };

      var updateFacetParam = function(param, selected) {
        queryMap = $.extend({}, queryMap);
        queryMap.page = undefined;

        if (!queryMap.selected_facets) {
          queryMap.selected_facets = [];
        }

        // Remove facet. If selected we'll add it back again with a push().
        queryMap.selected_facets = _.filter(
          queryMap.selected_facets, function(facet) {
            return facet !== param;
          }
        );

        if (selected) {
          queryMap.selected_facets.push(param);
        }

        return refreshFromAPI();
      };

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
      var updateFacets = function(facetId, valueId, selected) {
        var param = facetId + "_exact:" + valueId;

        return updateFacetParam(param, selected);
      };

      var updateMissingFacets = function(facetId, selected) {
        var param = "_missing_:" + facetId + "_exact";

        return updateFacetParam(param, selected);
      };

      /**
       * Update sorting and refresh from API.
       *
       * @param value {String} Sort parameter
       * @return {jQuery.Deferred} A promise which is resolved or rejected after
       * refresh has occurred.
       */
      var updateSort = function(value) {
        queryMap = $.extend({}, queryMap);
        queryMap.sortby = value;

        listingOptions = $.extend({}, listingOptions);
        var allOptions = listingOptions.sortingOptions.all.concat([
          listingOptions.sortingOptions.current
        ]);
        var current = _.filter(allOptions, function(pair) {
          return pair[0] === value;
        });
        var all = _.filter(allOptions, function(pair) {
          return pair[0] !== value;
        });
        listingOptions.sortingOptions.all = all;
        listingOptions.sortingOptions.current = current[0];

        refreshFromAPI();
      };

      /**
       * Rerender listing resources
       * @returns {ReactComponent}
       */
      renderListingResources = function() {
        return ListingResources.loader(listingOptions,
        container, openExportsPanel, openResourcePanel,
        updateFacets, updateMissingFacets,
          selectedFacets, selectedMissingFacets, updateSort);
      };

      /**
       * Update search parameter then refresh from API.
       *
       * @param search {String} The search phrase
       * @returns {jQuery.Deferred} Promise which evalutes after refresh occurs.
       */
      var updateSearch = function (search) {
        queryMap.page = undefined;
        if (search !== '') {
          queryMap.q = [search];
        } else {
          queryMap.q = undefined;
        }

        // clear facets
        queryMap.selected_facets = undefined;

        return refreshFromAPI();
      };

      // If search is executed update query parameter and refresh from API.
      $("#search_button").click(function(e) {
        e.preventDefault();

        var search = $("#id_q").val();
        updateSearch(search);
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
        //
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
        .then(function() {
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
        .then(function() {
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

      /**
       * Update page number and refresh from API.
       * @param newPageNum {Number} New page number
       * @return {jQuery.Deferred} Promise which resolves or rejects after
       * refresh has occurred.
       */
      var updatePage = function(newPageNum) {
        queryMap.page = [newPageNum.toString()];
        pageNum = newPageNum;

        return refreshFromAPI();
      };

      renderPagination = function() {
        return Pagination.loader(
          pageNum, numPages, updatePage, $("#lore-pagination")[0]);
      };

      var showConfirmationDialog = function(options) {
        var container = $("#confirmation-container")[0];
        Utils.showConfirmationDialog(
          options,
          container
        );
      };

      // Initial refresh to populate page.
      refreshFromAPI();
      ManageTaxonomies.loader(
        repoSlug,
        refreshFromAPI,
        showConfirmationDialog,
        $('#taxonomy-component')[0]);
    };

    return {
      loader: loader
    };
  });
