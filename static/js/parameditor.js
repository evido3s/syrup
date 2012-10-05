// Parameter editor
$(document).ready(function() {
    function editor() {
        var elid = $(this).attr('id');
        var param_id = $(this).attr('param_id');

        // create new input element
        var einput = $('<input type="text" name="param_value"></input>');
        einput.attr('value', $(this).html());
        einput.attr('oldvalue', $(this).html());
        einput.css('width', '30em');

        $('#param_edit_id').val($(this).attr('param_id'));
        $(this).html(einput);
        einput.focus();

        // unbind click event and bind blur event
        $(this).unbind('click')
        einput.blur(function() {
            var espan = $(this).parent();
            espan.html($(this).attr('oldvalue'));
            espan.click(editor);
        });
    };
    $('.param_edit').click(editor);
});
