define("test_utils", ["jquery", "stacktrace", "lodash", "QUnit",
  "jquery_mockjax"], function($, printStackTrace, _, QUnit) {
  'use strict';

  QUnit.config.testTimeout = 5000;

  /**
   * Number of AJAX calls intercepted by mockjax
   * @type {object}
   */
  var mockjaxCount = 0;

  /**
   * Pool of ajax requests
   * @type {Array}
   */
  var requestPool = [];

  /**
   * Map of mockjax url and type to mockjax id
   * @type {{}}
   */
  var mockjaxIdLookup = {};

  /**
   * Wait for expectedCount AJAX calls then execute callable.
   *
   * @param {number} expectedCount Wait for this many AJAX calls
   * @param {function} callable Execute this function after this many AJAX calls
   * @param {*} [stacktrace] If specified, the stacktrace of the original caller
   */
  var waitForAjax = function (expectedCount, callable, stacktrace) {
    if (stacktrace === undefined) {
      // start at 0 calls
      mockjaxCount = 0;
      // setTimeout will have its own stack trace, so preserve this one
      // so we can know where the error occurred
      stacktrace = printStackTrace().join("\n");
    }

    if (mockjaxCount < expectedCount) {
      setTimeout(function () {
        waitForAjax(expectedCount, callable, stacktrace);
      }, 100);
    } else if (mockjaxCount === expectedCount) {
      callable();
    } else {
      throw "Expected " + expectedCount +
        " AJAX requests but got " + mockjaxCount + " instead: " + stacktrace;
    }
  };

  var makeKeyFromSettings = function(settings) {
    if (settings.url === undefined) {
      throw "Expected url key in settings";
    }
    var type = settings.type;
    if (type === undefined) {
      type = "GET";
    } else {
      type = type.toUpperCase();
    }

    return JSON.stringify({url: settings.url, type: type});
  };

  var replaceMockjax = function (settings) {
    var key = makeKeyFromSettings(settings);
    var id = mockjaxIdLookup[key];
    if (id === undefined) {
      throw "Unable to find mocked url given key " + key;
    }

    $.mockjax.clear(id);
    return initMockjax(settings, true);
  };

  var initMockjax = function (settings, allowReplace) {
    var newSettings = $.extend({}, settings);
    newSettings.onAfterComplete = function () {
      mockjaxCount++;
    };
    var id = $.mockjax(newSettings);
    var key = makeKeyFromSettings(settings);

    if (!allowReplace) {
      if (_.has(mockjaxIdLookup, key)) {
        throw "Mockjax key " + key + " already exists";
      }
    }
    mockjaxIdLookup[key] = id;
    return id;
  };

  return {
    /**
     * Any cross-test cleanup
     */
    cleanup: function() {
      $.mockjax.clear();
      mockjaxCount = 0;

      _.each(requestPool, function(jqXHR) {
        jqXHR.abort();
      });
      requestPool = [];
    },
    /**
     * Setup mockjax settings
     */
    setup: function() {
      $.mockjax.clear();
      $.mockjaxSettings.responseTime = 20;

      // by default logs every URL which gets verbose
      $.mockjaxSettings.logging = false;

      // in case a test failed and we didn't get to cleanup
      mockjaxIdLookup = {};

      requestPool = [];
      $.ajaxSetup({
        beforeSend: function(jqXHR) {
          requestPool.push(jqXHR);
        },
        complete: function(jqXHR) {
          var i = requestPool.indexOf(jqXHR);
          if (i > -1) {
            requestPool.splice(i, 1);
          }
        }
      });
    },
    initMockjax: initMockjax,
    replaceMockjax: replaceMockjax,
    waitForAjax: waitForAjax
  };
});
