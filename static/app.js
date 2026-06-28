const state = {
  sessionId: null,
  analysis: null,
  strategies: [],
  selectedStrategy: "auto",
  customBackend: null,
  resultReady: false,
};

const els = {
  dropzone: document.getElementById("dropzone"),
  fileInput: document.getElementById("fileInput"),
  fileMeta: document.getElementById("fileMeta"),
  analysisStats: document.getElementById("analysisStats"),
  toggleWhy: document.getElementById("toggleWhy"),
  whyBox: document.getElementById("whyBox"),
  strategyGrid: document.getElementById("strategyGrid"),
  recommendationHero: document.getElementById("recommendationHero"),
  customSelectWrap: document.getElementById("customSelectWrap"),
  customSelect: document.getElementById("customSelect"),
  selectionNote: document.getElementById("selectionNote"),
  runButton: document.getElementById("runButton"),
  resultBanner: document.getElementById("resultBanner"),
  matchingBody: document.getElementById("matchingBody"),
  checksBody: document.getElementById("checksBody"),
  courseBody: document.getElementById("courseBody"),
  summaryBox: document.getElementById("summaryBox"),
  exportButton: document.getElementById("exportButton"),
};

function setFileMeta(message, good = false) {
  els.fileMeta.innerHTML = `<span class="meta-pill">${good ? "Uploaded:" : ""} ${message}</span>`;
}

function renderStats(analysis) {
  const items = [
    ["Courses", analysis.num_courses],
    ["TAs", analysis.num_tas],
    ["Total Slots", analysis.total_slots],
    ["Active Links", analysis.positive_pairs],
    ["Avg TA Choices", analysis.avg_ta_degree],
    ["Matrix Density", `${analysis.density}%`],
  ];

  els.analysisStats.innerHTML = items
    .map(([label, value]) => `
      <div class="meta-chip">
        <span class="label">${label}</span>
        <span class="value">${value}</span>
      </div>
    `)
    .join("");
}

function renderRecommendation(analysis) {
  els.recommendationHero.innerHTML = `
    <h3>${analysis.recommendation_text}</h3>
    <p>${analysis.insights.join(" ")}</p>
  `;
  els.whyBox.innerHTML = analysis.why_lines.map(line => `<div>• ${line}</div>`).join("");
  els.toggleWhy.disabled = false;
}

function renderCustomChoices(choices) {
  els.customSelect.innerHTML = choices
    .map(choice => `<option value="${choice.value}">${choice.label}</option>`)
    .join("");
  state.customBackend = els.customSelect.value;
}

function renderStrategies() {
  els.strategyGrid.innerHTML = state.strategies.map((strategy) => {
    const recommended = state.analysis?.recommended_strategy === strategy.id;
    const selected = state.selectedStrategy === strategy.id;
    return `
      <article class="strategy-card ${recommended ? "recommended" : ""} ${selected ? "selected" : ""}" data-strategy="${strategy.id}">
        <div class="icon">${strategy.icon}</div>
        <div>
          <h3>${strategy.title}</h3>
          <p class="helper">${strategy.description}</p>
        </div>
        <div class="right">
          <p class="mini-tip">${strategy.tooltip}</p>
          <span class="badge tone-${strategy.tone}">${recommended ? "Recommended" : strategy.badge}</span>
        </div>
      </article>
    `;
  }).join("");
}

function updateSelectionUI() {
  renderStrategies();
  const chosen = state.strategies.find((item) => item.id === state.selectedStrategy);
  if (chosen) {
    els.selectionNote.textContent = chosen.description;
  }
  els.customSelectWrap.classList.toggle("hidden", state.selectedStrategy !== "custom");
}

async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  setFileMeta("Uploading and analyzing...");
  els.runButton.disabled = true;
  els.exportButton.classList.add("disabled");

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: formData,
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Upload failed.");
    }

    state.sessionId = payload.session_id;
    state.analysis = payload.analysis;
    state.strategies = payload.strategies;
    state.selectedStrategy = payload.analysis.recommended_strategy || "auto";
    renderStats(payload.analysis);
    renderRecommendation(payload.analysis);
    renderCustomChoices(payload.custom_choices);
    updateSelectionUI();

    setFileMeta(payload.filename, true);
    els.runButton.disabled = false;
    els.resultBanner.className = "result-banner idle";
    els.resultBanner.textContent = "File analyzed successfully. Review the recommendation and click Run Matching.";
  } catch (error) {
    setFileMeta(error.message);
    els.resultBanner.className = "result-banner error";
    els.resultBanner.textContent = error.message;
  }
}

