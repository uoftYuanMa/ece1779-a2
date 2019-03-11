$(document).ready(function() {
    $('#nav-home').siblings().removeClass('active');
    $('#nav-home').addClass('active');

    var table = $('#workers_table').DataTable({
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

    $('#show_btn').on("click", function(){
        var instances = [];
        $("input[name=instance]:checked").each( function () {
            instances.push($(this).val());
        });
        console.log(instances)
        if (instances.length > 0) {
            showCharts(instances)
        } else {
            $('#charts1').html("");
            $('#charts2').html("");
        }
    });
});

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