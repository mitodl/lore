/* global SHIMS */
/* global REQUIRE_PATHS */
var allFiles = [];
var TEST_EXCLUDE_REGEXP = /(ui\/static\/bower\/)|(node_modules)|(test-main.js)|(require_config.js)/i;
var JS_INCLUDE_REGEXP = /\.jsx?$/i;

Object.keys(window.__karma__.files).forEach(function(file) {
  'use strict';
  if (JS_INCLUDE_REGEXP.test(file) && !TEST_EXCLUDE_REGEXP.test(file)) {
    // Normalize paths to RequireJS module names.
    allFiles.push(file);
  }
});

var paths = {};
for (var requireKey in REQUIRE_PATHS) {
  if (REQUIRE_PATHS.hasOwnProperty(requireKey)) {
    paths[requireKey] = 'ui/static/bower/' + REQUIRE_PATHS[requireKey];
  }
}

// relative to project root
var TESTING_PATHS = {
  QUnit: 'node_modules/qunitjs/qunit/qunit',
  jquery_mockjax: 'node_modules/jquery-mockjax/src/jquery.mockjax',
  test_utils: 'ui/jstests/test-utils.jsx?noext',
  stacktrace: 'node_modules/stacktrace-js/stacktrace',
};
for (var testingKey in TESTING_PATHS) {
  if (TESTING_PATHS.hasOwnProperty(testingKey)) {
    paths[testingKey] = TESTING_PATHS[testingKey];
  }
}

require.config({
  // Karma serves files under /base, which is the basePath from your config file
  baseUrl: '/base/',

  // dynamically load all files
  deps: allFiles,

  // Load up shims
  shim: SHIMS,

  // paths for required libraries
  paths: paths,

  // we have to kickoff karma, as it is asynchronous
  callback: window.__karma__.start
});
