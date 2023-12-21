const video = document.getElementById('live-video');
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
    console.log('WebSocket connection opened');
};

ws.onmessage = (event) => {
    
    let isScreenData = event.data.slice(0,11) == "frame_data:" 
    
    if (isScreenData){
        const frameBase64 = event.data.substring(11, event.data.length);
        const binaryData = atob(frameBase64);

        const arrayBuffer = new ArrayBuffer(binaryData.length);
        const uint8Array = new Uint8Array(arrayBuffer);
    
        for (let i = 0; i < binaryData.length; i++) {
            uint8Array[i] = binaryData.charCodeAt(i);
        }
    
        const blob = new Blob([uint8Array], { type: 'image/jpeg' });
        console.log(blob)
        const objectURL = URL.createObjectURL(blob);
        video.src = objectURL;
    }
     
};

ws.onclose = () => {
    console.log('WebSocket connection closed');
};

ws.onerror = (error) => {
    console.error(`WebSocket error: ${error}`);
};
