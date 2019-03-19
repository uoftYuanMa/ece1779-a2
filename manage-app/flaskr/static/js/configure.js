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
    $('#clear_btn').on("click", function() {
        clear_data()
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

function clear_data() {
    $.ajax({
        type: 'POST',
        url: '/clear_data',
        data: '',
        contentType: false,
        cache: false,
        processData: false,
        beforeSend: function() {
            $('#clear_btn').html("Clearing <img class='ajax-loading' src='static/img/ajax-loading.gif'>")
            $('#clear_btn').prop("disabled", true)
        },
        success: function(data) {
            data = JSON.parse(data);
            if(data.flag == true) {
                msg = 'All data cleared.'
                showAlert(msg, 'alert-success')
            } else {
                showAlert(data.msg, 'alert-danger')
            }
            $('#clear_btn').html("Clear")
            $('#clear_btn').prop("disabled", false)
        },
        error: function(xhr, textStatus, error){
            showAlert("Unable to clear data", "alert-danger")
            $('#clear_btn').html("Clear")
            $('#clear_btn').prop("disabled", false)
            console.log(error)
        }
    });
}

function showAlert(msg, type) {
    if (type == 'alert-warning') {
        title = "Warning: "
    } else if (type == 'alert-success') {
        title = "Success: "
    } else if (type == 'alert-danger') {
        title = "Failure: "
    } else { return ''}

    msg = "<strong>" + title + "</strong>" + msg
    alert = "<div class='alert " + type + " alert-dismissible fade show' role='alert'>" + msg
    alert += "<button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span>"
    alert += "</button></div>"
    $('#msg').html(alert)
}