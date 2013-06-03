(function($){

    $.fn.extend({
        insertAtCaret: function(text) {
            var txtarea = $(this).get(0);
            if (txtarea) {
                var scrollPos = txtarea.scrollTop;
                var strPos = 0;
                var br = ((txtarea.selectionStart || txtarea.selectionStart == '0') ?
                    "ff" : (document.selection ? "ie" : false ) );
                if (br == "ie") {
                    txtarea.focus();
                    var range = document.selection.createRange();
                    range.moveStart ('character', -txtarea.value.length);
                    strPos = range.text.length;
                }
                else if (br == "ff") strPos = txtarea.selectionStart;

                var front = (txtarea.value).substring(0,strPos);
                var back = (txtarea.value).substring(strPos,txtarea.value.length);
                txtarea.value=front+text+back;
                strPos = strPos + text.length;
                if (br == "ie") {
                    txtarea.focus();
                    var range = document.selection.createRange();
                    range.moveStart ('character', -txtarea.value.length);
                    range.moveStart ('character', strPos);
                    range.moveEnd ('character', 0);
                    range.select();
                }
                else if (br == "ff") {
                    txtarea.selectionStart = strPos;
                    txtarea.selectionEnd = strPos;
                    txtarea.focus();
                }
                txtarea.scrollTop = scrollPos;
            }
        }
    })

    var fields = 'input[type="text"], textarea';

    function load_vars(id) {
        $.ajax({
            url: '/notifier/load-vars/'+id+'/',
            type: 'GET',
            dataType: 'json',
            data: {},
            success: function (data)  {
                $(data.vars).each(function (i, e) {
                    for(var key in e) {
                        var v = $('<a/>').attr({'href': '#', 'data-var': '#' + key + '#'}).html(e[key] + ' - ' + key).addClass('j-var').click(function(){
                            $(fields).filter('.notifier-lastFocus').focus();
                            $(fields).filter('.notifier-lastFocus').insertAtCaret($(this).data('var'))
                            return false;
                        });

                        var item = $('<li/>').append(v);
                        $('.j-vars-list').append(item);
                    }
                });
            }
        });
    }

    $(function () {

        $(fields).bind('focus', function(){
            $(fields).removeClass('notifier-lastFocus');
            $(this).addClass('notifier-lastFocus');
        }).bind('blur', function() {})

        $('fieldset.grp-module').append($('<ul/>').addClass('j-vars-list'));
        load_vars($('#id_notification').val());

        $('#id_notification').change(function(e){
            $('.j-vars-list').html('');
            load_vars($(this).val());
        });
    });

})(jQuery || django.jQuery || grp.jQuery)
