<template>
    <h3> Mean delay per station </h3>
    <!-- Initialize a select button -->
    <select id="selectButton"></select>
    <br>

    <!-- Create a div where the graph will take place -->
    <div id="line_chart_departure"></div>
</template>

<script>
import * as d3 from 'd3';
import { ref, onMounted } from 'vue';
import { storeToRefs } from "pinia";
import { useChartStore } from '/src/stores/useChartStore';

export default {
    setup() {
        const store = useChartStore();
        onMounted(() => {
            if (!store.amtrak)
            {  
              d3.json('/public/amtrak-delays.json').then(result => {
                store.amtrak = result;
                store.displayLineChart('#line_chart_departure', '#selectButton');
              });
            } 
            else {
                store.displayLineChart('#line_chart_departure', '#selectButton');
            }
          });
        

        return {};
    }
}
</script>

<style>

</style>