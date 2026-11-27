// Parameter explorer (D6, D8). GENERATED SITE ASSET: edit src/aiwelfare/site_assets/explorer.js.
//
// This script computes nothing itself (D10). It loads Pyodide, copies the repository's own
// Python files (engine, explorer, models) into it, and asks aiwelfare.explorer for the chart.
// It only builds controls from data/spec.json and keeps the page address in step with them.
"use strict";

(async function () {
  const $ = (id) => document.getElementById(id);
  const status = $("status");
  const spec = await (await fetch("data/spec.json")).json();
  let state = { counterfactual: spec.default_counterfactual, settings: {}, filters: [] };
  let py = null;

  if (location.search.length > 1) {
    status.textContent =
      "Loading your settings from the page address. Until Python has loaded, the chart below " +
      "is the canonical default, not your settings.";
    status.classList.add("warn");
  }

  // ---- controls built from the models' declared parameters ------------------------------

  const sig3 = (v) => Number(Number(v).toPrecision(3));
  const toValue = (p, pos) => {
    const t = pos / 200;
    return sig3(p.log ? p.min * Math.pow(p.max / p.min, t) : p.min + (p.max - p.min) * t);
  };
  const toPos = (p, v) => {
    const t = p.log ? Math.log(v / p.min) / Math.log(p.max / p.min) : (v - p.min) / (p.max - p.min);
    return Math.round(200 * Math.min(1, Math.max(0, t)));
  };
  const show = (v) => (Math.abs(v) >= 1e4 || (v !== 0 && Math.abs(v) < 1e-3) ? v.toExponential(2) : String(v));

  function paramControl(card, p, i) {
    const div = document.createElement("div");
    div.className = "param";
    div.dataset.risk = card.risk;
    div.dataset.param = p.name;
    const swing = p.swing == null ? "" : ` · crux swing ×${Number(p.swing).toPrecision(2)}`;
    const meta = `<small>Default: full distribution (${p.distribution}) · evidence basis: ${p.basis}${swing} · claims: ${p.claims.join(", ")}</small>`;
    if (p.categorical) {
      const opts = ['<option value="">Mixed, equal weight (default, D14)</option>']
        .concat(p.categories.map((c) => `<option value="${c}">${c} only</option>`)).join("");
      div.innerHTML = `<label>${i < 3 ? "★ " : ""}<code>${p.name}</code>: ${p.description}</label>
        <select disabled>${opts}</select>${meta}`;
      div.querySelector("select").addEventListener("change", (e) => setParam(card.risk, p.name, e.target.value || null));
    } else {
      div.innerHTML = `<label>${i < 3 ? "★ " : ""}<code>${p.name}</code>: ${p.description}</label>
        <span class="fix"><label><input type="checkbox" disabled> fix at</label>
        <input type="range" min="0" max="200" step="1" disabled value="${toPos(p, p.median)}">
        <output>${show(sig3(p.median))}</output></span>${meta}`;
      const box = div.querySelector("input[type=checkbox]");
      const range = div.querySelector("input[type=range]");
      const out = div.querySelector("output");
      range.addEventListener("input", () => { out.textContent = show(toValue(p, range.value)); });
      range.addEventListener("change", () => { if (box.checked) setParam(card.risk, p.name, String(toValue(p, range.value))); });
      box.addEventListener("change", () => setParam(card.risk, p.name, box.checked ? String(toValue(p, range.value)) : null));
    }
    return div;
  }

  const sliders = $("sliders");
  if (spec.cards.length) {
    sliders.innerHTML = "<h2>Change the assumptions</h2><p class='small'>Parameters come from each " +
      "model's declarations, the largest cruxes first (★ = top three, from <code>aiwelfare cruxes</code>). " +
      "Fixing a parameter is what <code>aiwelfare whatif --set</code> does: every simulated future uses that value.</p>";
  }
  spec.cards.forEach((card, k) => {
    const d = document.createElement("details");
    d.open = k === 0;
    d.innerHTML = `<summary>${card.title}</summary>`;
    const more = document.createElement("details");
    more.innerHTML = "<summary>More parameters</summary>";
    card.params.forEach((p, i) => (i < 3 ? d : more).appendChild(paramControl(card, p, i)));
    if (card.params.length > 3) d.appendChild(more);
    sliders.appendChild(d);
  });

  document.querySelectorAll("input[name=cf]").forEach((el) =>
    el.addEventListener("change", () => { state.counterfactual = el.value; render(); }));
  document.querySelectorAll("input[name=filter]").forEach((el) =>
    el.addEventListener("change", () => {
      state.filters = [...document.querySelectorAll("input[name=filter]:checked")].map((x) => x.value);
      render();
    }));

  function setParam(risk, name, value) {
    const s = (state.settings[risk] = state.settings[risk] || {});
    if (value === null) delete s[name]; else s[name] = value;
    render();
  }

  function syncControls() {
    document.querySelectorAll("input[name=cf]").forEach((el) => (el.checked = el.value === state.counterfactual));
    document.querySelectorAll("input[name=filter]").forEach((el) => (el.checked = state.filters.includes(el.value)));
    document.querySelectorAll(".param").forEach((div) => {
      const card = spec.cards.find((c) => c.risk === div.dataset.risk);
      const p = card.params.find((x) => x.name === div.dataset.param);
      const v = (state.settings[card.risk] || {})[p.name];
      if (p.categorical) { div.querySelector("select").value = v || ""; return; }
      div.querySelector("input[type=checkbox]").checked = v !== undefined;
      if (v !== undefined) {
        div.querySelector("input[type=range]").value = toPos(p, Number(v));
        div.querySelector("output").textContent = show(Number(v));
      }
    });
  }

  // ---- talking to Python ---------------------------------------------------------------

  function query() {
    const parts = [];
    if (state.counterfactual !== spec.default_counterfactual) parts.push(["cf", state.counterfactual]);
    for (const [r, ps] of Object.entries(state.settings))
      for (const [k, v] of Object.entries(ps)) parts.push([`${r}.${k}`, v]);
    for (const f of state.filters) parts.push(["filter", f]);
    return parts.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join("&");
  }

  function apply(view) {
    state = view.state;
    $("chart").innerHTML = view.svg;
    $("commands").textContent = view.commands.join("\n") || "aiwelfare --help";
    const banner = $("settings-banner");
    banner.hidden = view.is_canonical;
    banner.innerHTML = view.is_canonical ? "" :
      "These are <strong>your settings, not the canonical chart</strong>. Do not cite them as " +
      'the repository\'s estimates. <a href="index.html">Back to the canonical default chart</a>.';
    const nm = $("not-modelled");
    nm.innerHTML = view.not_modelled.length
      ? "<h3>Not modelled under this comparison</h3><ul>" + view.not_modelled
          .map((r) => `<li><strong>${r.title}</strong>: ${r.reason}</li>`).join("") + "</ul>"
      : "";
    if (view.problems.length) {
      status.textContent = "Some settings in the address were ignored: " + view.problems.join("; ");
      status.classList.add("warn");
    }
    const url = location.pathname + (view.query ? "?" + view.query : "");
    if (url !== location.pathname + location.search) history.replaceState(null, "", url);
    syncControls();
  }

  function render() {
    if (!py) return;
    status.textContent = "Computing…";
    setTimeout(() => {
      apply(JSON.parse(py.runPython(`_update(${JSON.stringify(query())})`)));
      status.textContent = `Computed in your browser: ${spec.draws.toLocaleString()} draws, seed ${spec.seed}, same code as the CLI.`;
      status.classList.remove("warn");
    }, 0);
  }

  try {
    if (!spec.cards.length) {
      status.textContent = "No card is on this chart yet, so there is nothing to explore.";
      return;
    }
    py = await loadPyodide({ indexURL: spec.pyodide.url });
    await py.loadPackage("numpy");
    const root = "/home/pyodide/repo";
    for (const f of spec.py_files) {
      const text = await (await fetch("py/" + f)).text();
      const dir = root + "/" + f.split("/").slice(0, -1).join("/");
      py.FS.mkdirTree(dir);
      py.FS.writeFile(root + "/" + f, text);
    }
    const claims = await (await fetch("data/claims.json")).text();
    py.globals.set("_spec_json", JSON.stringify(spec));
    py.globals.set("_claims_json", claims);
    py.runPython(`
import json, sys
sys.path.insert(0, "${root}")
from aiwelfare import explorer as _ex
_EXP = _ex.Explorer(json.loads(_spec_json), json.loads(_claims_json), "${root}")
def _update(q):
    return json.dumps(_EXP.update(q))
`);
    const diffs = py.runPython("json.dumps(_EXP.check_defaults())");
    document.querySelectorAll("input, select").forEach((el) => (el.disabled = false));
    document.querySelectorAll(".fix input[type=range]").forEach((el) => (el.disabled = false));
    const startQuery = location.search.replace(/^\?/, "");
    status.textContent = "Computing…";
    apply(JSON.parse(py.runPython(`_update(${JSON.stringify(startQuery)})`)));
    status.textContent = `Ready. Computed in your browser: ${spec.draws.toLocaleString()} draws, seed ${spec.seed}, same code as the CLI.`;
    status.classList.remove("warn");
    if (JSON.parse(diffs).length) {
      status.textContent = "Warning: this browser's default numbers differ from the CLI's: " + JSON.parse(diffs).join("; ");
      status.classList.add("warn");
    }
  } catch (e) {
    status.textContent = "The explorer could not start (" + e + "). The chart above is the canonical default.";
    status.classList.add("warn");
  }
})();
