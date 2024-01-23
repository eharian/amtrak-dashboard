<template>
  <div id="route-map">
        <RouteMap />
  </div>
  <div id="line-delay">
        <LineDelay />
  </div>
</template>

<script>
import RouteMap from './components/RouteMap.vue';
import LineDelay from './components/LineDelay.vue';


export default {
    components: {
      RouteMap,
      LineDelay
    },
    setup() {
        return { };
    }, 

}
</script>

<style>
#route-map{
  padding: 2em;
}
</style>