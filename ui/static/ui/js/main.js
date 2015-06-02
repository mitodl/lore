define(['jquery', 'bootstrap', 'icheck', 'retina'], function($) {
    jQuery(document).ready(function($){
      $('input.icheck-11').iCheck({
          checkboxClass: 'icheckbox_square-blue',
          radioClass: 'iradio_square-blue'
      });
      $("[data-toggle=popover]").popover();

      //open the lateral panel
      $('.cd-btn').on('click', function(event){
          event.preventDefault();
          $('.cd-panel').addClass('is-visible');
      });

      //close the lateral panel
      $('.cd-panel').on('click', function(event){
        if ($(event.target).is('.cd-panel') ||
            $(event.target).is('.cd-panel-close') ) {
          $('.cd-panel').removeClass('is-visible');
          event.preventDefault();
        }
      });

      //open the lateral panel
      $('.btn-taxonomies').on('click', function(event){
        event.preventDefault();
        $('.cd-panel-2').addClass('is-visible');
      });

      //close the lateral panel
      $('.cd-panel-2').on('click', function(event){
        if ($(event.target).is('.cd-panel-2') ||
            $(event.target).is('.cd-panel-close') ) {
          $('.cd-panel-2').removeClass('is-visible');
          event.preventDefault();
        }
      });
  });
});
