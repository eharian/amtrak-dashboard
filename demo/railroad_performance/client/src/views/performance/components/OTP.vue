<template>
    <div id="vis"></div>
</template>

<script>
    import { ref, onMounted } from 'vue';
    import { storeToRefs } from "pinia";
    import { useChartStore } from '/src/stores/useChartStore';

    export default {
        setup(){
            const store = useChartStore();
            onMounted(() => {
                if (! store.otp)
                {
                    let file_name = '/public/OTP.csv';
                    store.otp = file_name;
                    store.displayOTP()
                }
                else {
                    store.displayOTP()
                }
            });
        return {};
        }
    }
</script>

<style>

</style>