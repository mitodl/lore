define(['QUnit'], function(QUnit) {
  'use strict';
  QUnit.test(
    'empty test used to prevent build failure due to lack of tests',
    function(assert) {
      assert.equal(1, 1);
    }
  );
});
