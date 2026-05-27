const fs = require("fs");
const path = require("path");

function loadPptxGen() {
  const bundledRoot = "C:/Users/nithi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
  const pnpmRoot = `${bundledRoot}/.pnpm/node_modules`;
  const Module = require("module");
  process.env.NODE_PATH = [bundledRoot, pnpmRoot, process.env.NODE_PATH || ""]
    .filter(Boolean)
    .join(path.delimiter);
  Module._initPaths();

  try {
    return require("pptxgenjs");
  } catch (err) {
    const bundled = `${bundledRoot}/pptxgenjs`;
    if (fs.existsSync(bundled)) return require(bundled);
    throw err;
  }
}

const pptxgen = loadPptxGen();
const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Codex";
pptx.company = "Smart Hire AI";
pptx.subject = "Face Recognition technical pitch deck";
pptx.title = "Face Recognition System";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  lang: "en-US"
};

const C = {
  navy: "0D1B2A",
  white: "FFFFFF",
  accent: "00C2FF",
  ink: "172033",
  muted: "5D6B7A",
  pale: "EAF7FC",
  line: "BFD7E3",
  good: "2ECC71",
  warn: "F4B942",
  bad: "E74C3C",
  soft: "F4F7FA"
};

const W = 13.333;
const H = 7.5;
const font = "Calibri";
const outFile = path.join(__dirname, "FaceAttendance_Submission.pptx");

function addTitle(slide, title, opts = {}) {
  const color = opts.dark ? C.white : C.navy;
  slide.addText(title, {
    x: 0.55, y: 0.35, w: 12.2, h: 0.5,
    fontFace: font, fontSize: opts.size || 36, bold: true,
    color, margin: 0, breakLine: false,
    fit: "shrink"
  });
}

function addBody(slide, lines, x, y, w, h, color = C.ink, fontSize = 16) {
  slide.addText(lines.map(t => ({ text: t, options: { bullet: { type: "bullet" } } })), {
    x, y, w, h,
    fontFace: font, fontSize,
    color,
    breakLine: false,
    fit: "shrink",
    paraSpaceAfterPt: 6,
    margin: 0.05
  });
}

function addChip(slide, text, x, y, w, fill = C.pale, color = C.navy) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h: 0.38,
    rectRadius: 0.06,
    fill: { color: fill },
    line: { color: fill }
  });
  slide.addText(text, {
    x: x + 0.08, y: y + 0.08, w: w - 0.16, h: 0.18,
    fontFace: font, fontSize: 10, bold: true, color,
    align: "center", margin: 0,
    fit: "shrink"
  });
}

function stat(slide, value, label, x, y, w, color = C.accent) {
  slide.addText(value, {
    x, y, w, h: 0.75,
    fontFace: font, fontSize: 60, bold: true,
    color, margin: 0, align: "center",
    fit: "shrink"
  });
  slide.addText(label, {
    x, y: y + 0.78, w, h: 0.35,
    fontFace: font, fontSize: 14, bold: true,
    color: C.muted, margin: 0, align: "center",
    fit: "shrink"
  });
}

function card(slide, title, body, x, y, w, h, fill = C.soft) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.08,
    fill: { color: fill },
    line: { color: C.line, transparency: 20 }
  });
  slide.addText(title, {
    x: x + 0.18, y: y + 0.16, w: w - 0.36, h: 0.28,
    fontFace: font, fontSize: 15, bold: true,
    color: C.navy, margin: 0, fit: "shrink"
  });
  slide.addText(body, {
    x: x + 0.18, y: y + 0.52, w: w - 0.36, h: h - 0.65,
    fontFace: font, fontSize: 12,
    color: C.ink, margin: 0, fit: "shrink",
    breakLine: false
  });
}

function arrow(slide, x1, y1, x2, y2) {
  slide.addShape(pptx.ShapeType.line, {
    x: x1, y: y1, w: x2 - x1, h: y2 - y1,
    line: { color: C.accent, width: 2, beginArrowType: "none", endArrowType: "triangle" }
  });
}

