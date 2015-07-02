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
for (var key in REQUIRE_PATHS) {
  if (REQUIRE_PATHS.hasOwnProperty(key)) {
    paths[key] = 'ui/static/bower/' + REQUIRE_PATHS[key];
  }
}
paths.QUnit = 'node_modules/qunitjs/qunit/qunit';

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
