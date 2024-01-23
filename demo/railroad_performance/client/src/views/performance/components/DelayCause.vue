<template>
    <div id="vis-4"></div>
</template>

<script>
    import { ref, onMounted } from 'vue';
    import { storeToRefs } from "pinia";
    import { useChartStore } from '/src/stores/useChartStore';

    export default {
        setup(){
            const store = useChartStore();
            onMounted(() => {
                if (! store.delaycause)
                {
                    let file_name = '/public/Delay-Cause.json';
                    store.delaycause = file_name;
                    store.displayDelayCause()
                }
                else {
                    store.displayDelayCause()
                }
            });
        return {};
        }
    }
</script>

<style>

</style>