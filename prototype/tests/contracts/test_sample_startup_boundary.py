"""A malformed sample manifest cannot produce a ready but empty workbench."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
pytestmark = [
    pytest.mark.contract,
    pytest.mark.frontend,
    pytest.mark.skipif(NODE is None, reason="node is not installed"),
]


def sample_startup(manifest, scenario="normal"):
    result = subprocess.run(
        [
            NODE,
            "-e",
            r"""
const fs = require('fs'), vm = require('vm');
const manifest = JSON.parse(process.argv[1]), scenario = process.argv[2], requests = [], timers = new Map();
let timerId = 0, deadline, signalCount = 0;
const context = {
  _workbenchState: { scratchDocs: scenario === 'scratch_collision' ? { 'scratch-1': { title: 'local.nomi' } } : {} },
  location: { href: 'https://example.org/nomi/web/' },
  URL, AbortController, window: {}, console: { warn() {} },
  setTimeout(callback, delay) { deadline = delay; timers.set(++timerId, callback); return timerId; },
  clearTimeout(id) { timers.delete(id); },
  fetch: async (url, options) => {
    requests.push(String(url));
    const signal = options && options.signal;
    if (signal) signalCount++;
    const stalled = () => new Promise((resolve, reject) => {
      if (signal) signal.addEventListener('abort', () => reject(new Error('aborted')), { once: true });
    });
    if ((scenario === 'stalled_manifest' && requests.length === 1)
      || (scenario === 'stalled_source' && requests.length === 2)) return stalled();
    const httpError = (scenario === 'http_manifest_error' && requests.length === 1)
      || (scenario === 'http_source_error' && requests.length === 2);
    return {
      ok: !httpError, status: httpError ? 503 : 200,
      json: async () => scenario === 'stalled_manifest_body' ? stalled() : manifest,
      text: async () => scenario === 'stalled_source_body' ? stalled() : 'print(42)\n',
    };
  },
};
vm.createContext(context);
vm.runInContext(fs.readFileSync('./web/demos.js', 'utf8'), context);
(async () => {
  const pending = context.loadSampleSources().then(
    () => ({ ok: true, samples: vm.runInContext('Object.keys(DEMOS)', context), nullPrototype: vm.runInContext('Object.getPrototypeOf(DEMOS) === null', context) }),
    error => ({ ok: false, message: error.message }),
  );
  for (let turn = 0; turn < 12; turn++) await Promise.resolve();
  if (scenario.startsWith('stalled_') && timers.size) [...timers.values()][0]();
  const outcome = await Promise.race([pending, new Promise(resolve => setTimeout(() => resolve({ ok: null }), 20))]);
  process.stdout.write(JSON.stringify({ ...outcome, requests, deadline, timerCount: timers.size, signalCount }));
})();
""",
            json.dumps(manifest),
            scenario,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize(
    "manifest",
    [
        None,
        [],
        {},
        {"samples": []},
        {"samples": {}},
        {"samples": "samples/demo_terse.nomi"},
        {"samples": [42]},
        {"samples": [""]},
        {"samples": [" "]},
        {"samples": ["samples/demo_terse.nomi", None]},
    ],
)
def test_invalid_sample_manifest_fails_before_fetching_any_source(manifest):
    result = sample_startup(manifest)
    assert result["ok"] is False
    assert "Sample manifest needs a nonempty text-path samples list" in result["message"]
    assert result["requests"] == ["./manifest.json"]
    assert result["timerCount"] == 0


def test_sample_manifest_requires_the_workbench_initial_source():
    result = sample_startup({"samples": ["samples/collections.nomi"]})
    assert result["ok"] is False
    assert "Sample manifest is missing samples/demo_terse.nomi" in result["message"]
    assert result["requests"] == ["./manifest.json"]
    assert result["timerCount"] == 0


def test_valid_sample_manifest_loads_its_initial_source():
    result = sample_startup({"samples": ["samples/demo_terse.nomi"]})
    assert result["ok"] is True
    assert result["samples"] == ["terse"]
    assert result["requests"] == [
        "./manifest.json",
        "https://example.org/nomi/samples/demo_terse.nomi",
    ]
    assert result["timerCount"] == 0


@pytest.mark.parametrize(
    "scenario",
    [
        "stalled_manifest",
        "stalled_source",
        "stalled_manifest_body",
        "stalled_source_body",
    ],
)
def test_stalled_sample_loading_aborts_instead_of_leaving_startup_pending(scenario):
    result = sample_startup({"samples": ["samples/demo_terse.nomi"]}, scenario)
    assert result["ok"] is False
    assert "Sample loading timed out" in result["message"]
    assert 0 < result["deadline"] <= 30_000
    assert result["timerCount"] == 0
    assert result["signalCount"] == len(result["requests"])


@pytest.mark.parametrize(
    "path",
    [
        "../private.nomi",
        "samples/../private.nomi",
        "samples/./draft.nomi",
        "samples//draft.nomi",
        "samples/draft.nomi?alternate=1",
        "samples/draft.nomi#alternate",
        "samples/%64raft.nomi",
        "samples/draft\\.nomi",
        "samples/draft\n.nomi",
        "samples/draft.py",
    ],
)
def test_sample_paths_are_canonical_and_cannot_alias_another_asset(path):
    result = sample_startup({"samples": ["samples/demo_terse.nomi", path]})
    assert result["ok"] is False
    assert "Invalid sample manifest path" in result["message"]
    assert result["requests"] == ["./manifest.json"]
    assert result["timerCount"] == 0


@pytest.mark.parametrize(
    ("paths", "message"),
    [
        (
            ["samples/demo_terse.nomi", "samples/demo_terse.nomi"],
            "Duplicate sample manifest path",
        ),
        (
            ["samples/demo_terse.nomi", "samples/terse.nomi"],
            "Colliding sample manifest identity",
        ),
        (
            ["samples/demo_terse.nomi", "samples/a_b.nomi", "samples/a-b.nomi"],
            "Colliding sample manifest identity",
        ),
        (
            ["samples/demo_terse.nomi", "samples/demo.nomi", "samples/demo.nomi.nb"],
            "Colliding sample manifest identity",
        ),
    ],
)
def test_duplicate_paths_and_colliding_document_keys_fail_before_source_fetch(paths, message):
    result = sample_startup({"samples": paths})
    assert result["ok"] is False
    assert message in result["message"]
    assert result["requests"] == ["./manifest.json"]
    assert result["timerCount"] == 0


@pytest.mark.parametrize("scenario", ["http_manifest_error", "http_source_error"])
def test_http_sample_loading_failure_also_clears_the_deadline(scenario):
    result = sample_startup({"samples": ["samples/demo_terse.nomi"]}, scenario)
    assert result["ok"] is False
    assert "returned HTTP 503" in result["message"]
    assert result["timerCount"] == 0


def test_sample_manifest_cannot_overwrite_a_restored_local_document():
    result = sample_startup(
        {"samples": ["samples/demo_terse.nomi", "samples/scratch-1.nomi"]},
        "scratch_collision",
    )
    assert result["ok"] is False
    assert "Colliding sample manifest identity: scratch-1" in result["message"]
    assert result["requests"] == ["./manifest.json"]
    assert result["timerCount"] == 0


def test_current_generated_manifest_remains_accepted():
    manifest = json.loads((ROOT / "web/manifest.json").read_text(encoding="utf-8"))
    result = sample_startup(manifest)
    assert result["ok"] is True
    assert len(result["samples"]) == len(manifest["samples"])
    assert len(result["requests"]) == len(manifest["samples"]) + 1
    assert result["timerCount"] == 0


def test_special_host_names_remain_own_sample_identities():
    result = sample_startup(
        {
            "samples": [
                "samples/demo_terse.nomi",
                "samples/__proto__.nomi",
                "samples/constructor.nomi",
                "samples/toString.nomi",
            ]
        }
    )
    assert result["ok"] is True
    assert result["samples"] == ["terse", "--proto--", "constructor", "toString"]
    assert result["nullPrototype"] is True
