<template>
<div class="notes">
    <p>Here we can see Amtrak's On time performance. It is clear that the worst performance is seen in the Long distance trains. </p>
    <p> A comparison of the Northbound and Southbound OTP of a long distance train can be seen here. The northbound OTP's are significantly low. </p>
    <p> It is clear that if Amtrak can improve it's OTP, it would lead to a significant increase in revenue in terms of sales and reduced cost </p>
    <p> We have also analyzed the contribution of different causes that leads to delays in Amtrak. Significant contribution is from host railway interference. However, if ontime performance was increased, it would still lead to a more lucrative business. </p> 
</div>
    <table style="border: 1px solid black;">
    <tr>
        <td ><OTP /></td>
        <td><Comparison /></td>
    </tr>
    <tr>
        <td><OTPCause /></td>
        <td><DelayCause /></td>
    </tr>
    </table>
</template>

<script>
import OTP from './components/OTP.vue';
import OTPCause from './components/OTPCause.vue';
import Comparison from './components/Comparison.vue';
import DelayCause from './components/DelayCause.vue';

    export default {
        components: {
            OTP,
            OTPCause,
            Comparison,
            DelayCause
        },
        setup() {
            return {};
        }
        
    }

</script>

<style>
.reason{
    margin: 0 25%;
}
.notes {
    padding: 2em;
}
</style>