let ws;
let stream = document.getElementById("stream");
let info = document.getElementById("human");

function websocketInit() {
    ws = new WebSocket("ws://0.0.0.0:8500/stream");
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
            let main = ''
            for (const dict of data["humans"]) {
               for (const [_, capital] of Object.entries(dict))
                   main += capital ? '1' : '0';
               info.src = 'http://127.0.0.1:8500/static/images/' + main + '.png';
               break
            }
        }
    }

    ws.onclose = (e) => {
        console.log("WS closed", e);
        setTimeout(websocketInit, 1000);
    }
}

websocketInit();