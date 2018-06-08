/**
 * Created by LBI on 2017/3/21.
 */

$(function () {
    $('select,input,textarea').focus(function () {
        if ($(this).next().hasClass('field-validation-error')) {
            $(this).next().remove();
            $(this).removeClass('input-validation-error').removeClass('Validform_wrong');
        }

        if ($(this).next().hasClass('Validform_wrong')) {
            $(this).next().remove();
            $(this).removeClass('Validform_error');
        }

    });
});
$('select,input,textarea').each(function () {
    if ($(this).next().hasClass('field-validation-error')) {
        $(this).addClass('input-validation-error');
    }
});

$('input[name=username],input[name=password]').each(function () {
    if ($(this).next().hasClass('Validform_wrong')) {
        $(this).addClass('Validform_error');
    }
});
