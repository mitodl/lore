define(['jquery'], function(jQuery) {
  'use strict';

  jQuery(document).ready(function($) {

    // Setup CSRF cookie handling so we can communicate with API
    // This code is pulled from
    // https://docs.djangoproject.com/en/dev/ref/csrf/#ajax
    var getCookie = function(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
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
