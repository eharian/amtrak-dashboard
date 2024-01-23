import * as d3 from 'd3';

function avgDelayLine(data, id, button_id) {
    

    // set the dimensions and margins of the graph
    var margin = { top: 30, right: 30, bottom: 30, left: 60 },
        width = 500 - margin.left - margin.right,
        height = 450 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    var svg = d3.select(id)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    const monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];

    const data_arrival = data.filter(i => i.type == 'A');
    const data_departure = data.filter(i => i.type == 'D');


    // List of groups (here I have one group per column)
    var allGroup = d3.map(data, d => d.station).filter((v, i, a) => a.indexOf(v) === i).sort();

    // add the options to the button
    d3.select(button_id)
        .selectAll('myOptions')
        .data(allGroup)
        .enter()
        .append('option')
        .text(function (d) { return d; }) // text showed in the menu
        .attr("value", function (d) { return d; }) // corresponding value returned by the button

    // create a list of keys
    var keys = ["Arrival", "Departure"]

    // A color scale: one color for each group
    var color = d3.scaleOrdinal()
        .domain(allGroup)
        .range(d3.schemeSet2);

    // Add X axis --> it is a date format
    var x = d3.scaleBand()
        .domain(monthNames)
        .range([0, width]);
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("y", 0)
        .attr("x", 8)
        .attr("dy", ".35em")
        .style("font", "8px times")
        .attr("transform", "rotate(40)")
        .style("text-anchor", "start");


    // Add Y axis
    var y = d3.scaleLinear()
        .domain([0, d3.max(data, function (d) { return +d.delay; })])
        .range([height, 0]);
    svg.append("g")
        .call(d3.axisLeft(y));

    // Add the text label for the Y axis
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margin.left)
        .attr("x", 0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Average Delay (minutes)");


    // Add title
    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 0 - (margin.top / 2))
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .style("text-decoration", "underline")
        .text("Average Delay for each Station");

    // Add one dot in the legend for each name.
    var size = 10
    svg.selectAll("mydots")
        .data(keys)
        .enter()
        .append("rect")
        .attr("x", width - 55)
        .attr("y", function (d, i) { return 100 + i * (size + 5) }) // 100 is where the first dot appears. 25 is the distance between dots
        .attr("width", size)
        .attr("height", size)
        .style("fill", function (d) { return color(d) })

    // Add one dot in the legend for each name.
    svg.selectAll("mylabels")
        .data(keys)
        .enter()
        .append("text")
        .attr("x", width - 55 + size * 1.2)
        .attr("y", function (d, i) { return 100 + i * (size + 5) + (size / 2) }) // 100 is where the first dot appears. 25 is the distance between dots
        .style("fill", function (d) { return color(d) })
        .text(function (d) { return d })
        .attr("text-anchor", "left")
        .style("alignment-baseline", "middle")


    // Initialize line with for Departure delay
    var line = svg
        .append('g')
        .append("path")
        .datum(data_departure.filter(function (d) { return d.station == allGroup[0] }))
        .attr("d", d3.line()
            .x(function (d) { return x(d.month) })
            .y(function (d) { return y(+d.delay) })
        )
        .attr("stroke", function (d) { return color("Departure") })
        .style("stroke-width", 4)
        .style("fill", "none")

    // Initialize line with for Arrival delay
    var line2 = svg
        .append('g')
        .append("path")
        .datum(data_arrival.filter(function (d) { return d.station == allGroup[0] }))
        .attr("d", d3.line()
            .x(function (d) { return x(d.month) })
            .y(function (d) { return y(+d.delay) })
        )
        .attr("stroke", function (d) { return color("Arrival") })
        .style("stroke-width", 4)
        .style("fill", "none")

    // A function that update the chart
    function update(selectedGroup) {

        // Create new data with the selection?
        var dataFilter = data_departure.filter(function (d) { return d.station == selectedGroup })
        var dataFilter2 = data_arrival.filter(function (d) { return d.station == selectedGroup })

        // Give these new data to update line
        line
            .datum(dataFilter)
            .transition()
            .duration(1000)
            .attr("d", d3.line()
                .x(function (d) { return x(d.month) })
                .y(function (d) { return y(+d.delay) })
            )
            .attr("stroke", function (d) { return color("Departure") })


        line2
            .datum(dataFilter2)
            .transition()
            .duration(1000)
            .attr("d", d3.line()
                .x(function (d) { return x(d.month) })
                .y(function (d) { return y(+d.delay) })
            )
            .attr("stroke", function (d) { return color("Arrival") })
    }

    // When the button is changed, run the updateChart function
    d3.select(button_id).on("change", function (d) {
        // recover the option that has been chosen
        var selectedOption = d3.select(this).property("value")
        // run the updateChart function with this selected option
        update(selectedOption)
    })
}


export { avgDelayLine }