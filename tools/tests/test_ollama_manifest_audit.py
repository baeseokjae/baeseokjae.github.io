"""Keep the corrected Ollama article, its reader, and captured evidence aligned."""
import csv
import hashlib
import json
import math
import re
import unittest
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SLUG = "ollama-tag-quant-bits-per-weight-audit-2026"
EVIDENCE = ROOT / "research/evidence" / SLUG / "results"
ARTICLE = (ROOT / "content/posts" / f"{SLUG}.md").read_text()
SNAPSHOT = json.loads((EVIDENCE / "correction-2026-11-09.json").read_text())
SOURCES = json.loads((EVIDENCE / "tensor-sources-2026-11-09.json").read_text())


def reader_namespace():
    blocks = re.findall(r"```python\n(.*?)\n```", ARTICLE, re.S)
    if len(blocks) != 1:
        raise AssertionError("Expected exactly one executable Python example")
    namespace = {"__name__": "article_test"}
    exec(compile(blocks[0], "article-reader.py", "exec"), namespace)
    return namespace


class OllamaManifestAuditTests(unittest.TestCase):
    def setUp(self):
        self.reader = reader_namespace()
        self.responses = {}
        self.requests = []
        for row in SNAPSHOT["rows"]:
            for kind in ("manifest", "config"):
                read = row[f"{kind}_read"]
                self.responses[read["url"]] = (
                    row[f"{kind}_raw"].encode(), read["server_date"], read["checked_at"]
                )

        def get(url):
            self.requests.append(url)
            return self.responses[url]

        self.reader["get"] = get

    def test_captured_manifests_and_configs_match_recorded_hashes_and_sizes(self):
        with (EVIDENCE / "audit-2026-11-03.csv").open() as stream:
            original = {f"{r['family']}:{r['tag']}": r for r in csv.DictReader(stream)}
        self.assertEqual(len(SNAPSHOT["rows"]), 14)
        for row in SNAPSHOT["rows"]:
            with self.subTest(tag=row["tag"]):
                manifest = json.loads(row["manifest_raw"])
                for kind in ("manifest", "config"):
                    raw = row[f"{kind}_raw"].encode()
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), row[f"{kind}_read"]["sha256"])
                    self.assertEqual(len(raw), row[f"{kind}_read"]["bytes"])
                    self.assertEqual(row[f"{kind}_read"]["status"], 200)
                self.assertEqual(manifest["config"]["digest"], "sha256:" + row["config_read"]["sha256"])
                self.assertEqual(manifest["config"]["size"], len(row["config_raw"].encode()))
                self.assertEqual(row["manifest_read"]["sha256"], original[row["tag"]]["manifest_sha256"])
                self.assertTrue(row["unchanged_since_original"])

    def test_tensor_elements_recompute_from_unique_names_and_dimensions(self):
        records = defaultdict(list)
        with (EVIDENCE / "tensor-elements-2026-11-09.csv").open() as stream:
            for row in csv.DictReader(stream):
                records[row["tag"]].append(row)
        self.assertEqual(len(records), 14)
        for source in SOURCES["records"]:
            with self.subTest(tag=source["tag"]):
                tensors = records[source["tag"]]
                self.assertEqual(len(tensors), source["tensor_count"])
                self.assertEqual(len({x["tensor_name"] for x in tensors}), len(tensors))
                total = 0
                for tensor in tensors:
                    elements = math.prod(int(d) for d in tensor["dimensions"].split("x"))
                    self.assertEqual(elements, int(tensor["elements"]))
                    total += elements
                self.assertEqual(total, source["total"])

    def test_all_fourteen_printed_rows_reproduce_from_same_blob_evidence(self):
        tensor_sources = {r["tag"]: r for r in SOURCES["records"]}
        for row in SNAPSHOT["rows"]:
            with self.subTest(tag=row["tag"]):
                source = tensor_sources[row["tag"]]
                result = self.reader["audit"](f"{row['tag']}={source['total']}")
                self.assertEqual(result["model_bytes"], source["bytes"])
                self.assertEqual(len(result["model_layers"]), 1)
                self.assertEqual(result["model_layers"][0]["digest"], source["digest"])
                self.assertEqual(result["file_bpw"], round(source["bytes"] * 8 / source["total"], 3))
                self.assertEqual(result["all_layer_bytes"], row["all_layer_bytes"])
                table_line = next(line for line in ARTICLE.splitlines() if line.startswith(f"| [{row['tag']}]"))
                w = result["model_bytes"]
                expected = (
                    f"| {result['file_type']} | {w:,} | {w/1e9:.3f} / {w/2**30:.3f} | "
                    f"[{source['total']:,}]({source['url']}) | {result['file_bpw']:.3f} | "
                    f"{result['all_layer_bytes']:,} |"
                )
                self.assertIn(expected, table_line)
        # Exactly manifest + config per model; never request model or projector blobs.
        self.assertEqual(len(self.requests), 28)

    def test_absent_denominator_leaves_bpw_null(self):
        result = self.reader["audit"]("phi4:14b")
        self.assertIsNone(result["parameters_supplied"])
        self.assertIsNone(result["file_bpw"])

    def test_invalid_specs_rejected_before_network(self):
        for spec in ("qwen3", "qwen3:32b=0", "qwen3:32b=-1", "qwen3:32b=1.5", "../qwen3:32b", "qwen3:32b/evil"):
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                self.reader["audit"](spec)
        self.assertEqual(self.requests, [])

    def test_manifest_lists_rejected_without_selecting_an_artifact(self):
        self.reader["get"] = lambda url: (b'{"manifests": []}', None, "test")
        with self.assertRaisesRegex(ValueError, "manifest list"):
            self.reader["audit"]("qwen3:32b")

    def test_missing_model_layer_rejected(self):
        self.reader["get"] = lambda url: (b'{"layers": []}', None, "test")
        with self.assertRaisesRegex(ValueError, "No model layer"):
            self.reader["audit"]("qwen3:32b")

    def test_config_digest_mismatch_rejected(self):
        row = next(r for r in SNAPSHOT["rows"] if r["tag"] == "qwen3:32b")
        key = row["config_read"]["url"]
        raw, date, checked = self.responses[key]
        self.responses[key] = (raw.replace(b"Q4_K_M", b"Q5_K_M"), date, checked)
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.reader["audit"]("qwen3:32b")

    def test_config_size_mismatch_rejected(self):
        row = next(r for r in SNAPSHOT["rows"] if r["tag"] == "qwen3:32b")
        key = row["config_read"]["url"]
        raw, date, checked = self.responses[key]
        self.responses[key] = (raw + b" ", date, checked)
        with self.assertRaisesRegex(ValueError, "size or digest mismatch"):
            self.reader["audit"]("qwen3:32b")

    def test_qwen32_size_examples(self):
        w, n = 20_201_240_160, 32_762_123_264
        self.assertEqual(32_000_000_000 * 4 // 8, 16_000_000_000)
        self.assertEqual(round(w / 64e9 * 100, 1), 31.6)
        self.assertEqual(round(w / (n * 2) * 100, 1), 30.8)
        self.assertEqual(round(35_132_291_680 / w, 3), 1.739)
        self.assertEqual(round((35_132_291_680 / w - 1) * 100, 1), 73.9)


if __name__ == "__main__":
    unittest.main()
