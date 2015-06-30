define(
  ['jquery', 'setup_manage_taxonomies', 'bootstrap', 'icheck', 'csrf'],
  function(jQuery, setupManageTaxonomies) {
    'use strict';

    jQuery(document).ready(function($) {
      $('input.icheck-11').iCheck({
        checkboxClass: 'icheckbox_square-blue',
        radioClass: 'iradio_square-blue'
      });
      $('[data-toggle=popover]').popover();

      //open the lateral panel
      $('.cd-btn').on('click', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        var title = $(this).html();
        var textarea = $('.cd-panel .textarea-xml');
        $('.cd-panel header h1').html(title);

        // Clear out text area while waiting for AJAX to return
        textarea.val('');
        $.ajax({url: url, dataType: 'text'}).done(function(data) {
          $('.cd-panel .textarea-xml').val(data);
        }).error(function() {
          $('.cd-panel .textarea-xml').val('Unable to retrieve XML.');
        });
        $('.cd-panel').addClass('is-visible');
      });

      // Handle "Copy to Clipboard"
      $('.cd-panel #copy-textarea-xml').on('click', function(event) {
        event.preventDefault();
        $('.cd-panel .textarea-xml').select();
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

      var repoSlug = $("#repo_slug").val();
      setupManageTaxonomies(repoSlug);
    });
  });
