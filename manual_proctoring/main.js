const { app, BrowserWindow, ipcMain } = require("electron");
const { execFile } = require("child_process");
const fs = require("fs");
const path = require("path");

let mainWindow;
let monitoringInterval = null;

const BLOCKED_APPS_CONFIG_PATH = path.join(__dirname, "config", "blocked-network-apps.json");
const FALLBACK_BLOCKED_NETWORK_APPS = [
 "arc.exe",
 "brave.exe",
 "chrome.exe",
 "discord.exe",
 "element.exe",
 "firefox.exe",
 "iexplore.exe",
 "line.exe",
 "microsoftedge.exe",
 "msedge.exe",
 "opera.exe",
 "opera_gx.exe",
 "pidgin.exe",
 "qutebrowser.exe",
 "signal.exe",
 "skype.exe",
 "slack.exe",
 "teams.exe",
 "teamsclassic.exe",
 "telegram.exe",
 "vivaldi.exe",
 "wechat.exe",
 "whatsapp.exe",
 "zoom.exe"
];

function loadBlockedNetworkApps() {
 try {
  const rawConfig = fs.readFileSync(BLOCKED_APPS_CONFIG_PATH, "utf8");
  const parsedConfig = JSON.parse(rawConfig);

  if (!Array.isArray(parsedConfig)) {
   throw new Error("Blocked network apps config must be an array.");
  }

  const normalizedApps = parsedConfig
   .map(entry => String(entry || "").trim().toLowerCase())
   .filter(Boolean);

  if (normalizedApps.length === 0) {
   throw new Error("Blocked network apps config is empty.");
  }

  return normalizedApps;
 } catch (error) {
  console.error("Failed to load blocked network apps config, using fallback list:", error.message);
  return FALLBACK_BLOCKED_NETWORK_APPS;
 }
}

function runProcessCommand(file, args = []) {
 return new Promise(resolve => {
  execFile(file, args, { windowsHide: true }, (error, stdout = "") => {
   if (error) {
    resolve("");
    return;
   }

   resolve(stdout);
  });
 });
}

async function scanAndBlockNetworkApps() {
 const blockedNetworkApps = loadBlockedNetworkApps();
 const taskListOutput = await runProcessCommand("tasklist", ["/FO", "CSV", "/NH"]);

 if (!taskListOutput) {
  return;
 }

 const detectedApps = new Set();
 const lines = taskListOutput
  .split(/\r?\n/)
  .map(line => line.trim())
  .filter(Boolean);

 for (const line of lines) {
  const match = line.match(/^"([^"]+)"/);

  if (!match) {
   continue;
  }

  const processName = match[1].toLowerCase();

  if (!blockedNetworkApps.includes(processName)) {
   continue;
  }

  detectedApps.add(processName);
  await runProcessCommand("taskkill", ["/IM", processName, "/F"]);
 }

 if (detectedApps.size > 0 && mainWindow && !mainWindow.isDestroyed()) {
  mainWindow.webContents.send("network-app-blocked", Array.from(detectedApps));
 }
}

function startExamMonitoring() {
 stopExamMonitoring();
 monitoringInterval = setInterval(scanAndBlockNetworkApps, 2000);
 scanAndBlockNetworkApps();
}

function stopExamMonitoring() {
 if (!monitoringInterval) {
  return;
 }

 clearInterval(monitoringInterval);
 monitoringInterval = null;
}

function createWindow(){

 mainWindow = new BrowserWindow({
  width:1200,
  height:800,
  autoHideMenuBar:true,
  webPreferences:{
   preload:path.join(__dirname,"preload.js"),
   contextIsolation:true
  }
 });

 mainWindow.loadFile(path.join(__dirname, "renderer", "login.html"));

}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
 if (process.platform !== "darwin") {
  app.quit();
 }
});

app.on("activate", () => {
 if (BrowserWindow.getAllWindows().length === 0) {
  createWindow();
 }
});


// START FULLSCREEN WHEN EXAM STARTS
ipcMain.on("start-fullscreen",()=>{

 mainWindow.setFullScreen(true);
 mainWindow.setKiosk(true);

});

ipcMain.on("exit-fullscreen",()=>{

 if (!mainWindow) {
  return;
 }

 stopExamMonitoring();
 mainWindow.setKiosk(false);
 mainWindow.setFullScreen(false);

});

ipcMain.on("start-exam-monitoring", () => {
 startExamMonitoring();
});

ipcMain.on("stop-exam-monitoring", () => {
 stopExamMonitoring();
});

app.on("browser-window-created", (_, window) => {
 window.on("leave-full-screen", () => {
  window.webContents.send("fullscreen-exited");
 });
});

app.on("before-quit", () => {
 stopExamMonitoring();
});
