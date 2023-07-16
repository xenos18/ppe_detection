let ws;
let stream = document.getElementById("stream");
let info = document.getElementById("info");

function websocketInit() {
    ws = new WebSocket("ws://localhost:8000/stream");
    ws.onopen = (e) => {
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