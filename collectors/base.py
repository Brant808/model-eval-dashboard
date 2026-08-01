"""Shared collector infrastructure (brief Phase 7, architecture mandated):
per-source timeout (~60s), retry with backoff, honest User-Agent, raw-response
caching to raw/ for reparse, and LOUD parse failures — a collector must raise,
never emit a guessed number.

Each per-source module in collectors/ subclasses Collector and implements
parse(raw) -> list[CellValue]. Fixtures for tests live in collectors/fixtures/
as recorded raw responses; fixture tests run parse() offline.
"""

from __future__ import annotations

import dataclasses
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent
RAW_DIR = REPO / "raw"

USER_AGENT = (
    "model-eval-dashboard/1.0 (+https://github.com/brant808/model-eval-dashboard; "
    "daily eval dashboard; contact via repo issues)"
)

DEFAULT_TIMEOUT_S = 60
RETRIES = 3
BACKOFF_S = (2, 8, 30)


class ParseFailure(Exception):
    """Source fetched but did not parse as expected. Always fatal for the
    source (never guess); pipeline degrades that source to last-good+stale."""


class FetchFailure(Exception):
    """Source unreachable after retries."""


@dataclasses.dataclass
class CellValue:
    """One normalized observation, pre-snapshot. run.py merges these into the
    canonical cell schema."""

    metric_id: str
    model_id: str
    value: object  # number or string; None is not allowed here (absence = no CellValue)
    unit: str
    tag: str  # "I" | "V" — must match the source's ledger independence class
    source_id: str
    comparability_set: str
    retrieved_at: str  # source data vintage where declared, else fetch time
    effort_tier: str | None = None
    flags: list = dataclasses.field(default_factory=list)
    derived_from: list | None = None  # parent cell ids for derived metrics
    value_disclaimed: bool = False  # publisher disclaims the value itself


class Collector:
    """Base class. Subclasses set: source_id, name, url(s); implement
    fetch() (default GET of self.url) and parse(raw) -> list[CellValue]."""

    source_id: str = ""
    name: str = ""
    url: str = ""
    timeout_s: int = DEFAULT_TIMEOUT_S

    def __init__(self, now: datetime | None = None):
        self.now = now or datetime.now(timezone.utc)
        self.fetched_at = self.now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # -- fetching ----------------------------------------------------------
    def http_get(self, url: str, headers: dict | None = None) -> bytes:
        h = {"User-Agent": USER_AGENT}
        if headers:
            h.update(headers)
        last_err: Exception | None = None
        for attempt in range(RETRIES + 1):
            try:
                r = requests.get(url, headers=h, timeout=self.timeout_s)
                if r.status_code == 429 and attempt < RETRIES:
                    retry_after = int(r.headers.get("Retry-After", BACKOFF_S[min(attempt, len(BACKOFF_S) - 1)]))
                    time.sleep(min(retry_after, 60))
                    continue
                r.raise_for_status()
                return r.content
            except requests.RequestException as e:  # includes HTTPError
                last_err = e
                if attempt < RETRIES:
                    time.sleep(BACKOFF_S[min(attempt, len(BACKOFF_S) - 1)])
        raise FetchFailure(f"{self.source_id} {url}: {last_err}")

    def fetch(self) -> bytes:
        return self.http_get(self.url)

    # -- parsing -----------------------------------------------------------
    def parse(self, raw: bytes) -> list[CellValue]:
        raise NotImplementedError

    # -- orchestration ------------------------------------------------------
    def cache_raw(self, raw: bytes, date_str: str) -> Path:
        RAW_DIR.mkdir(exist_ok=True)
        path = RAW_DIR / f"{date_str}.{self.source_id}.{self.name}.raw"
        path.write_bytes(raw)
        return path

    def collect(self, date_str: str) -> list[CellValue]:
        """fetch -> cache raw -> parse. Raises FetchFailure/ParseFailure;
        the runner catches per-source and applies last-good+stale semantics."""
        raw = self.fetch()
        self.cache_raw(raw, date_str)
        cells = self.parse(raw)
        if not cells:
            raise ParseFailure(f"{self.source_id} {self.name}: parse produced zero cells")
        return cells


