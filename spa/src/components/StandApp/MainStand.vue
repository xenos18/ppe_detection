<template>

  <div class="main_container">
    <div class="data">{{string}}</div>
    <img class="logo" src="@/assets/images/biocad-logo.png"/>
    <!-- <img id="logo" src="@/assets/images/logo.jpg"> -->
    <img id="stream" class="video"/>
    <img id="human" :src="main" class="human"/>
  </div>

</template>

<script>
export default {
  name: "MainStand",
  data() {
    return {
      main: require('@/assets/images/human/00000000.png'),
      socket: null,
      url: null,
      string: 'ТЫц-тыц телевизор'
    }
  },
  mounted() {
    this.connectWebSocket();
  },
  methods: {
    connectWebSocket() {
      this.socket = new WebSocket(process.env.VUE_APP_BACKEND_WS + "stream");
      this.socket.onopen = this.onSocketOpen;
      this.socket.onmessage = this.onSocketMessage;
      this.socket.onclose = this.onSocketClose;
    },
    onSocketOpen() {
      console.log('WebSocket connection established.');
    },
    onSocketMessage(e) {
      if (e.data instanceof Blob) {
        // (window.URL || window.webkitURL).revokeObjectURL(this.url);
        // window.gc && window.gc();
        // // console.log(this.url);
        // this.url = (window.URL || window.webkitURL).createObjectURL(e.data);

        document.getElementById("stream").src = (window.URL || window.webkitURL).createObjectURL(e.data);
        return;
      }

      let data = JSON.parse(e.data);
      if ('edited' in data) {
        console.log(data['edited'])
      }

      if ('form' in data) {
        this.string = data['form']
      }

      if (data["type"] === "detection") {
        let main = ''
        for (const dict of data["humans"]) {
          // eslint-disable-next-line no-unused-vars
          for (const [_, capital] of Object.entries(dict))
            main += capital ? '1' : '0';
          this.main = require('@/assets/images/human/' + main + '.png')
          break
        }
      }
      // data = null;
      // window.gc && window.gc();
    },
    onSocketClose() {
      console.log('WebSocket connection closed. Reconnecting...');
      setTimeout(() => {
        this.connectWebSocket();
      }, 1000); // Пауза 3 секунды перед повторным подключением
    },
  },
};
</script>


<style scoped>
.main_container {
    display: grid;
    align-items: center;
    justify-content: center;
    grid-template-columns: 2fr 1fr;
    grid-template-rows: 2fr 1fr;
    grid-template-areas: "video human"
                         "data logo";
    height: 100vh;
    overflow: hidden;

}

.video {
    grid-area: video;
    width: 85%;
    padding: 5%;
}

.human {
    padding-top: 10px;
    grid-area: human;
    margin: auto;
    display: block;
    max-width: 100%;
    max-height: 70vh;
}

.data{
    grid-area: data;
    display: table-cell;
    vertical-align: middle;
    margin: 10px 10px;
}

.logo{
    grid-area: logo;
    margin: auto;
    display: block;
    max-width: 90%;
}
</style>

<!--.main_container {-->
<!--    display: grid;-->
<!--    align-items: center;-->
<!--    justify-content: center;-->
<!--    grid-template-columns: 2fr 1fr;-->
<!--    grid-template-rows: 2fr 1fr;-->
<!--    grid-template-areas: "video human"-->
<!--                         "data logo";-->
<!--    height: 100vh;-->
<!--    overflow: hidden;-->

<!--}-->

<!--.video {-->
<!--    grid-area: video;-->
<!--    width: 100%;-->
<!--}-->

<!--.human {;-->
<!--    grid-area: human;-->
<!--    margin: auto;-->
<!--    display: block;-->
<!--    max-width: 100%;-->
<!--    max-height: 70vh;-->
<!--}-->

<!--.data{-->
<!--    grid-area: data;-->
<!--    display: table-cell;-->
<!--    vertical-align: middle;-->
<!--    margin: 10px 10px;-->
<!--}-->

<!--.logo{-->
<!--    grid-area: logo;-->
<!--    margin: auto;-->
<!--    display: block;-->
<!--    max-width: 90%;-->
<!--}-->