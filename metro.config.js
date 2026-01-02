const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");
const path = require("path");

// Fix for Windows ESM loader issue
const projectRoot = __dirname;
const config = getDefaultConfig(projectRoot);

// Add .tflite to asset extensions
if (!config.resolver.assetExts.includes("tflite")) {
  config.resolver.assetExts.push("tflite");
}

// Ensure .tflite is NOT in sourceExts
config.resolver.sourceExts = config.resolver.sourceExts.filter(ext => ext !== "tflite");

module.exports = withNativeWind(config, {
  input: "./global.css",
  forceWriteFileSystem: true,
});
