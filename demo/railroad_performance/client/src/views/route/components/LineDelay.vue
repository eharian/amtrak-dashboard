<template>
    <h3> Number of delays per line in 2021 </h3>
    <div id="line-delay"> </div>
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
                 if (!store.line){
                         d3.csv('/public/amtrak-total-delay.csv').then(result => {
                        store.line = result;
                        store.displayStackedBar('#line-delay');
              });
                 }
                 else {
                    store.displayStackedBar('#line-delay');
                 }
            });
        return {};
        }
}
</script>

<style>
h3 {
    padding: 1em;
}
</style>