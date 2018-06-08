//对表单校验、ajax的封装
Nature = new Object();

Nature.FormSubmit = function (formInfo, ajaxInfo) {
    //表单提交
    $("#submitBtn").click(function () {
        $("#mainForm").submit();
    });

    formInfo.errorElement = "em";
    formInfo.invalidHandler = function (form, validator) { //validate只显示第一个警告
        // $.each(validator.invalid, function (key, value) {
        //     if ($("span[id='" + key + "-error" + "']").length > 0) {
        //         return false;
        //     }
        // });
        $.each(validator.invalid, function (key, value) {
            if ($("span[for='" + key + "']").length > 0) {
                $("span[for='" + key + "']").remove();
            }
            $("[name='" + key + "']").after("<span for='" + key + "' class='hint'>" + value + "</span>")
            return false;
        });
    }
    formInfo.highlight = function (element) {
        $(element).parents(".controls").addClass("error");
    }
    formInfo.success = function (element) {
        $(element).parents(".controls").removeClass('error');
    }
    //提交处理
    formInfo.submitHandler = function (form) {
        Nature.Ajax(ajaxInfo);
    }

    //表单验证
    $("#mainForm").validate(formInfo);
}


Nature.Ajax = function (ajaxInfo) {

    //定义默认值
    //type: "GET",   //访问方式：如果dataPata不为空，自动设置为POST；如果为空设置为GET。
    //dataType: "JSON",      //数据类型：JSON、JSONP、text
    //cache: true,   //是否缓存，默认缓存
    //urlPara: {},  //url后面的参数。一定会加在url后面，不会加到form里。
    //formData: {},  //表单里的参数。如果dataType是JSON，一定加在form里，不会加在url后面；如果dataType是JSONP的话，只能加在url后面。
    //url:  //依靠上层指定

    //补全ajaxInfo
    //dataType
    if (typeof ajaxInfo.dataType == "undefined") ajaxInfo.dataType = 'JSON';
    //cache
    if (typeof ajaxInfo.cache == "undefined") ajaxInfo.cache = false;
    //type
    if (typeof ajaxInfo.type == "undefined") {
        ajaxInfo.type = "POST";
        //ajaxInfo.data = ajaxInfo.formData;
        ajaxInfo.data = $('#mainForm').serialize();
    }

    //处理URL和参数
    if (typeof ajaxInfo.urlPara != "undefined") {
        var tmpUrlPara = "";
        var para = ajaxInfo.urlPara;
        for (var key in para) {
            tmpUrlPara += "&" + key + "=" + para[key];
        }
        if (ajaxInfo.url.indexOf('?') >= 0) {
            //原地址有参数，直接加
            ajaxInfo.url += tmpUrlPara;
        } else {
            //原地址没有参数，变成?再加
            ajaxInfo.url += tmpUrlPara.replace('&', '?');
        }
    }

    //处理xhrFields
    if (typeof ajaxInfo.xhrFields == "undefined") {
        ajaxInfo.xhrFields = {
            //允许cors跨域访问时添加cookie
            withCredentials: true
        };
    } else {
        if (typeof ajaxInfo.xhrFields.withCredentials == "undefined") {
            ajaxInfo.xhrFields.withCredentials = true;
        }
    }
    //使用cors的方式实现跨域
    jQuery.support.cors = true;

    //处理error
    var error = ajaxInfo.error;
    ajaxInfo.error = function (request, textStatus, errorThrown) {
        //访问失败，自动停止加载动画，并且给出提示
        alert("请求发生错误！");
        if (typeof error == "function") error();
    };


    //处理success
    var success = ajaxInfo.success;
    ajaxInfo.success = function (data) {
        if (data.retcode == "10001") {
            parent.layer.msg(data.msg, {icon: 5, time: 1000});
        }
        else {
            if (ajaxInfo.success_redirect_url) {
                window.location.href = ajaxInfo.success_redirect_url;
            }
            else if (typeof success == "function") {
                success(data)
            }
            else {
                parent.layer.msg('操作成功', {icon: 6, time: 1000});
            }
        }
    };
    ajaxInfo.beforeSend = function (XMLHttpRequest) {
        XMLHttpRequest.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        // if ($('#loadingToast').length == 0) {
        //     $("body").append(toast);
        // }
        // $('#loadingToast').fadeIn(100);
    }
    ajaxInfo.complete = function (XMLHttpRequest, textStatus) {
        //$('#loadingToast').fadeOut(100);
    }

    //开始执行ajax
    $.ajax(ajaxInfo);
};

//添加错误提示
function addError(id, msg) {
    if (!$("#" + id).parent(".controls").hasClass("error")) {
        $("#" + id).parent(".controls").addClass("error");
    }
    $("#" + id).after("<span for='" + id + "' class='hint'>" + msg + "</span>");
}

//$.ajax({
//    type: ajaxInfo.type,
//    dataType: ajaxInfo.dataType,
//    cache: ajaxInfo.cache,
//    xhrFields: {
//        //允许跨域访问时添加cookie
//        withCredentials: true
//    },
//    url: ajaxInfo.url,
//    data: ajaxInfo.data,
//    //timeout: 2000,
//    error: function (request, textStatus, errorThrown) { //访问失败，自动停止加载动画，并且给出提示
//        alert("提交" + ajaxInfo.title + "的时候发生错误！");
//        if (typeof ajaxInfo.error == "function") ajaxInfo.error();
//    },
//    success: function (data) {
//    }
//});

  
 