<template>

  <div class="main_container">
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
        document.getElementById("stream").src = (window.URL || window.webkitURL).createObjectURL(e.data);
        return;
      }

      let data = JSON.parse(e.data);

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
  grid-template-areas:
        "video human";
  height: 95vh;
  overflow: hidden;

}

.video {
  grid-area: video;
  width: 100%;
}

.human {;
  grid-area: human;
  margin: auto;
  display: block;
  max-width: 100%;
  max-height: 75vh;
  width: auto;
  height: auto;
  /*width: 100%;*/
  /*height: 90vh;*/

}
</style>