({
  "name": "listing",
  "fileExclusionRegExp": /^node_modules|^staticfiles|^htmlcov|^coverage|^ui\/jstests/,
  "baseUrl": "../../../../",
  "paths": {
    "jquery": "ui/static/bower/jquery/dist/jquery",
    "bootstrap": "ui/static/bower/bootstrap/dist/js/bootstrap",
    "icheck": "ui/static/bower/icheck/icheck",
    "retina": "ui/static/bower/retina.js/dist/retina",
    "react": "ui/static/bower/react/react-with-addons",
    "JSXTransformer": "ui/static/bower/react/JSXTransformer",
    "jsx": "node_modules/requirejs-react-jsx/jsx",
    "text": "node_modules/requirejs-text/text",
    "react_infinite": "ui/static/bower/react-infinite/dist/react-infinite",
    "react_datagrid": "ui/static/lib/js/react-datagrid",
    "lodash": "ui/static/bower/lodash/lodash",
    "select2": "ui/static/bower/select2/dist/js/select2.full",
    "uri": "ui/static/bower/uri.js/src/URI",
    "punycode": "ui/static/bower/uri.js/src/punycode",
    "IPv6": "ui/static/bower/uri.js/src/IPv6",
    "SecondLevelDomains": "ui/static/bower/uri.js/src/SecondLevelDomains",
    "history": "ui/static/bower/history.js/scripts/compressed/history",
    "historyadapter": "ui/static/bower/history.js/scripts/compressed/history.adapter.jquery",
    "csrf": "ui/static/ui/js/csrf",
    "listing": "ui/static/ui/js/listing",
    "manage_taxonomies": "ui/static/ui/js/manage_taxonomies",
    "xml_panel": "ui/static/ui/js/xml_panel",
    "learning_resources": "ui/static/ui/js/learning_resources",
    "listing_resources": "ui/static/ui/js/listing_resources",
    "static_assets": "ui/static/ui/js/static_assets",
    "lr_exports": "ui/static/ui/js/lr_exports",
    "pagination": "ui/static/ui/js/pagination",
    "utils": "ui/static/ui/js/utils",
  },
  "shim": {
    "react": {
      "exports": "React"
    },
    "JSXTransformer": "JSXTransformer",
    "icheck": {"deps": ["jquery"]},
    "bootstrap": {"deps": ["jquery"]},
    "react_infinite": {"deps": ["react"]},
    "historyadapter": {"deps": ["jquery"]},
    "history": {"deps": ["historyadapter"], "exports": "History"}
  },
  "onBuildWrite": function(moduleName, path, singleContents) {
    return singleContents.replace(/jsx!/g, '');
  },
  "config": {
    "jsx": {
      "fileExtension": ".jsx",
      "transformOptions": {
        "harmony": true,
        "stripTypes": false,
        "inlineSourceMap": true
      },
      "usePragma": false
    }
  },
  "optimize": "uglify2",
  "generateSourceMaps": true,
  "preserveLicenseComments": false,
  "out": "stdout"
})