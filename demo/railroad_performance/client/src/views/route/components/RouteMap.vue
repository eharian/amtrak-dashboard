<template>
    <h3> Mapbox map showing all Amtrak Routes </h3>
    <div id="route"></div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { storeToRefs } from "pinia";
import { useMapStore } from '/src/stores/useMapStore';


export default {
    setup() {
        //const map = ref(null)
        const store = useMapStore();
        const { station, dataset } = storeToRefs(store)
        const { loadStationData, createMap } = store

        onMounted(() =>{
            store.loadStationData('route')
            store.createMap('route')
        });

        return {};

    }
}

</script>

<style>
#route
{ 
    height: 800px;
 }
 h3 {
    padding: 1em;
}
</style>