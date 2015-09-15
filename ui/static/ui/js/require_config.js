// relative to ui/static/bower
/* jshint ignore:start */
var REQUIRE_PATHS = {
  jquery: "jquery/dist/jquery",
  bootstrap: "bootstrap/dist/js/bootstrap",
  icheck: "icheck/icheck",
  retina: "retina.js/dist/retina",
  react: "react/react-with-addons",
  react_infinite: "react-infinite/dist/react-infinite",
  lodash: "lodash/lodash",
  select2: "select2/dist/js/select2.full",
  uri: "uri.js/src/URI",
  punycode: "uri.js/src/punycode",
  IPv6: "uri.js/src/IPv6",
  SecondLevelDomains: "uri.js/src/SecondLevelDomains",
  history: "history.js/scripts/uncompressed/history",
  historyadapter: "history.js/scripts/uncompressed/history.adapter.jquery",
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
/* jshint ignore:end */
