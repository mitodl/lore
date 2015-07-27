define('listing',
  ['jquery', 'lodash', 'setup_manage_taxonomies', 'facets',
    'learning_resources', 'static_assets', 'utils',
    'lr_exports', 'bootstrap', 'icheck', 'csrf'],
  function($, _, setupManageTaxonomies, facets, LearningResources, StaticAssets,
  Utils, Exports) {
    'use strict';
    facets.setupFacets(window);
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
        .done(function(results) {
          formatUserGroups(results, '#cd-panel-members-list');
        })
        .fail(function() {
          var message = 'Unable to retrieve list of members.';
          showMembersAlert(message, 'danger');
        });
    }

    $(document).ready(function() {

      $('[data-toggle=popover]').popover();

      //open the lateral panel
      $('.cd-btn').on('click', function(event) {
        event.preventDefault();
        var learningResourceId = $(event.target).attr(
          "data-learningresource-id");
        LearningResources.loader(repoSlug, learningResourceId, $("#tab-1")[0]);
        $('.cd-panel').addClass('is-visible');
        StaticAssets.loader(repoSlug, learningResourceId, $("#tab-3")[0]);
      });

      //close the lateral panel
      $('.cd-panel').on('click', function(event) {
        if ($(event.target).is('.cd-panel') ||
            $(event.target).is('.cd-panel-close')) {
          $('.cd-panel').removeClass('is-visible');
          event.preventDefault();
        }
      });

      //open the lateral panel
      $('.btn-taxonomies').on('click', function(event) {
        event.preventDefault();
        $('.cd-panel-2').addClass('is-visible');
      });

      //close the lateral panel
      $('.cd-panel-2').on('click', function(event) {
        if ($(event.target).is('.cd-panel-2') ||
            $(event.target).is('.cd-panel-close')) {
          $('.cd-panel-2').removeClass('is-visible');
          event.preventDefault();
        }
      });

      // Open exports panel.
      var loggedInUsername = $("#export_button").data("logged-in-user");

      $('#export_button').on('click', function(event) {
        event.preventDefault();
        $('.cd-panel-exports').addClass('is-visible');
        Exports.loader(repoSlug, loggedInUsername, $("#exports_content")[0]);
      });

      // Close exports panel.
      $('.cd-panel-exports').on('click', function(event) {
        if ($(event.target).is('.cd-panel-exports') ||
            $(event.target).is('.cd-panel-close')) {
          $('.cd-panel-exports').removeClass('is-visible');
          event.preventDefault();
        }
      });

      //open the lateral panel for members
      $('.btn-members').on('click', function(event) {
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
      $('.cd-panel-members').on('click', function(event) {
        if ($(event.target).is('.cd-panel-members') ||
            $(event.target).is('.cd-panel-close')) {
          $('.cd-panel-members').removeClass('is-visible');
          event.preventDefault();
        }
      });
      //add button for the members
      $(document).on('click', '.cd-panel-members-add', function() {
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
        .done(function() {
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
        .fail(function(data) {
          //show alert
          var message = 'Error adding user ' + email +
            ' to group ' + formatGroupName(groupType);
          message = message + '<br>' + data.responseJSON.username[0];
          showMembersAlert(message, 'danger');
        });
      });
      //remove button for the members
      $(document).on('click', '.cd-panel-members-remove', function() {
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
        .done(function() {
          //show alert
          var message = '<strong>' + email +
            '</strong> deleted from group <strong>' +
            formatGroupName(groupType) + '</strong>';
          showMembersAlert(message);
          //retrieve the members lists
          showUpdateAllMembers();
        })
        .fail(function(data) {
          //show alert
          var message = 'Error deleting user <strong>' +
          email + '</strong> from group <strong>' +
            formatGroupName(groupType) + '</strong>';
          try {
            message += '<br>' + data.responseJSON.detail;
          }
          catch (err) {}
          showMembersAlert(message, 'danger');
        });
      });

      var updateCheckDisplay = function(node) {
        if ($(node).data("selected")) {
          $(node).find("i").attr("class", "fa fa-check");
        } else {
          $(node).find("i").attr("class", "fa fa-arrow-right");
        }
      };

      /**
       * Update export count badge.
       *
       * @param {number} direction Add this value to
       * the existing count before rendering.
       */
      var updateExportCount = function(direction) {
        var oldCount = $("#export_button").data("export-count");
        var newCount = oldCount + direction;

        $("#export_button .badge").remove();
        if (newCount > 0) {
          var $badge = $("<span class='badge' />");
          $badge.append(_.escape(newCount));
          $("#export_button").append($badge);
        }
        $("#export_button").data("export-count", newCount);
      };
      _.each($(".link-export"), function(node) {
        updateCheckDisplay(node);
      });
      updateExportCount(0);

      // Set up click handlers for export links.
      $(".link-export").click(function(event) {
        event.preventDefault();
        var node = this;
        var $node = $(node);

        var learningResourceId = $node.data("learningresource-id");
        var selected = $node.data("selected") === true;
        if (selected) {
          // Remove an item from export cart.
          $.ajax({
            type: "DELETE",
            url: "/api/v1/repositories/" + repoSlug +
            "/learning_resource_exports/" + loggedInUsername + "/" +
            learningResourceId + "/"
          }).then(function() {
            updateExportCount(-1);
            $node.data("selected", false);
            updateCheckDisplay(node);
          });
        } else {
          // Add an item to export cart.
          $.post("/api/v1/repositories/" + repoSlug +
            "/learning_resource_exports/" + loggedInUsername + "/", {
            id: learningResourceId
          }).then(function () {
            updateExportCount(1);
            $node.data("selected", true);
            updateCheckDisplay(node);
          });
        }
      });

      var repoSlug = $("#repo_slug").val();
      setupManageTaxonomies.loader(repoSlug);
    });
  });
