const { spawn } = require("child_process");
const path = require("path");

const electronBinary = path.join(
  __dirname,
  "..",
  "node_modules",
  "electron",
  "dist",
  process.platform === "win32" ? "electron.exe" : "electron"
);

const environment = { ...process.env };
delete environment.ELECTRON_RUN_AS_NODE;

const child = spawn(electronBinary, ["."], {
  cwd: path.join(__dirname, ".."),
  stdio: "inherit",
  env: environment
});

child.on("exit", code => {
  process.exit(code ?? 0);
});

child.on("error", error => {
  console.error("Failed to launch Electron:", error.message);
  process.exit(1);
});
