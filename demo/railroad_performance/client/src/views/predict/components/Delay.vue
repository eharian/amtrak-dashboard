<template>
  <div class="container">
   
   <p v-if="ans.delay"> 
        <p> Linear Regression plot: </p>
        <img :src="ans.delay" > 
        <p> Predicted delay: 30 minutes </p>
    </p>

    <p v-else> 
        <p> Linear Regression plot: </p>
        <img src="/src/assets/images/1.png" > 
        <p> Predicted delay: 20 minutes </p>
    </p>

    <p> You can enter: 14, LAX, SLO, 40 for now. In the future we can make this more descriptive"</p>
    <form @submit.prevent="onSubmit">
        <input v-model="getDelay.train_id" placeholder="Train Id">
        <input v-model="getDelay.source" placeholder="Source">
        <input v-model="getDelay.dest" placeholder="Destination">
        <input v-model="getDelay.delay_time" placeholder="Delay Time">
        <button>Get Delay</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';


export default {
  name: 'Delay',
  data() {
    return {
      msg: '',
      ans: '',
      getDelay: {
        train_id: ' ',
        source: ' ',
        dest: ' ',
        delay_time: ' ',
      },
    };
  },
  methods: {
    getMessage() {
      const path = 'http://127.0.0.1:5000/delay';
      axios.get(path)
        .then((res) => {
          this.msg = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    computeDelay(payload){
        const path = 'http://127.0.0.1:5000/delay';
        axios.post(path, payload)
            .then((res) => {
                this.ans = res.data
                this.getMessage();
            })
            .catch((error) => {
                console.log(error);
                this.getMessage();
            });
    },
    initForm() {
        this.getDelay.train_id = '';
        this.getDelay.source = '';
        this.getDelay.dest = '';
        this.getDelay.delay_time = ''; 
    },
    onSubmit() {
        const payload = {
            train_id: this.getDelay.train_id,
            source: this.getDelay.source,
            dest: this.getDelay.dest,
            delay_time: this.getDelay.delay_time,
        };
        this.computeDelay(payload)
        this.initForm();
    }
  },
  created() {
    this.getMessage();
  },
};
</script>