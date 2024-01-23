<template>
    <div id="station"></div>
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
            store.loadStationData('station')
            store.createMap('station')
        });

        return {};

    }
}

</script>

<style>
#station
{ 
   
    height: 800px;
 }
</style>