// Karma configuration
// Generated on Mon Jun 22 2015 16:55:41 GMT-0400 (EDT)

module.exports = function(config) {
  'use strict';

  config.set({
    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',

    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    // phantom-js doesn't support function.bind in 1.x so we need the shim
    frameworks: ['phantomjs-shim', 'requirejs', 'qunit'],

    // list of files / patterns to load in the browser
    files: [
      'ui/static/ui/js/require_config.js',
      'ui/jstests/test-main.js',
      {
        pattern: 'ui/static/bower/**/*.js',
        included: false
      },
      {
        pattern: 'ui/static/bower/**/*.jsx',
        included: false
      },
      {
        pattern: 'ui/static/ui/**/*.js',
        included: false
      },
      {
        pattern: 'ui/static/ui/**/*.jsx',
        included: false
      },
      {
        pattern: 'ui/jstests/**/*.js',
        included: false
      },
      {
        pattern: 'ui/jstests/**/*.jsx',
        included: false
      },
      {
        pattern: 'node_modules/jquery-mockjax/src/jquery.mockjax.js',
        included: false
      },
      {
        pattern: 'node_modules/stacktrace-js/stacktrace.js',
        included: false
      },
    ],

    // list of files to exclude from coverage and testing
    exclude: [
      "ui/static/ui/js/listing.js",
      "ui/static/ui/js/csrf.js"
    ],

    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
      'ui/static/ui/**/*.jsx': ['react', 'coverage'],
      'ui/jstests/**/*.jsx': ['react', 'coverage'],
      'ui/static/ui/**/*.js': ['coverage'],
      'ui/jstests/**/*.js': ['coverage']
    },

    reactPreprocessor: {
      transformPath: function(path) {
        // need to override this since the default behavior is jsx -> js
        return path;
      }
    },

    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress', 'coverage', 'html'],

    coverageReporter: {
      dir: 'coverage/',
      reporters: [
        {
          type: 'lcov',
          subdir: '.',
        },
        {
          type: 'lcovonly',
          subdir: '.',
          file: 'coverage-js.lcov'
        },
        {
          type: 'text-summary',
          subdir: '.',
          file: 'text-summary.txt'
        }
      ]
    },

    htmlReporter: {
      outputFile: 'jstest_results.html'
    },

    // web server port
    port: 9876,

    // enable / disable colors in the output (reporters and logs)
    colors: true,

    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,

    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: false,

    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['PhantomJS'],

    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: true
  });
};
