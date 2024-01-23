import * as d3 from 'd3';

function displayTop10(data, id, reset_id, alpha, top5_id, bottom5_id, asc_id, des_id, all_id) {
 
        var margin = { top: 40, left: 75, bottom: 100, right: 200 },
            width = 1200 - margin.left - margin.right,
            height = 400 - margin.top - margin.bottom;

            var svg = d3.select(id).append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')');

            var dataset, all, mode;
            var x = d3.scaleBand();
            var y = d3.scaleLinear();
            var xAxis, yAxis; 
            var sort;

            dataset = data;
            all = data;
            dataset.sort(function(a, b) { return d3.ascending(a.Station, b.Station); });
            drawBars();
            sort = "alphabetical";
            mode = "all";
            


            //sort bars
            d3.select(reset_id)
                .on("click", function () {
                    dataset = all;
                    sort = "alphabetical";
                    mode = "all";
                    x.domain(dataset.sort(
                        function(a, b) { return d3.ascending(a.Station, b.Station); }
                    ).map(function (d) { return d.Station; }));
                    filterBars();
                });

            d3.select(alpha)
                .on("click", function () {
                    sort = "alphabetical";
                    x.domain(dataset.sort(
                        function(a, b) { return d3.ascending(a.Station, b.Station); }
                    ).map(function (d) { return d.Station; }));
                    transitionBars();
                });
            d3.select(asc_id)
                .on("click", function () {
                    sort = "ascending";
                    x.domain(dataset.sort(
                        function(a, b) { return d3.ascending(a.Ridership, b.Ridership); }
                    ).map(function (d) { return d.Station; }));
                    transitionBars();
                });
            d3.select(des_id)
                .on("click", function () {
                    sort = "descending";
                    x.domain(dataset.sort(
                        function(a, b) { return d3.descending(a.Ridership, b.Ridership); }
                    ).map(function (d) { return d.Station; }));
                    transitionBars();
                });

            // filter bars
            d3.select(all_id)
                .on("click", function () {
                    mode = "all"
                    dataset = all.sort(
                        function(a, b) { return d3.descending(a.Ridership, b.Ridership); }
                    ).slice(0, 10);
                    
                    if (sort === "alphabetical") {
                        dataset.sort(function(a, b) { return d3.ascending(a.Station, b.Station); })
                    } else if (sort === "ascending") {
                        dataset.sort(function(a, b) { return d3.ascending(a.Ridership, b.Ridership); })
                    } else if (sort === "descending") {
                        dataset.sort(function(a, b) { return d3.descending(a.Ridership, b.Ridership); })
                    }
                    
                    filterBars();
            });

            d3.select(top5_id)
                .on("click", function () {
                    mode = "top 5"
                    dataset = all.sort(
                        function(a, b) { return d3.descending(a.Ridership, b.Ridership); }
                    ).slice(0, 5);
                    
                    if (sort === "alphabetical") {
                        dataset.sort(function(a, b) { return d3.ascending(a.Station, b.Station); })
                    } else if (sort === "ascending") {
                        dataset.sort(function(a, b) { return d3.ascending(a.Ridership, b.Ridership); })
                    } else if (sort === "descending") {
                        dataset.sort(function(a, b) { return d3.descending(a.Ridership, b.Ridership); })
                    }

                    filterBars();
            });

            d3.select(bottom5_id)
                .on("click", function () {
                    mode = "bottom 5"
                    dataset = all.sort(
                        function(a, b) { return d3.descending(a.Ridership, b.Ridership); }
                    ).slice(5, 10);

                    if (sort === "alphabetical") {
                        dataset.sort(function(a, b) { return d3.ascending(a.Station, b.Station); })
                    } else if (sort === "ascending") {
                        dataset.sort(function(a, b) { return d3.ascending(a.Ridership, b.Ridership); })
                    } else if (sort === "descending") {
                        dataset.sort(function(a, b) { return d3.descending(a.Ridership, b.Ridership); })
                    }

                    filterBars();
            });


            function filterBars() {
                //update scale
                x.domain(dataset.map(function (d) { return d.Station; }));

                ////////////////////////////////
                // DATA JOIN FOR BARS.
                var bars = svg.selectAll(".bar")
                    .data(dataset, function (d) { return d.Station; });

                // UPDATE + ENTER.
                bars.enter().append("rect")
                    .attr("x", function (d) { return x(d.Station); })
                    .attr("y", function (d) { return y(d.Ridership); })
                    .merge(bars)
                    .transition()
                    .duration(750)
                    .attr("class", "bar")
                    .attr("x", function (d) { return x(d.Station); })
                    .attr("y", function (d) { return y(d.Ridership); })
                    .attr("width", x.bandwidth())
                    .attr("height", function (d) { return height - y(d.Ridership); })
                    .attr('fill', 'mistyrose');

                // EXIT.
                bars.exit()
                    .transition()
                    .duration(750)
                    .style("opacity", 0)
                    .remove();

                

                ////////////////////////////////
                // x_axis.                 
                xAxis = d3.axisBottom()
                    .scale(x);
                svg.select(".x_axis")
                    .transition()
                    .duration(750)
                    .call(xAxis)
                    .selectAll('text')  
                    .attr('text-anchor', 'start');
                // y_axis. 
                svg.select(".y_axis")
                    .call(yAxis);

                ////////////////////////////////
                // title.   
                var titles = svg.select(".title")              
                    .transition()
                    .duration(750)
                    .text("Amtrak Ridership at " + mode +  " stations in " + sort + " order")
            }

            function transitionBars() {
                var transition = svg.transition()
                    .duration(750);

                transition.selectAll(".bar")
                    .attr("x", function (d) {
                        return x(d.Station);
                    });

                transition.selectAll(".label")
                    .attr("x", function (d) {
                        return x(d.Station) + x.bandwidth() / 2;
                    });

                transition.select(".x_axis").call(xAxis);
                transition.select(".y_axis").call(yAxis);
                
                transition.select(".title")
                    .text("Amtrak Ridership at " + mode +  " stations in " + sort + " order");
            }

            function drawBars() {
                x.domain(dataset.map(function (d) { return d.Station; }))
                    .range([0, width])
                    .padding(0.05);

                y.domain([0, d3.max(dataset, function (d) { return d.Ridership; })])
                    .range([height, 0]);

                svg.selectAll(".bar")
                    .data(dataset, function (d) { return d.Station; })
                    .enter().append("rect")
                    .attr("class", "bar")
                    .attr("x", function (d) { return x(d.Station); })
                    .attr("y", function (d) { return y(d.Ridership); })
                    .attr("width", x.bandwidth())
                    .attr("height", function (d) { return height - y(d.Ridership); })
                    .attr('fill', 'mistyrose');

                
                //xAxis;
                xAxis = d3.axisBottom()
                    .scale(x);

                svg.append("g")
                    .attr("class", "x_axis")
                    .attr("transform", "translate(0," + height + ")")
                    .call(xAxis);
                    
                svg.append("text")
                    .attr("class", "xlabel")
                    .text("Station")
                    .attr("x", width/2)
                    .attr("y", height + 70)
                    .style("baseline-shift", "nomal")

                //yAxis;
                yAxis = d3.axisLeft()
                    .scale(y)
                    .ticks(5, 'd');

                svg.append("g")
                    .attr("class", "y_axis")
                    .call(yAxis);

                svg.append("text")
                    .attr('x', - height / 2)
                    .attr('y', - margin.left * 0.7)
                    .attr('transform', 'rotate(-90)')
                    .attr('class', 'ylabel')
                    .style('font-size', '1em')
                    .append('tspan').text('RiderShip');;
                
                //title
                svg.append("text")
                .attr("class", "title")
                .text("Ridership at top 10 busiest Amtrak Stations")
                .attr("x", (margin.right * 2))
                .attr("y", 0)
                .style("baseline-shift", "nomal");
            }
    }

export { displayTop10 }