def extract_next_flight_json(html: str, anchor: str) -> str:
    """Locate the JSON region following `anchor` inside a Next.js flight
    payload (self.__next_f.push chunks). Returns the raw candidate string for
    json extraction by the caller. Raises ParseFailure when the anchor is
    missing — the page shape changed, so fail LOUD."""
    idx = html.find(anchor)
    if idx == -1:
        raise ParseFailure(f"flight-JSON anchor {anchor!r} not found — page shape changed")
    return html[idx:]


def balanced_json_object(text: str, start_key: str):
    """Parse the first balanced {...} object that starts at/after start_key.
    Handles quoted strings and escapes. Raises ParseFailure on imbalance."""
    kidx = text.find(start_key)
    if kidx == -1:
        raise ParseFailure(f"start key {start_key!r} not found")
    oidx = text.find("{", kidx)
    if oidx == -1:
        raise ParseFailure(f"no object after {start_key!r}")
    depth = 0
    in_str = False
    esc = False
    for i in range(oidx, len(text)):
        c = text[i]
        if esc:
            esc = False
            continue
        if c == "\\":
            esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                blob = text[oidx : i + 1]
                try:
                    return json.loads(blob)
                except json.JSONDecodeError as e:
                    raise ParseFailure(f"balanced object at {start_key!r} not valid JSON: {e}") from e
    raise ParseFailure(f"unbalanced object after {start_key!r}")


def decode_flight_region(html: str, anchor_escaped: str, back: int = 200, span: int = 2_500_000) -> str:
    """Next.js flight payloads embed JSON as an escaped JS string
    (self.__next_f.push([1,"...\\"key\\":...")). Locate the escaped anchor,
    unescape the surrounding region, and return proper JSON text for
    balanced parsing. Raises ParseFailure if the anchor is missing (page
    shape changed -> fail LOUD)."""
    idx = html.find(anchor_escaped)
    if idx == -1:
        raise ParseFailure(f"flight anchor {anchor_escaped!r} not found — page shape changed")
    window = html[max(0, idx - back): idx + span]
    return window.replace("\\\\", "\x00").replace('\\"', '"').replace("\x00", "\\")


def balanced_json_array(text: str, start_key: str):
    """Parse the first balanced [...] array that starts at/after start_key."""
    kidx = text.find(start_key)
    if kidx == -1:
        raise ParseFailure(f"start key {start_key!r} not found")
    oidx = text.find("[", kidx)
    if oidx == -1:
        raise ParseFailure(f"no array after {start_key!r}")
    depth = 0
    in_str = False
    esc = False
    for i in range(oidx, len(text)):
        c = text[i]
        if esc:
            esc = False
            continue
        if c == "\\":
            esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c in "[{":
            depth += 1
        elif c in "]}":
            depth -= 1
            if depth == 0:
                blob = text[oidx: i + 1]
                try:
                    return json.loads(blob)
                except json.JSONDecodeError as e:
                    raise ParseFailure(f"balanced array at {start_key!r} not valid JSON: {e}") from e
    raise ParseFailure(f"unbalanced array after {start_key!r}")


FLIGHT_CHUNK_RE = None  # compiled lazily (import-time regex cost)


def flight_text(html: str) -> str:
    """Concatenate ALL Next.js flight chunks (self.__next_f.push([1,"..."]))
    into one decoded payload string. Needed when an embedded array spans chunk
    boundaries (large SSR pages split payloads). Raises ParseFailure when no
    chunks exist — the page shape changed."""
    global FLIGHT_CHUNK_RE
    import re as _re

    if FLIGHT_CHUNK_RE is None:
        FLIGHT_CHUNK_RE = _re.compile(
            r'self\.__next_f\.push\(\[1,\s*"((?:[^"\\]|\\.)*)"\]\)', _re.S
        )
    parts = FLIGHT_CHUNK_RE.findall(html)
    if not parts:
        raise ParseFailure("no flight chunks found — page shape changed")
    decoded = []
    for s in parts:
        try:
            decoded.append(json.loads('"' + s + '"'))
        except json.JSONDecodeError:
            # fall back to the cheap unescape for odd chunks
            decoded.append(s.replace("\\\\", "\x00").replace('\\"', '"').replace("\x00", "\\"))
    return "".join(decoded)
