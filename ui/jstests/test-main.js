var allTestFiles = [];
var TEST_REGEXP = /(spec|test)\.js$/i;

Object.keys(window.__karma__.files).forEach(function(file) {
  'use strict';
  if (TEST_REGEXP.test(file)) {
    // Normalize paths to RequireJS module names.
    allTestFiles.push(file);
  }
});

require.config({
  // Karma serves files under /base, which is the basePath from your config file
  baseUrl: '/base/',

  // dynamically load all test files
  deps: allTestFiles,

  // paths for required libraries
  paths: {
    QUnit: 'node_modules/qunitjs/qunit/qunit'
  },

  // we have to kickoff karma, as it is asynchronous
  callback: window.__karma__.start
});
