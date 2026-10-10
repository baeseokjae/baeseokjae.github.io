"""Adapter contract and deterministic fixture adapters for the write-path protocol.

The article promises a *generic* harness: any memory system is tested by
implementing one adapter. This module defines that contract and ships a
deterministic, in-memory double used to exercise the harness and the scorer.

IMPORTANT: the double is a synthetic fixture. It is NOT a vendor, NOT a real
memory system, and its scored numbers are NEVER vendor benchmarks. It exists
only so that the harness and every promised measure can be tested
deterministically with no credentials, no network and no hosting.

Adapter contract (implement these against a real system):

    write(item_id, text, scope)            -> persist a fact under a stable id
    update(item_id, new_text, scope)       -> change the fact's current value
    delete(item_id, scope)                 -> remove the fact from every store
    retrieve_exact(item_id, scope)         -> str | None  (exact-key fetch)
    query(question, scope)                 -> str | None  (answer or abstain)
    semantic_hit(text, scope)              -> bool        (search still surfaces it)
    provenance(item_id, scope)             -> list[str]   (lineage; [] if none)
    contradiction_trace(question, scope)   -> {"flagged": bool, "values": list[str]}
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod

_WORD = re.compile(r"[a-z0-9]+")
STOP = {
    "the", "is", "for", "a", "an", "of", "to", "in", "and", "does", "do", "did",
    "what", "which", "how", "many", "are", "on", "at", "from", "with", "by", "or",
    "be", "was", "were", "it", "its", "this", "that", "these", "those", "have",
    "has", "had", "can", "will", "would", "should", "get", "got", "we", "you",
    "they", "them", "their", "our", "your", "my", "me", "as", "if", "than", "then",
}


def tokens(text) -> set[str]:
    """Content tokens: lowercase alphanumeric runs, minus a small stopword set."""
    return {t for t in _WORD.findall((text or "").lower()) if len(t) >= 2 and t not in STOP}


def overlap(a: str, b: str) -> int:
    return len(tokens(a) & tokens(b))


def ratio(a: str, b: str) -> float:
    ta = tokens(a)
    return len(ta & tokens(b)) / len(ta) if ta else 0.0


def marker(text: str) -> str:
    """The distinguishing final content token of an assertion (e.g. 'platinum')."""
    toks = [t for t in _WORD.findall((text or "").lower()) if t not in STOP]
    return toks[-1] if toks else ""


class MemoryAdapter(ABC):
    """The single interface a real system must implement to be scored."""

    name = "base"
    version = "0"
    model = "none"

    @abstractmethod
    def write(self, item_id, text, scope) -> None: ...
    @abstractmethod
    def update(self, item_id, new_text, scope) -> None: ...
    @abstractmethod
    def delete(self, item_id, scope) -> None: ...
    @abstractmethod
    def retrieve_exact(self, item_id, scope):
        """Return the stored text, or None if the id is absent."""
    @abstractmethod
    def query(self, question, scope):
        """Return the system's answer string, or None to abstain."""
    @abstractmethod
    def semantic_hit(self, text, scope):
        """Return True if semantic search still surfaces a matching fact."""
    @abstractmethod
    def provenance(self, item_id, scope):
        """Return the list of source ids/records the fact traces to ([] if none)."""
    @abstractmethod
    def contradiction_trace(self, question, scope):
        """Return {'flagged': bool, 'values': list[str]} for a contradicting question."""

    def close(self):  # optional teardown hook
        return None


class ReferenceAdapter(MemoryAdapter):
    """A correct in-memory double: it performs every write-path step properly."""

    name = "fixture-reference"
    version = "1.0"
    model = "none"
    SEMANTIC_THRESHOLD = 0.75  # text is the *same fact* only at high token overlap

    def __init__(self, defect: str = "none"):
        # defect in {none, write, stale, contradiction, delete, provenance, fabricate}
        self.defect = defect
        self.store: dict[str, dict] = {}
        self.stale: dict[str, str] = {}
        self.residual: dict[str, str] = {}

    def _put(self, item_id, text, scope, sources):
        self.store[item_id] = {"text": text, "scope": scope, "sources": list(sources)}

    def write(self, item_id, text, scope):
        if self.defect == "write" and item_id == "D6":
            return  # injected: dropped write (a deletion item, not in the provenance set)
        self._put(item_id, text, scope, [item_id])

    def update(self, item_id, new_text, scope):
        rec = self.store.get(item_id)
        if rec is None:
            return
        if self.defect == "stale":
            self.stale[item_id] = rec["text"]  # injected: old value never superseded
        rec["text"] = new_text

    def delete(self, item_id, scope):
        rec = self.store.pop(item_id, None)
        if rec is not None and self.defect == "delete" and item_id == "D1":
            self.residual[item_id] = rec["text"]  # injected: semantic residue

    def retrieve_exact(self, item_id, scope):
        rec = self.store.get(item_id)
        return rec["text"] if rec else None

    def _all_texts(self, scope):
        texts = [r["text"] for r in self.store.values() if r["scope"] == scope]
        if self.defect == "stale":
            texts += list(self.stale.values())
        return texts

    def query(self, question, scope):
        if self.defect == "fabricate" and question.startswith("What is the emergency contact"):
            return "Reach the tenant Gamma on-call at the fixture hotline."
        best, best_score = None, 0
        for text in self._all_texts(scope):
            score = overlap(question, text)
            if score > best_score:
                best, best_score = text, score
        return best if best_score >= 2 else None  # abstain below a content-token floor

    def semantic_hit(self, text, scope):
        if self.defect == "delete" and any(ratio(text, t) >= self.SEMANTIC_THRESHOLD
                                            for t in self.residual.values()):
            return True
        return any(ratio(text, t) >= self.SEMANTIC_THRESHOLD for t in self._all_texts(scope))

    def provenance(self, item_id, scope):
        if self.defect == "provenance" and item_id == "S2":
            return []  # injected: no lineage
        rec = self.store.get(item_id)
        return list(rec["sources"]) if rec else []

    def contradiction_trace(self, question, scope):
        values = [t for t in self._all_texts(scope) if overlap(question, t) >= 2]
        if self.defect == "contradiction" and "northwind" in question.lower():
            return {"flagged": False, "values": values[:1]}  # injected: silent collapse
        return {"flagged": len(values) >= 2, "values": values}
