define(['jquery', 'bootstrap', 'icheck'], function(jQuery) {
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

    // Setup CSRF cookie handling so we can communicate with API
    // This code is pulled from
    // https://docs.djangoproject.com/en/dev/ref/csrf/#ajax
    var getCookie = function (name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    };
    var csrfSafeMethod = function(method) {
      // these HTTP methods do not require CSRF protection
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    };

    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        }
      }
    });
  });
});
