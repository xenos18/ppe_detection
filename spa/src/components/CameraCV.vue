<template>
  <img id="stream" style="width: 90%" class="displayed">
  <span id="info"></span>
</template>

<script>
export default {
  name: "CameraCV",
  mounted() {
    this.socket()
  },
  methods: {
    socket() {
      let ws;
      let stream = document.getElementById("stream");
      let info = document.getElementById("info");

      function websocketInit() {
        ws = new WebSocket(process.env.VUE_APP_BACKEND_WS + "stream");
        ws.onopen = () => {
          console.log("WS opened");
        };

        ws.onmessage = (e) => {
          if (e.data instanceof Blob) {
            stream.src = (window.URL || window.webkitURL).createObjectURL(e.data);
            return;
          }

          let data = JSON.parse(e.data);

          if (data["type"] === "detection") {
            info.innerText = JSON.stringify(data["humans"]);
          }
        }

        ws.onclose = (e) => {
          console.log("WS closed", e);
          setTimeout(websocketInit, 1000);
        }
      }

      websocketInit();
    }
  }
}
</script>

<style>
img.displayed {
    display: block;
    margin-left: auto;
    margin-right: auto }
</style>
