<template>
    <div id="comp"></div>
</template>

<script>
    import { ref, onMounted } from 'vue';
    import { storeToRefs } from "pinia";
    import { useChartStore } from '/src/stores/useChartStore';

    export default {
        setup(){
            const store = useChartStore();
            onMounted(() => {
                if (! store.comp)
                {
                    let file_name = '/public/worst-performance.json';
                    store.comp = file_name;
                    store.displayComp()
                }
                else {
                    store.displayComp()
                }
            });
        return {};
        }
    }
</script>

<style>

</style>