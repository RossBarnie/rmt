google.load("visualization", "1", {packages:["corechart"]});
function drawChart(graph_datatable, title, resource) {
        var data = google.visualization.DataTable(graph_datatable);
        var options = {
            title: title
        };

        var chart = new google.visualization.LineChart(document.getElementById(resource + '_chart'));
        chart.draw(data, options);
}