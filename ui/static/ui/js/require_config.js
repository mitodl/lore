// relative to ui/static/bower
/* jshint ignore:start */
var REQUIRE_PATHS = {
  jquery: "jquery/dist/jquery.min",
  bootstrap: "bootstrap/dist/js/bootstrap.min",
  icheck: "icheck/icheck.min",
  retina: "retina.js/dist/retina.min",
  React: "react/react-with-addons.min",
  react_infinite: "react-infinite/dist/react-infinite.min",
  react_datagrid: "../lib/js/react-datagrid.min",
  lodash: "lodash/lodash.min",
  select2: "select2/dist/js/select2.full.min",
  uri: "uri.js/src/URI",
  punycode: "uri.js/src/punycode",
  IPv6: "uri.js/src/IPv6",
  SecondLevelDomains: "uri.js/src/SecondLevelDomains",
  history: "history.js/scripts/compressed/history",
  historyadapter: "history.js/scripts/compressed/history.adapter.jquery",
  csrf: "../ui/js/csrf",
  listing: "../ui/js/listing",
  manage_taxonomies: "../ui/js/manage_taxonomies.jsx?noext",
  learning_resources: "../ui/js/learning_resources.jsx?noext",
  listing_resources: "../ui/js/listing_resources.jsx?noext",
  static_assets: "../ui/js/static_assets.jsx?noext",
  lr_exports: "../ui/js/lr_exports.jsx?noext",
  pagination: "../ui/js/pagination.jsx?noext",
  utils: "../ui/js/utils.jsx?noext",
};
var SHIMS = {
  "icheck": {"deps": ["jquery"]},
  "bootstrap": {"deps": ["jquery"]},
  "react_infinite": {"deps": ["react"]},
  "historyadapter": {"deps": ["jquery"]},
  "history": {"deps": ["historyadapter"], "exports": "History"}
};
define("react", ["React"], function(React) {
  // Workaround for react_datagrid referring to "React"
  return React;
});
/* jshint ignore:end */
