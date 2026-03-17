const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI",{

 startFullscreen:()=>ipcRenderer.send("start-fullscreen"),
 exitFullscreen:()=>ipcRenderer.send("exit-fullscreen"),
 startExamMonitoring:()=>ipcRenderer.send("start-exam-monitoring"),
 stopExamMonitoring:()=>ipcRenderer.send("stop-exam-monitoring"),
 onFullscreenExited:(callback)=>ipcRenderer.on("fullscreen-exited", callback),
 onNetworkAppBlocked:(callback)=>ipcRenderer.on("network-app-blocked", (_, processes) => callback(processes))

});