function renderMatchingRows(rows) {
  if (!rows.length) {
    els.matchingBody.innerHTML = `<tr><td colspan="2" class="empty-cell">No result yet</td></tr>`;
    return;
  }

  els.matchingBody.innerHTML = rows.map(row => `
    <tr>
      <td>${row.ta}</td>
      <td>${row.course}</td>
    </tr>
  `).join("");
}

function renderChecks(checks) {
  if (!checks.length) {
    els.checksBody.innerHTML = `<tr><td colspan="3" class="empty-cell">No checks available</td></tr>`;
    return;
  }

  els.checksBody.innerHTML = checks.map(check => `
    <tr>
      <td>${check.name}</td>
      <td><span class="status-pill ${check.passed ? "status-pass" : "status-fail"}">${check.passed ? "PASS" : "FAIL"}</span></td>
      <td>${check.message}</td>
    </tr>
  `).join("");
}

function renderCourseSummary(rows) {
  if (!rows.length) {
    els.courseBody.innerHTML = `<tr><td colspan="5" class="empty-cell">No course summary yet</td></tr>`;
    return;
  }

  els.courseBody.innerHTML = rows.map(row => `
    <tr>
      <td>${row.course}</td>
      <td>${row.capacity}</td>
      <td>${row.assigned_tas}</td>
      <td>${row.avg_util}</td>
      <td><span class="status-pill ${row.meets_threshold ? "status-pass" : "status-fail"}">${row.meets_threshold ? "YES" : "NO"}</span></td>
    </tr>
  `).join("");
}

async function runMatching() {
  if (!state.sessionId) return;

  els.runButton.disabled = true;
  els.runButton.textContent = "Running...";
  els.resultBanner.className = "result-banner idle";
  els.resultBanner.textContent = "Matching is running. Please wait...";

  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: state.sessionId,
        strategy: state.selectedStrategy,
        custom_backend: state.selectedStrategy === "custom" ? els.customSelect.value : null,
      }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Run failed.");
    }

    renderMatchingRows(payload.matching_rows);
    renderChecks(payload.checks);
    renderCourseSummary(payload.course_summary);
    els.summaryBox.textContent = payload.summary_text || "No run summary available.";
    els.resultBanner.className = `result-banner ${payload.ok ? "success" : "error"}`;
    els.resultBanner.textContent = payload.verdict;

    state.resultReady = true;
    if (payload.ok) {
      els.exportButton.href = `/api/export/${state.sessionId}`;
      els.exportButton.classList.remove("disabled");
    } else {
      els.exportButton.href = "#";
      els.exportButton.classList.add("disabled");
    }
  } catch (error) {
    els.resultBanner.className = "result-banner error";
    els.resultBanner.textContent = error.message;
  } finally {
    els.runButton.disabled = false;
    els.runButton.textContent = "Run Matching";
  }
}

els.dropzone.addEventListener("click", () => els.fileInput.click());
els.fileInput.addEventListener("change", (event) => {
  const file = event.target.files?.[0];
  if (file) uploadFile(file);
});

["dragenter", "dragover"].forEach((eventName) => {
  els.dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    els.dropzone.classList.add("dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  els.dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    els.dropzone.classList.remove("dragging");
  });
});

els.dropzone.addEventListener("drop", (event) => {
  const file = event.dataTransfer?.files?.[0];
  if (file) uploadFile(file);
});

els.toggleWhy.addEventListener("click", () => {
  els.whyBox.classList.toggle("hidden");
  els.toggleWhy.textContent = els.whyBox.classList.contains("hidden")
    ? "Why this recommendation?"
    : "Hide recommendation details";
});

els.strategyGrid.addEventListener("click", (event) => {
  const card = event.target.closest(".strategy-card");
  if (!card) return;
  state.selectedStrategy = card.dataset.strategy;
  updateSelectionUI();
});

els.customSelect.addEventListener("change", () => {
  state.customBackend = els.customSelect.value;
});

els.runButton.addEventListener("click", runMatching);
