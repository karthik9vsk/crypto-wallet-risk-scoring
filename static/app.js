const payloadInput = document.getElementById("payloadInput");
const loadSampleBtn = document.getElementById("loadSampleBtn");
const copyPayloadBtn = document.getElementById("copyPayloadBtn");
const predictBtn = document.getElementById("predictBtn");
const clearBtn = document.getElementById("clearBtn");
const statusBar = document.getElementById("statusBar");

const scoreValue = document.getElementById("scoreValue");
const progressFill = document.getElementById("progressFill");
const riskLabel = document.getElementById("riskLabel");
const predictionMeta = document.getElementById("predictionMeta");
const signalsList = document.getElementById("signalsList");
const summaryBox = document.getElementById("summaryBox");
const sourceBadge = document.getElementById("sourceBadge");
const copySummaryBtn = document.getElementById("copySummaryBtn");

function setStatus(message, type = "") {
  statusBar.textContent = message;
  statusBar.className = `status-bar ${type}`.trim();
  statusBar.classList.remove("hidden");
}

function clearStatus() {
  statusBar.className = "status-bar hidden";
  statusBar.textContent = "";
}

function setRiskUI(probability, prediction) {
  const percent = Math.round(probability * 100);
  scoreValue.textContent = `${percent}%`;
  progressFill.style.width = `${percent}%`;
  predictionMeta.textContent = `Prediction: ${prediction === 1 ? "Fraudulent" : "Non-Fraudulent"}`;

  riskLabel.classList.remove("low", "medium", "high", "neutral");

  if (probability >= 0.8) {
    riskLabel.textContent = "High Risk";
    riskLabel.classList.add("high");
  } else if (probability >= 0.5) {
    riskLabel.textContent = "Medium Risk";
    riskLabel.classList.add("medium");
  } else {
    riskLabel.textContent = "Low Risk";
    riskLabel.classList.add("low");
  }
}

function renderSignals(signals = []) {
  signalsList.innerHTML = "";

  if (!signals.length) {
    const li = document.createElement("li");
    li.className = "placeholder";
    li.textContent = "No dominant suspicious indicators were returned.";
    signalsList.appendChild(li);
    return;
  }

  for (const signal of signals) {
    const li = document.createElement("li");
    li.textContent = signal;
    signalsList.appendChild(li);
  }
}

function resetOutput() {
  scoreValue.textContent = "--";
  progressFill.style.width = "0%";
  riskLabel.textContent = "Not analyzed";
  riskLabel.className = "risk-label neutral";
  predictionMeta.textContent = "Prediction: --";
  summaryBox.textContent = "Run an analysis to generate a summary.";
  sourceBadge.textContent = "Awaiting analysis";
  renderSignals([]);
}

async function loadSample() {
  clearStatus();
  try {
    const res = await fetch("/sample-payload");
    if (!res.ok) {
      throw new Error("Failed to load sample payload.");
    }
    const data = await res.json();
    payloadInput.value = JSON.stringify(data, null, 2);
    setStatus("Sample payload loaded.", "success");
  } catch (error) {
    setStatus(error.message || "Unable to load sample payload.", "error");
  }
}

async function analyzeWallet() {
  clearStatus();

  let payload;
  try {
    payload = JSON.parse(payloadInput.value);
  } catch {
    setStatus("Payload is not valid JSON.", "error");
    return;
  }

  predictBtn.disabled = true;
  predictBtn.textContent = "Analyzing...";

  try {
    const res = await fetch("/explain", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Analysis failed.");
    }

    setRiskUI(data.fraud_probability, data.prediction);
    renderSignals(data.top_signals || []);
    summaryBox.textContent = data.analyst_summary || "No summary returned.";
    sourceBadge.textContent =
      data.summary_source === "llm" ? "AI Summary" : "Rule-Based Summary";

    setStatus("Analysis completed successfully.", "success");
  } catch (error) {
    setStatus(error.message || "Unable to analyze wallet.", "error");
  } finally {
    predictBtn.disabled = false;
    predictBtn.textContent = "Analyze Wallet";
  }
}

function clearAll() {
  payloadInput.value = "";
  clearStatus();
  resetOutput();
}

async function copyPayload() {
  try {
    await navigator.clipboard.writeText(payloadInput.value);
    setStatus("Payload copied.", "success");
  } catch {
    setStatus("Unable to copy payload.", "error");
  }
}

async function copySummary() {
  try {
    await navigator.clipboard.writeText(summaryBox.textContent);
    setStatus("Summary copied.", "success");
  } catch {
    setStatus("Unable to copy summary.", "error");
  }
}

loadSampleBtn.addEventListener("click", loadSample);
predictBtn.addEventListener("click", analyzeWallet);
clearBtn.addEventListener("click", clearAll);
copyPayloadBtn.addEventListener("click", copyPayload);
copySummaryBtn.addEventListener("click", copySummary);

resetOutput();