function footer(slide, n, dark = false) {
  slide.addText(`Smart Hire AI Face Recognition | ${n}/14`, {
    x: 0.55, y: 7.08, w: 12.2, h: 0.2,
    fontFace: font, fontSize: 8,
    color: dark ? "AFC4D4" : "7A8792",
    margin: 0,
    align: "right"
  });
}

function sectionPill(slide, text, dark = false) {
  addChip(slide, text, 0.58, 6.88, 2.4, dark ? "14334A" : C.pale, dark ? C.white : C.navy);
}

// Slide 1
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  s.addShape(pptx.ShapeType.arc, { x: 8.9, y: 0.4, w: 3.8, h: 3.8, line: { color: C.accent, width: 3, transparency: 20 }, adjustPoint: 0.25 });
  s.addShape(pptx.ShapeType.arc, { x: 9.55, y: 1.05, w: 2.5, h: 2.5, line: { color: C.white, width: 1, transparency: 60 }, adjustPoint: 0.35 });
  s.addText("FACE RECOGNITION SYSTEM", { x: 0.72, y: 1.55, w: 8.4, h: 0.58, fontFace: font, fontSize: 40, bold: true, color: C.white, margin: 0, fit: "shrink" });
  s.addText("Local edge AI for real-time identity verification", { x: 0.75, y: 2.28, w: 7.7, h: 0.38, fontFace: font, fontSize: 18, color: "B9D7EA", margin: 0 });
  s.addText("Team: Smart Hire AI\nDate: 27 May 2026", { x: 0.75, y: 5.85, w: 4.0, h: 0.55, fontFace: font, fontSize: 14, color: C.white, margin: 0 });
  stat(s, "LOCAL", "Tkinter + OpenCV + MediaPipe", 8.45, 4.75, 3.7, C.accent);
  footer(s, 1, true);
}

// Slide 2
{
  const s = pptx.addSlide();
  addTitle(s, "Problem Statement");
  card(s, "Identity fraud", "Manual attendance or verification can be bypassed when identity is not checked live.", 0.75, 1.25, 3.7, 2.0);
  card(s, "Connectivity gaps", "The scanned codebase is local-first: webcam, models, and matching run on the desktop.", 4.82, 1.25, 3.7, 2.0);
  card(s, "Spoof risk", "The app requires a blink before match labels are trusted, reducing static photo attempts.", 8.9, 1.25, 3.7, 2.0);
  stat(s, "640x480", "configured camera capture", 0.95, 4.25, 3.2, C.navy);
  stat(s, "5", "frame compare interval", 5.05, 4.25, 2.6, C.navy);
  stat(s, "0.5", "detection confidence", 9.1, 4.25, 2.6, C.navy);
  sectionPill(s, "actual desktop code");
  footer(s, 2);
}

