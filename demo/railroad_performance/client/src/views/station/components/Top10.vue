<template>
    <div id="top10">
        <div class="col-md-12 pt-4 controls">
                Show: <button type="button" class="btn btn-outline-info filter" id="all10">All</button>
                <button type="button" class="btn btn-outline-info filter" id="top5">Top 5</button>
                <button type="button" class="btn btn-outline-info filter" id="bottom5">Bottom 5</button>
        </div>
        <div class="col-md-12 pt-4 controls">
                Sort in: <button type="button" id="Station_alphabetical" class="btn btn-outline-warning sort">Alphabetic order</button>
                <button type="button" id="Ridership_asc" class="btn btn-outline-warning sort">Ridership
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-up" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 15a.5.5 0 0 0 .5-.5V2.707l3.146 3.147a.5.5 0 0 0 .708-.708l-4-4a.5.5 0 0 0-.708 0l-4 4a.5.5 0 1 0 .708.708L7.5 2.707V14.5a.5.5 0 0 0 .5.5z"/>  
</svg>
                </button>
                <button type="button" id="Ridership_des" class="btn btn-outline-warning sort">Ridership 
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-down" viewBox="0 0 16 16">
  <path fill-rule="evenodd" d="M8 1a.5.5 0 0 1 .5.5v11.793l3.146-3.147a.5.5 0 0 1 .708.708l-4 4a.5.5 0 0 1-.708 0l-4-4a.5.5 0 0 1 .708-.708L7.5 13.293V1.5A.5.5 0 0 1 8 1z"/>
</svg>
                </button>
        </div>
        <div class="col-md-12 pt-4 controls">
                <button type="button" id="reset" class="btn btn-outline-danger">Reset</button>  
        </div>

    </div>
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
                if (! store.ridership)
                {
                    d3.json('/public/ridership.json').then(result => {
                        store.ridership = result;
                        store.displayBarChart('#top10','#reset', '#Station_alphabetical', '#top5', '#bottom5', '#Ridership_asc', '#Ridership_des', '#all10');
                    })
                }
                else {
                    store.displayBarChart();
                }
            });
        return {};
    }
}
</script>

<style>
.controls {
    text-align: center;
}
.controls button {
    margin: 0 5px;
}
#chart {
    text-align: center;
}
rect.bar:hover {
    fill: pink;
}
svg {
    margin: 0 10%;
}
</style>