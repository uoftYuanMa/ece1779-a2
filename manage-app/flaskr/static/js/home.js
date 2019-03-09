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
            // show chart in #charts
            showCharts(instances)
        } else {
            $('#charts').html("");
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
            $('#charts').html("<img class='loading' src='static/img/loading.gif'>");
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

            var myChart = Highcharts.stockChart('charts', {
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
 }