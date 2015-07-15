#!/usr/bin/env node
/**
 * Convert lcov input to coveralls JSON output
 *
 * Based off of node_modules/coveralls/bin/coveralls.js but this doesn't
 * upload to Coveralls since we need to merge Python input beforehand.
 */
var coveralls = require('coveralls');
var fs = require('fs');

var inputFile = process.argv[2];
var outputFile = process.argv[3];

fs.readFile(inputFile, {encoding: 'utf-8'}, function(err, input) {
  'use strict';

  if (err) {
    throw err;
  }

  // treat paths as absolute
  var options = {filepath: ''};

  coveralls.convertLcovToCoveralls(input, options, function(err, data) {
    if (err) {
      throw err;
    }

    fs.writeFile(outputFile, JSON.stringify(data), function(err) {
      if (err) {
        throw err;
      }
    });
  });
});