// Slide 3
{
  const s = pptx.addSlide();
  addTitle(s, "Solution Overview");
  s.addShape(pptx.ShapeType.chevron, { x: 0.9, y: 2.0, w: 2.3, h: 1.0, fill: { color: C.pale }, line: { color: C.line } });
  s.addText("Load\nReference", { x: 1.1, y: 2.22, w: 1.75, h: 0.46, fontSize: 17, fontFace: font, bold: true, color: C.navy, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.chevron, { x: 3.65, y: 2.0, w: 2.3, h: 1.0, fill: { color: C.pale }, line: { color: C.line } });
  s.addText("Detect\nFace", { x: 3.88, y: 2.22, w: 1.75, h: 0.46, fontSize: 17, fontFace: font, bold: true, color: C.navy, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.chevron, { x: 6.4, y: 2.0, w: 2.3, h: 1.0, fill: { color: C.pale }, line: { color: C.line } });
  s.addText("Blink\nLiveness", { x: 6.62, y: 2.22, w: 1.75, h: 0.46, fontSize: 17, fontFace: font, bold: true, color: C.navy, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.chevron, { x: 9.15, y: 2.0, w: 2.3, h: 1.0, fill: { color: C.pale }, line: { color: C.line } });
  s.addText("Cosine\nMatch", { x: 9.37, y: 2.22, w: 1.75, h: 0.46, fontSize: 17, fontFace: font, bold: true, color: C.navy, align: "center", margin: 0 });
  addBody(s, [
    "Actual project is a Python desktop app, not React Native.",
    "Models are downloaded or loaded locally from the app folder.",
    "Recognition results are rendered directly into the Tkinter video panel."
  ], 1.1, 4.2, 10.8, 1.0);
  sectionPill(s, "offline local inference");
  footer(s, 3);
}

// Slide 4
{
  const s = pptx.addSlide();
  addTitle(s, "System Architecture");
  const nodes = [
    ["Tkinter UI", 0.8, 1.45],
    ["OpenCV\nWebcam", 0.8, 3.45],
    ["BlazeFace\nDetector", 4.0, 1.45],
    ["FaceLandmarker\nBlink + Align", 4.0, 3.45],
    ["SFace ONNX\nEmbedding", 7.25, 1.45],
    ["Cosine Match\nStatus Overlay", 7.25, 3.45],
    ["Detection Log", 10.45, 2.45]
  ];
  for (const [t, x, y] of nodes) {
    s.addShape(pptx.ShapeType.roundRect, { x, y, w: 2.25, h: 0.92, rectRadius: 0.08, fill: { color: C.pale }, line: { color: C.accent, width: 1.2 } });
    s.addText(t, { x: x + 0.1, y: y + 0.2, w: 2.05, h: 0.42, fontFace: font, fontSize: 14, bold: true, color: C.navy, align: "center", margin: 0, fit: "shrink" });
  }
  arrow(s, 3.05, 1.9, 4.0, 1.9);
  arrow(s, 3.05, 3.9, 4.0, 3.9);
  arrow(s, 6.25, 1.9, 7.25, 1.9);
  arrow(s, 6.25, 3.9, 7.25, 3.9);
  arrow(s, 9.5, 3.9, 10.45, 2.9);
  arrow(s, 1.9, 2.37, 1.9, 3.45);
  arrow(s, 5.1, 2.37, 5.1, 3.45);
  sectionPill(s, "native shape diagram");
  footer(s, 4);
}

// Slide 5
{
  const s = pptx.addSlide();
  addTitle(s, "ML Pipeline: Actual Models");
  card(s, "1. Detect", "MediaPipe BlazeFace short-range\nblaze_face_short_range.tflite\n0.22 MB", 0.8, 1.45, 3.0, 2.0);
  card(s, "2. Liveness + Align", "MediaPipe FaceLandmarker\nface_landmarker.task\n3.58 MB", 4.05, 1.45, 3.0, 2.0);
  card(s, "3. Embed + Match", "OpenCV SFace ONNX\nface_recognition_sface_2021dec.onnx\n36.90 MB", 7.3, 1.45, 3.0, 2.0);
  arrow(s, 3.8, 2.45, 4.05, 2.45);
  arrow(s, 7.05, 2.45, 7.3, 2.45);
  s.addShape(pptx.ShapeType.roundRect, { x: 10.7, y: 1.45, w: 1.85, h: 2.0, rectRadius: 0.08, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("No\nMobileNetV2\nfound", { x: 10.88, y: 1.98, w: 1.48, h: 0.75, fontFace: font, fontSize: 16, bold: true, color: C.white, align: "center", margin: 0, fit: "shrink" });
  stat(s, "40.70 MB", "actual total model artifacts", 1.15, 4.45, 4.0, C.navy);
  stat(s, "0.363", "SFace threshold reference", 5.15, 4.45, 3.4, C.navy);
  stat(s, "99.31%", "LFW accuracy comment", 8.8, 4.45, 3.2, C.navy);
  sectionPill(s, "code-grounded correction");
  footer(s, 5);
}

// Slide 6
{
  const s = pptx.addSlide();
  addTitle(s, "Liveness Detection");
  s.addShape(pptx.ShapeType.flowChartPreparation, { x: 0.95, y: 1.45, w: 2.4, h: 1.0, fill: { color: C.pale }, line: { color: C.accent } });
  s.addText("Open eyes\nEAR > 0.25", { x: 1.15, y: 1.75, w: 2.0, h: 0.38, fontFace: font, fontSize: 15, bold: true, color: C.navy, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.flowChartDecision, { x: 4.25, y: 1.32, w: 2.0, h: 1.25, fill: { color: C.pale }, line: { color: C.accent } });
  s.addText("Blink?\nEAR < 0.20", { x: 4.55, y: 1.74, w: 1.4, h: 0.38, fontFace: font, fontSize: 15, bold: true, color: C.navy, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.flowChartPreparation, { x: 7.15, y: 1.45, w: 2.4, h: 1.0, fill: { color: C.pale }, line: { color: C.accent } });
  s.addText("Tilt guard\nheight > 90%", { x: 7.35, y: 1.75, w: 2.0, h: 0.38, fontFace: font, fontSize: 15, bold: true, color: C.navy, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.flowChartTerminator, { x: 10.1, y: 1.45, w: 2.0, h: 1.0, fill: { color: C.good }, line: { color: C.good } });
  s.addText("LIVE", { x: 10.45, y: 1.78, w: 1.3, h: 0.3, fontFace: font, fontSize: 18, bold: true, color: C.white, align: "center", margin: 0 });
  arrow(s, 3.35, 1.95, 4.25, 1.95);
  arrow(s, 6.25, 1.95, 7.15, 1.95);
  arrow(s, 9.55, 1.95, 10.1, 1.95);
  addBody(s, [
    "Implemented liveness mode: blink only.",
    "Smile and head-turn liveness are not present in the scanned source.",
    "If no face is seen for more than 15 frames, liveness resets."
  ], 1.2, 4.1, 10.8, 1.0);
  sectionPill(s, "blink state machine");
  footer(s, 6);
}

// Slide 7
{
  const s = pptx.addSlide();
  addTitle(s, "Offline Capability");
  s.addShape(pptx.ShapeType.roundRect, { x: 1.0, y: 1.35, w: 2.2, h: 1.4, rectRadius: 0.08, fill: { color: C.pale }, line: { color: C.accent } });
  s.addText("In-memory\nreference embedding", { x: 1.25, y: 1.75, w: 1.7, h: 0.45, fontFace: font, fontSize: 14, bold: true, color: C.navy, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.roundRect, { x: 8.75, y: 1.25, w: 2.4, h: 1.5, rectRadius: 0.08, fill: { color: "F8E9E9" }, line: { color: C.bad } });
  s.addText("SQLite\nnot found", { x: 9.22, y: 1.78, w: 1.4, h: 0.35, fontFace: font, fontSize: 15, bold: true, color: C.bad, align: "center", margin: 0 });
  arrow(s, 3.2, 2.05, 8.75, 2.05);
  addBody(s, [
    "The code is offline in the sense that webcam inference runs locally.",
    "No SQLite schema, database file, or persistence service exists.",
    "The reference face embedding is stored only in process memory."
  ], 1.0, 4.1, 10.9, 1.1);
  sectionPill(s, "local-first, not database-backed");
  footer(s, 7);
}

// Slide 8
{
  const s = pptx.addSlide();
  addTitle(s, "AWS Sync Mechanism");
  card(s, "Queue", "No queue implementation exists in the scanned files.", 0.9, 1.4, 3.1, 1.6, "F8E9E9");
  card(s, "Upload", "No AWS SDK, boto3, HTTP API client, or SyncService exists.", 5.0, 1.4, 3.1, 1.6, "F8E9E9");
  card(s, "Purge", "No purge job, retention task, or cloud deletion flow exists.", 9.1, 1.4, 3.1, 1.6, "F8E9E9");
  arrow(s, 4.0, 2.2, 5.0, 2.2);
  arrow(s, 8.1, 2.2, 9.1, 2.2);
  stat(s, "0", "AWS services found", 1.25, 4.4, 3.2, C.bad);
  stat(s, "0", "SQLite tables found", 5.05, 4.4, 3.2, C.bad);
  stat(s, "0", "service files found", 8.85, 4.4, 3.2, C.bad);
  sectionPill(s, "requested architecture absent");
  footer(s, 8);
}

// Slide 9
{
  const s = pptx.addSlide();
  addTitle(s, "Performance Benchmarks");
  stat(s, "N/A", "latency not measured in code", 0.8, 1.45, 3.0, C.warn);
  stat(s, "36.9 MB", "SFace ONNX model", 4.05, 1.45, 3.5, C.navy);
  stat(s, "99.31%", "accuracy comment for SFace threshold", 8.2, 1.45, 3.7, C.navy);
  s.addShape(pptx.ShapeType.line, { x: 1.0, y: 4.1, w: 10.8, h: 0, line: { color: C.line, width: 1.2 } });
  addBody(s, [
    "Requested < 1 sec latency is not present as a measured benchmark.",
    "Requested < 20 MB model target is not met by the current 36.9 MB SFace ONNX file.",
    "Recognition is throttled to every 5 frames for UI responsiveness."
  ], 1.05, 4.65, 10.8, 1.0);
  sectionPill(s, "constants over claims");
  footer(s, 9);
}

// Slide 10
{
  const s = pptx.addSlide();
  addTitle(s, "Platform Compatibility");
  stat(s, "Python", "desktop app runtime", 0.85, 1.35, 3.2, C.navy);
  stat(s, "3.12-3.14", "README compatibility note", 4.1, 1.35, 3.6, C.navy);
  stat(s, "Tkinter", "native desktop UI", 8.2, 1.35, 3.4, C.navy);
  card(s, "Android 8+", "Not implemented: no React Native Android project found.", 1.0, 4.25, 3.2, 1.15, "F8E9E9");
  card(s, "iOS 12+", "Not implemented: no React Native iOS project found.", 5.05, 4.25, 3.2, 1.15, "F8E9E9");
  card(s, "3GB RAM", "No memory requirement is stated in code or README.", 9.1, 4.25, 3.2, 1.15, "FFF4DA");
  sectionPill(s, "actual compatibility");
  footer(s, 10);
}

// Slide 11
{
  const s = pptx.addSlide();
  addTitle(s, "Open-Source Stack");
  const libs = [
    ["OpenCV contrib", "opencv-contrib-python >= 4.8.0"],
    ["MediaPipe", "mediapipe >= 0.10.0"],
    ["Pillow", "pillow >= 10.0.0"],
    ["NumPy", "numpy >= 1.24.0"],
    ["Tkinter", "Python standard library UI"],
    ["Stdlib", "threading, urllib, datetime, os, sys"]
  ];
  libs.forEach(([a, b], i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    card(s, a, b, 0.85 + col * 4.15, 1.35 + row * 2.0, 3.45, 1.45, row === 0 ? C.pale : C.soft);
  });
  sectionPill(s, "from requirements and imports");
  footer(s, 11);
}

// Slide 12
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  addTitle(s, "Evaluation Scorecard", { dark: true });
  const rows = [
    ["Innovation", "30", "Blink liveness + SFace matching"],
    ["Feasibility", "30", "Runs locally with Python desktop stack"],
    ["Scale", "20", "Needs service, DB, and sync layers for scale"],
    ["Docs", "20", "Grounded documentation generated from code"]
  ];
  s.addShape(pptx.ShapeType.roundRect, { x: 0.9, y: 1.35, w: 11.5, h: 4.4, rectRadius: 0.08, fill: { color: "14334A" }, line: { color: "14334A" } });
  rows.forEach((r, i) => {
    const y = 1.65 + i * 0.92;
    s.addShape(pptx.ShapeType.rect, { x: 1.2, y, w: 10.9, h: 0.68, fill: { color: i % 2 === 0 ? "1B4965" : "173B54" }, line: { color: "1B4965", transparency: 100 } });
    s.addText(r[0], { x: 1.45, y: y + 0.18, w: 2.5, h: 0.22, fontFace: font, fontSize: 15, bold: true, color: C.white, margin: 0 });
    s.addText(r[1], { x: 4.2, y: y + 0.04, w: 1.25, h: 0.46, fontFace: font, fontSize: 28, bold: true, color: C.accent, align: "center", margin: 0 });
    s.addText(r[2], { x: 5.8, y: y + 0.18, w: 5.6, h: 0.24, fontFace: font, fontSize: 14, color: "D7E8F2", margin: 0, fit: "shrink" });
  });
  footer(s, 12, true);
}

// Slide 13
{
  const s = pptx.addSlide();
  addTitle(s, "Demo Flow");
  card(s, "1. Load Reference", "User selects a clear face image. App detects and crops the first face.", 0.75, 1.25, 3.55, 1.55);
  card(s, "2. Start Camera", "OpenCV captures webcam frames and mirrors the live feed.", 4.9, 1.25, 3.55, 1.55);
  card(s, "3. Blink + Match", "Blink liveness gates SFace cosine matching and overlay labels.", 9.05, 1.25, 3.55, 1.55);
  s.addShape(pptx.ShapeType.rect, { x: 0.85, y: 3.55, w: 5.4, h: 2.25, fill: { color: "EEF3F7" }, line: { color: C.line, dash: "dash" } });
  s.addText("Screenshot placeholder\nReference panel + controls", { x: 1.3, y: 4.35, w: 4.5, h: 0.5, fontFace: font, fontSize: 17, bold: true, color: C.muted, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.rect, { x: 7.1, y: 3.55, w: 5.4, h: 2.25, fill: { color: "EEF3F7" }, line: { color: C.line, dash: "dash" } });
  s.addText("Screenshot placeholder\nLive camera overlay", { x: 7.55, y: 4.35, w: 4.5, h: 0.5, fontFace: font, fontSize: 17, bold: true, color: C.muted, align: "center", margin: 0 });
  sectionPill(s, "key user journeys");
  footer(s, 13);
}

// Slide 14
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  s.addShape(pptx.ShapeType.roundRect, { x: 8.7, y: 1.0, w: 2.4, h: 2.1, rectRadius: 0.08, fill: { color: "14334A" }, line: { color: C.accent, width: 2 } });
  s.addText("READY\nFOR\nREVIEW", { x: 9.15, y: 1.45, w: 1.5, h: 0.8, fontFace: font, fontSize: 19, bold: true, color: C.white, align: "center", margin: 0 });
  s.addText("Conclusion", { x: 0.75, y: 1.15, w: 5.5, h: 0.45, fontFace: font, fontSize: 38, bold: true, color: C.white, margin: 0 });
  s.addText("The scanned project is a working local desktop face recognition app with BlazeFace detection, blink liveness, SFace embeddings, and cosine matching. The next architectural step is adding persistence, service APIs, and cloud sync if mobile attendance is required.", {
    x: 0.78, y: 2.1, w: 7.4, h: 1.4,
    fontFace: font, fontSize: 18, color: "D7E8F2",
    margin: 0, fit: "shrink", breakLine: false
  });
  card(s, "Submission files", "technical_documentation.md\npresentation.js\nFaceAttendance_Submission.pptx", 0.85, 4.65, 5.0, 1.35, "14334A");
  s.addText("No React Native, SQLite, AWS SyncService, or MobileNetV2 files were found in the current codebase.", {
    x: 6.45, y: 4.9, w: 5.6, h: 0.55,
    fontFace: font, fontSize: 15, bold: true,
    color: C.accent, margin: 0,
    fit: "shrink"
  });
  footer(s, 14, true);
}

pptx.writeFile({ fileName: outFile });
console.log(`Wrote ${outFile}`);
