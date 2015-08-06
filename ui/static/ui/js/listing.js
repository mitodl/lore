define('listing',
  ['jquery', 'lodash', 'manage_taxonomies', 'facets',
    'learning_resources', 'static_assets', 'utils',
    'lr_exports', 'listing_resources', 'bootstrap', 'icheck', 'csrf'],
  function ($, _, ManageTaxonomies, Facets, LearningResources, StaticAssets,
            Utils, Exports, ListingResources) {
    'use strict';

    var loader = function (listingOptions, container) {
      var repoSlug = listingOptions.repoSlug;
      var loggedInUsername = listingOptions.loggedInUsername;

      Facets.setupFacets(window);
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
        $('#cd-panel-members-list').empty();
        Utils.getCollection(url)
          .done(function (results) {
            formatUserGroups(results, '#cd-panel-members-list');
          })
          .fail(function () {
            var message = 'Unable to retrieve list of members.';
            showMembersAlert(message, 'danger');
          });
      }

      /**
       * Change page number in edit mode. Navigate to new page of it is valid
       *
       * @param {Number} pageNum - current page number
       * @param {Number} maxPages - total number of pages
       * @param {JQuery} callerElem - Reference to pagination status link
       */
      function navigateToPage(pageNum, maxPages, callerElem) {
        var replaceWith = $(
          '<input name="search_temp" type="number" ' +
            'value="' + pageNum + '" size="10" ' +
          'class="form-control repo-page-status"/>'
        );
        var callerSelector = $(callerElem);

        callerSelector.hide();
        callerSelector.after(replaceWith);
        replaceWith.focus();
        $(replaceWith).focusout(function() {
          processPage(
              pageNum,
              maxPages,
              replaceWith,
              callerSelector
            );
        });
        $(replaceWith).keypress(function(e) {
          var key = e.which;
          // the enter key code
          if (key === 13) {
            e.preventDefault();
            processPage(
              pageNum,
              maxPages,
              replaceWith,
              callerSelector
            );
          }
        });
      }

      /**
       * If page number is change and it is valid then navigate user to new page
       *
       * @param {Number} pageNum - current page number
       * @param {Number} maxPages - total number of pages
       * @param {JQuery} replaceWith - text field selector
       * @param {JQuery} callerSelector - pagination status selector
       */
      function processPage(pageNum, maxPages, replaceWith, callerSelector) {
        var newPageNum = replaceWith.val();
        replaceWith.remove();
        if (newPageNum !== pageNum &&
          newPageNum > 0 &&
          newPageNum <= maxPages) {
          var href = $(location).attr('href');
          var url;
          if (href.toLowerCase().indexOf("page=") >= 0) {
            url = href.replace(
              "page=" + pageNum,
              "page=" + newPageNum
            );
          } else {
            if (href[href.length - 1] === "/") {
              url = href + "?page=" + newPageNum;
            } else {
              url = href + "&page=" + newPageNum;
            }
          }
          $(location).attr(
            'href',
            url
          );
        }
        callerSelector.show();
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

      // Need to declare this above assignment due to circular dependencies.
      var listingResources;

      /**
       * Clears exports on page. Assumes DELETE to clear on server already
       * happened.
       */
      var clearExports = function () {
        // Clear export links.
        listingResources.setState({exports: []});
      };

      var openExportsPanel = function() {
        $('.cd-panel-exports').addClass('is-visible');
        Exports.loader(repoSlug, loggedInUsername, clearExports,
          $("#exports_content")[0]);
      };

      var openResourcePanel = function(resourceId) {
        LearningResources.loader(
          repoSlug, resourceId, $("#tab-1")[0]);
        $('.cd-panel').addClass('is-visible');
        StaticAssets.loader(
          repoSlug, resourceId, $("#tab-3")[0]);
      };

      // Listing resources React object. We need this variable to allow
      // clearExports to tell it to clear exports.
      listingResources = ListingResources.loader(listingOptions,
        container, openExportsPanel, openResourcePanel);

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
          .done(function () {
            //reset the values
            resetUserGroupForm();
            //show alert
            var message = '<strong>' + email +
              '</strong> added to group <strong>' +
              formatGroupName(groupType) + '</strong>';
            showMembersAlert(message);
            //retrieve the members lists
            showUpdateAllMembers();
          })
          .fail(function (data) {
            //show alert
            var message = 'Error adding user ' + email +
              ' to group ' + formatGroupName(groupType);
            message = message + '<br>' + data.responseJSON.username[0];
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
          .done(function () {
            //show alert
            var message = '<strong>' + email +
              '</strong> deleted from group <strong>' +
              formatGroupName(groupType) + '</strong>';
            showMembersAlert(message);
            //retrieve the members lists
            showUpdateAllMembers();
          })
          .fail(function (data) {
            //show alert
            var message = 'Error deleting user <strong>' +
              email + '</strong> from group <strong>' +
              formatGroupName(groupType) + '</strong>';
            try {
              message += '<br>' + data.responseJSON.detail;
            }
            catch (err) {
            }
            showMembersAlert(message, 'danger');
          });

        $("a#repo_page_status").click(function() {
          var pageNum = $(this).data('page-num');
          var maxPages = $(this).data('max-page-num');
          navigateToPage(pageNum, maxPages, this);
        });
      });

      ManageTaxonomies.loader(repoSlug, $('#taxonomy-component')[0]);
    };

    return {
      loader: loader
    };
  });
