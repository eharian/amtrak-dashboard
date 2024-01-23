<template>
  <div id="bar-chart">
      <h3> The Top 10 busiest stations in America </h3>
        <Top10 />
  </div>
  <div id="station-map">
        <StationMap />
  </div>

  <div id="line-chart">
        <AvgDelay />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useChartStore } from '/src/stores/useChartStore';
import StationMap from './components/StationMap.vue';
import Top10 from './components/Top10.vue';
import AvgDelay from './components/AvgDelay.vue';
import * as d3 from 'd3';


export default {
    components: {
      StationMap,
      Top10,
      AvgDelay
    },
    setup() {
        return { };
    }, 

}
</script>

<style>
#station-map{
      padding: 2em;     
}
h3 {
    padding: 1em;
}
button#Ridership_asc, button#Ridership_des {
    width: 137px;
}
select#selectButton {
    text-align: center;
    width: 50%;
}
div#line-chart {
    text-align: center;
}
</style>