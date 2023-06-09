$(document).on('click', '[id="alert"]', function(e) {
    var current_row = $(this).closest('tr');
    var part_id = current_row.find('td:eq(0)').html();
    var postavshik = current_row.find('td:eq(1)').html();
    var tname = $(this).attr('tname');
    var stock_id = $(this).attr('st_id');

    $("#modal_postavshik").val(postavshik);
    $("#modal_part_id").val(part_id);
    $("#modal_st_id").attr("stock_id", stock_id);
    $("#modal_tname").attr("tname", tname);
});

$(document).on('click', '[id="modal_st_id"]', function(e) {
    var tname = $("#modal_tname").attr("tname");
    var part_id = $("#modal_part_id").val();
    var postavshik = $("#modal_postavshik").val();
    var qty = $("#modal_qty").val();
    var comment = $("#modal_comment").val();
    var stock_id = $("#modal_st_id").attr("stock_id");
    $.ajax({
        url: "/new_order/",
        type: "POST",
        data: {
            tablename: tname,
            qty: qty,
            partId: part_id,
            postavshik_id: postavshik,
            stock_id: stock_id,
            comment: comment
        },
        success: function(response) {
            var result = response.result;
            notify({
                type: "success",
                title: "Заказ " + part_id + " выполнен",
                message: result,
                position: {
                    x: "right",
                    y: "top"
                },
                autoHide: true,
                delay: 10000
            });
        }
    });
});

