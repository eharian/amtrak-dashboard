import * as d3 from 'd3';

function displayStack(data, id) {

  const margin = { top: 10, right: 100, bottom: 110, left: 50 },
    width = 1400 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

  // append the svg object to the body of the page
  const svg = d3.select(id)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // List of subgroups = header of the csv files = soil condition here
  const subgroups = data.columns.slice(1)

  // List of groups = species here = value of the first column called group -> I show them on the X axis
  const groups = data.map(d => d.train)

  // Add X axis
  const x = d3.scaleBand()
    .domain(groups)
    .range([0, width])
    .padding([0.02])
  svg.append("g")
    .attr("transform", `translate(0, ${height})`)
    .call(d3.axisBottom(x).tickSizeOuter(0))
    .selectAll("text")
    .attr("y", 0)
    .attr("x", 9)
    .attr("dy", ".35em")
    .attr("transform", "rotate(90)")
    .style("text-anchor", "start");

  // Add Y axis
  const y = d3.scaleLinear()
    .domain([0, 200000])
    .range([height, 0]);
  svg.append("g")
    .call(d3.axisLeft(y));

  // color palette = one color per subgroup
  const color = d3.scaleOrdinal()
    .domain(subgroups)
    .range(d3.schemeSet2);

  //stack the data? --> stack per subgroup
  const stackedData = d3.stack()
    .keys(subgroups)
    (data)
  for (let i = 0; i < stackedData.length; i++) {
    for (let j = 0; j < stackedData[i].length; j++) {
      if (isNaN(stackedData[i][j][1])) {
        stackedData[i][j][1] = 0
      }
    }
  }
  // Add one dot in the legend for each name.
  svg.selectAll("mydots")
    .data(subgroups)
    .enter()
    .append("circle")
    .attr("cx", width)
    .attr("cy", function (d, i) { return  i * 25 }) // 100 is where the first dot appears. 25 is the distance between dots
    .attr("r", 7)
    .style("fill", function (d) { return color(d) })

  // Add one dot in the legend for each name.
  svg.selectAll("mylabels")
    .data(subgroups)
    .enter()
    .append("text")
    .attr("x", width + 20)
    .attr("y", function (d, i) { return   i * 25 }) // 100 is where the first dot appears. 25 is the distance between dots
    .style("fill", function (d) { return color(d) })
    .text(function (d) { return d })
    .attr("text-anchor", "left")
    .style("alignment-baseline", "middle")
  // ----------------
  // Highlight a specific subgroup when hovered
  // ----------------
  // Show the bars
  svg.append("g")
    .selectAll("g")
    // Enter in the stack data = loop key per key = group per group
    .data(stackedData)
    .join("g")
    .attr("fill", d => color(d.key))
    .selectAll("rect")
    // enter a second time = loop subgroup per subgroup to add all rectangles
    .data(d => d)
    .join("rect")
    .attr("x", d => x(d.data.train))
    .attr("y", d => y(d[1]))
    .attr("height", d => y(d[0]) - y(d[1]))
    .attr("width", 20)


}

export { displayStack }