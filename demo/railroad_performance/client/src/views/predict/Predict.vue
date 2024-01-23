<template>
    <div class="predict">
        <h3> Get predicted delay </h3>
        <p> Enter train id, Source, Destination, Delay at Source</p>

        <Delay />
    </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import Delay from './components/Delay.vue';

export default {
    components: {
      Delay
    },
    setup() {
        return { };
    }, 

}
</script>

<style>
.predict{
    padding: 2em;
}
p{
    padding: 0, 2em;
}
</style>