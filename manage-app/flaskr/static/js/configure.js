$(document).ready(function() {
    $('#nav-configure').siblings().removeClass('active');
    $('#nav-configure').addClass('active');
    $("button[class~='btn-success']").each(function (i, ele) {
        // console.log(ele)
        $(ele).on("click", function(e){
            e.preventDefault();
            modifyEnable($(ele).attr('id'));
        });
    });
});

function modifyEnable(id) {
    // console.log(id)
    if (id == "modify-btn1") {
        $("#input1").prop('readonly', false);
    } else if (id == "modify-btn2") {
        $("#input2").prop('readonly', false);
    } else if (id == "modify-btn3") {
        $("#input3").prop('readonly', false);
    } else if (id == "modify-btn4") {
        $("#input4").prop('readonly', false);
    } else {}
}