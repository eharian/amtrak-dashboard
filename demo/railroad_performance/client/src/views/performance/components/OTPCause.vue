<template>
    <div id="vis-2"></div>
</template>

<script>
    import { ref, onMounted } from 'vue';
    import { storeToRefs } from "pinia";
    import { useChartStore } from '/src/stores/useChartStore';

    export default {
        setup(){
            const store = useChartStore();
            onMounted(() => {
                if (! store.otpcause)
                {
                    let file_name = '/public/OPT-Cause.json';
                    store.otpcause = file_name;
                    store.displayOTPCause()
                }
                else
                {
                    store.displayOTPCause()
                }
            });
        return {};
        }
    }
</script>

<style>

</style>