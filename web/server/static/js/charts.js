function drawChart(data, divname) {
    $.plot($(divname), [data], {
        xaxis: {
            mode: "time",
            label: "Timestamp (UTC)",
            timeformat: "%y/%m/%d %H:%M"
        },
        yaxis:{
            label: "Load (%)",
            max: 100,
            min: 0
        }
    });
}

function drawTemp(data, divname) {
    $.plot($(divname), [data], {
        xaxis: {
            mode: "time",
            timeformat: "%y/%m/%d %H:%M"
        },
        yaxis:{
            max: 100,
            min: 20
        }
    })
}