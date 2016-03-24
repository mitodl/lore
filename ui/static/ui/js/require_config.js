// relative to ui/static/bower
/* jshint ignore:start */
var REQUIRE_PATHS = {
  jquery: "jquery/dist/jquery.min",
  bootstrap: "bootstrap/dist/js/bootstrap.min",
  icheck: "icheck/icheck.min",
  retina: "retina.js/dist/retina.min",
  React: "react/react-with-addons",
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
  spin: "spin.js/spin.min",
  csrf: "../ui/js/csrf",

  listing: "../ui/js/listing/listing.jsx?noext",
  listing_resources: "../ui/js/listing/listing_resources.jsx?noext",
  pagination: "../ui/js/listing/pagination.jsx?noext",
  import_status: "../ui/js/listing/import_status.jsx?noext",

  add_terms_component: "../ui/js/taxonomy/add_terms_component.jsx?noext",
  add_vocabulary: "../ui/js/taxonomy/add_vocabulary.jsx?noext",
  manage_taxonomies: "../ui/js/taxonomy/manage_taxonomies.jsx?noext",
  taxonomy_component: "../ui/js/taxonomy/taxonomy_component.jsx?noext",
  term_component: "../ui/js/taxonomy/term_component.jsx?noext",
  vocabulary_component: "../ui/js/taxonomy/vocabulary_component.jsx?noext",

  learning_resources: "../ui/js/learningresources/learning_resources.jsx?noext",
  learning_resource_panel: "../ui/js/learningresources/" +
    "learning_resource_panel.jsx?noext",
  static_assets: "../ui/js/learningresources/static_assets.jsx?noext",
  term_list: "../ui/js/learningresources/term_list.jsx?noext",
  vocab_select: "../ui/js/learningresources/vocab_select.jsx?noext",
  term_select: "../ui/js/learningresources/term_select.jsx?noext",
  term_list_item: "../ui/js/learningresources/term_list_item.jsx?noext",
  xml_panel: "../ui/js/learningresources/xml_panel.jsx?noext",

  lr_exports: "../ui/js/exports/lr_exports.jsx?noext",
  exports_component: "../ui/js/exports/exports_component.jsx?noext",
  exports_header: "../ui/js/exports/exports_header.jsx?noext",

  utils: "../ui/js/util/utils.jsx?noext",
  confirmation_dialog: "../ui/js/util/confirmation_dialog.jsx?noext",
  icheckbox: "../ui/js/util/icheckbox.jsx?noext",
  infinite_list: "../ui/js/util/infinite_list.jsx?noext",
  react_overlay_loader: "../ui/js/util/react_overlay_loader.jsx?noext",
  react_spinner: "../ui/js/util/react_spinner.jsx?noext",
  select2_component: "../ui/js/util/select2_component.jsx?noext",
  status_box: "../ui/js/util/status_box.jsx?noext",
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
