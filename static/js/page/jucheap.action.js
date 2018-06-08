(function () {
    //返回按钮
    $("#btnBack")
        .bind("click",
            function (e) {
                var type = $(this).data("type");
                if (type === "window") {//表示关闭弹框
                    parent.layer.closeAll();
                } else if (type === "url") {//表示url跳转
                    window.history.go(-1);
                }
            });
    $("#btnSave")
        .bind("click",
            function () {
                //$(this).button("loading");
            });
})();

function postData(url, params, success, error, method) {
    $.ajax({
        url: url,
        type: 'POST',
        data: params,
        success: function (res) {
            if (res.retcode == '10000') {
                if (success) {
                    success(res);
                }
                else {
                    parent.layer.msg('操作成功', {icon: 6, time: 1000});
                }
            } else {
                if (error) {
                    error(res);
                }
                else {
                    parent.layer.msg(res.msg, {icon: 5, time: 1000});
                }
            }
        }
    });
}