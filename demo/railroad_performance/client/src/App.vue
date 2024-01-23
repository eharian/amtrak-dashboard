<script setup>
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
<div class="nav_position">
  <nav class="navbar navbar-horizontal navbar-light bg-light navbar-expand-md" id="nav">
    <a href="#" class="navbar-brand" target="_self"><span class="header-title">Amtrak Performance Visualization</span></a>
    <RouterLink class="route" to="/route">Route Analysis</RouterLink>
    <RouterLink class="route" to="/station">Station Analysis</RouterLink>
    <RouterLink class="route" to="/performance">Performance Analysis</RouterLink>
    <RouterLink class="route" to="/plan">Station Planning</RouterLink>
    <RouterLink class="route" to="/predict">Predictive Analysis</RouterLink>
  </nav>
</div>
 
  <!--<header>
    <nav>
        
    </nav>
  </header>-->

  <RouterView />
</template>

<style>
#nav {
    border-bottom: 1px solid #d3d3d3;
}
.bg-light {
    background-color: #f8f9fa!important;
}
.nav_position {
    grid-row: 1/2;
    position: sticky;
    top: 0;
    z-index: 401;
}
.navbar-brand
{
  margin-right: 25% !important;
  margin-left: 10px;
}
.route{
  margin: 0 10px;
}
a.route {
    color: black;
    text-decoration: none;
}
a.router-link-active.router-link-exact-active.route {
    border-bottom: 3px solid #265acc;
}
</style>