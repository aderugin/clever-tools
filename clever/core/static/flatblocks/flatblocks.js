$(document).ready(function(){
    (function(){
        var block = '.b-flatblock-edit';
        $(block).find('.flatblock-edit-link').click(function(){

            var url = $(this).attr('href');
            var coords = $(this).offset();
            var left = coords.left;
            var top = coords.top;

            console.log(coords);

            $.ajax({
                url: url,
                type: 'GET',
                dataType: 'html',
                success: function (data) {
                    result = $(data).filter('.b-flatblock__edit-popup').css({'left': coords.left, 'top': coords.top});
                    $('body').append(result);

                    var close_btn = $('.b-flatblock__edit-popup').find('.btn[data-dismiss="modal"]');

                    $(close_btn).bind('click', function(){
                        $(this).parents('.b-flatblock__edit-popup').remove();
                        return false;
                    });
                }
            });
            return false;

        });
    })();
});
