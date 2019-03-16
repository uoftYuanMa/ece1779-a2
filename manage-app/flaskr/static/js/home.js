$(document).ready(function() {
    $('#nav-home').siblings().removeClass('active');
    $('#nav-home').addClass('active');

    loadTable()

    $('#show_btn').on("click", function(){
        var instances = [];
        $("input[name=instance]:checked").each( function () {
            instances.push($(this).val());
        });
        // console.log(instances)
        if (instances.length > 0) {
            showCharts(instances)
        } else {
            $('#charts1').html("");
            $('#charts2').html("");
        }
    });

    $('#add_btn').on("click", function(){
        addInstance()
    });

    $('#delete_btn').on("click", function(){
        var instances = [];
        $("input[name=instance]:checked").each( function () {
            instances.push($(this).val());
        });
        // console.log(instances)
        if (instances.length > 0) {
            deleteInstance(instances)
        } else {
            msg = "No instances chosen."
            showAlert(msg, 'alert-warning')
        }
    });

    Highcharts.setOptions({
        time: {
            timezone: 'Canada/Eastern'
        }
    });

});

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

function loadTable() {
    $('#workers_table').DataTable({
        ajax: "/fetch_workers",
        "columns": [
            {
                sortable: false,
                "render": function ( data, type, full, meta ) {
                    return '<input type="checkbox" name="instance"' + 'value="'+ full.Id +'"/>';
                }
             },
            {"data": 'Id'},
            {"data": 'Port'},
            {"data": 'State'},
        ],
    });
}

function showCharts(instances) {
    $.ajax({
        type: 'POST',
        url: '/fetch_cpu_utils',
        data: JSON.stringify(instances),
        contentType: false,
        cache: false,
        processData: false,
        beforeSend: function() {
            $('#charts1').html("<img class='loading' src='static/img/loading.gif'>");
        },
        success: function(data) {
            data = JSON.parse(data);
            newdata = []
            for (i=0 ; i<data.length ; i++){
                name = data[i].name
                info = JSON.parse(data[i].data)
                newdata.push({
                    "name": name,
                    "data": info
                })
            }

            var myChart1 = Highcharts.stockChart('charts1', {
                legend: {
                        enabled: true,
                        align: 'right',
                },

                rangeSelector: {
                    selected: 1
                },

                title: {
                    text: 'Instances CPU Utilities in Worker Pool'
                },

                series: newdata
            });
        }
    });

    $.ajax({
        type: 'POST',
        url: '/fetch_requests_rate',
        data: JSON.stringify(instances),
        contentType: false,
        cache: false,
        processData: false,
        beforeSend: function() {
            $('#charts2').html("<img class='loading' src='static/img/loading.gif'>");
        },
        success: function(data) {
            data = JSON.parse(data);
            newdata = []
            for (i=0 ; i<data.length ; i++){
                name = data[i].name
                info = JSON.parse(data[i].data)
                newdata.push({
                    "name": name,
                    "data": info
                })
            }

            var myChart2 = Highcharts.stockChart('charts2', {
                legend: {
                        enabled: true,
                        align: 'right',
                },

                rangeSelector: {
                    selected: 1
                },

                title: {
                    text: 'Instances Requests rate in Worker Pool'
                },

                series: newdata
            });
        }
    });
 }

 function addInstance() {
    $.ajax({
        type: 'POST',
        url: '/grow_one_worker',
        data: '',
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            data = JSON.parse(data);
            if(data.flag == true) {
                msg = 'One worker grown.'
                showAlert(msg, 'alert-success')
                $('#workers_table').DataTable().ajax.reload();
            } else {
                showAlert(data.msg, 'alert-danger')
            }
        }
    });
 }

function deleteInstance(instances) {
    $.ajax({
        type: 'POST',
        url: '/shrink_one_worker',
        data: JSON.stringify(instances),
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            data = JSON.parse(data);
            if (data.flag == true) {
                msg = "One worker deleted."
                showAlert(msg, 'alert-success')
                $('#workers_table').DataTable().ajax.reload();
            } else {
                showAlert(data.msg, 'alert-danger')
            }
        }
    });
}