"""Loading and validating sources and claims (D13, D15)."""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass, field
from functools import cache
from importlib import resources
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

MAX_QUOTE_WORDS = 24  # "under 25 words" (CLAUDE.md)


def repo_root(start: Path | None = None) -> Path:
    """Nearest ancestor containing pyproject.toml and sources/ or claims/."""
    here = (start or Path.cwd()).resolve()
    for p in [here, *here.parents]:
        if (p / "pyproject.toml").exists() and (p / "docs" / "decisions.md").exists():
            return p
    raise FileNotFoundError("not inside the aiwelfare repository")


@cache
def _validator(name: str) -> Draft202012Validator:
    text = resources.files("aiwelfare.schema").joinpath(f"{name}.schema.yaml").read_text()
    return Draft202012Validator(yaml.safe_load(text), format_checker=FormatChecker())


@dataclass
class Dataset:
    root: Path
    include_mock: bool = False
    sources: dict[str, dict] = field(default_factory=dict)
    claims: dict[str, dict] = field(default_factory=dict)
    baselines: dict[str, dict] = field(default_factory=dict)
    paths: dict[str, Path] = field(default_factory=dict)

    @property
    def touches_mock(self) -> bool:
        return any(d.get("mock") for d in [*self.sources.values(), *self.claims.values()])


def _trees(root: Path, include_mock: bool) -> list[tuple[Path, bool]]:
    trees = [(root, False)]
    if include_mock:
        trees.append((root / "mock", True))
    return trees


def load(root: Path | None = None, include_mock: bool = False) -> Dataset:
    root = root or repo_root()
    ds = Dataset(root=root, include_mock=include_mock)
    for base, _ in _trees(root, include_mock):
        for f in sorted((base / "sources").glob("*/source.yaml")):
            d = _read(f)
            ds.sources[d["id"]] = d
            ds.paths[d["id"]] = f
        for f in sorted((base / "claims").glob("*/*.yaml")):
            d = _read(f)
            ds.claims[d["id"]] = d
            ds.paths[d["id"]] = f
        for f in sorted((base / "baselines").glob("*.yaml")):
            d = _read(f)
            ds.baselines[d["id"]] = d
            ds.paths["baseline/" + d["id"]] = f
    return ds


def _read(f: Path):
    """Load YAML with dates kept as ISO strings, so schemas see what the file says."""
    return _stringify_dates(yaml.safe_load(f.read_text()))


def _stringify_dates(x):
    if isinstance(x, dict):
        return {k: _stringify_dates(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_stringify_dates(v) for v in x]
    if isinstance(x, (datetime.date, datetime.datetime)):
        return x.isoformat()
    return x


def _words(s: str) -> int:
    return len(re.findall(r"\S+", s))


def validate(root: Path | None = None, include_mock: bool = True) -> list[str]:
    """Return a list of human-readable problems; empty means valid."""
    root = root or repo_root()
    problems: list[str] = []
    seen: dict[str, Path] = {}
    source_ids: set[str] = set()
    claims: list[tuple[Path, dict]] = []
    baselines: list[tuple[Path, dict]] = []

    for base, is_mock_tree in _trees(root, include_mock):
        for kind, pattern in (
            ("source", "sources/*/source.yaml"),
            ("claim", "claims/*/*.yaml"),
            ("baseline", "baselines/*.yaml"),
        ):
            for f in sorted(base.glob(pattern)):
                rel = f.relative_to(root)
                try:
                    d = _read(f)
                except yaml.YAMLError as e:
                    problems.append(f"{rel}: invalid YAML: {e}")
                    continue
                for err in _validator(kind).iter_errors(d):
                    loc = "/".join(str(x) for x in err.absolute_path) or "(root)"
                    problems.append(f"{rel}: {loc}: {err.message}")
                if not isinstance(d, dict) or "id" not in d:
                    continue
                key = ("baseline/" if kind == "baseline" else "") + d["id"]
                if key in seen:
                    problems.append(f"{rel}: duplicate id {d['id']} (also {seen[key]})")
                seen[key] = rel
                if d.get("mock") is not is_mock_tree:
                    where = "inside mock/" if is_mock_tree else "outside mock/"
                    problems.append(f"{rel}: mock: {d.get('mock')} not allowed {where} (D13)")
                if kind == "source":
                    if f.parent.name != d["id"]:
                        problems.append(f"{rel}: folder name must equal id {d['id']}")
                    source_ids.add(d["id"])
                elif kind == "baseline":
                    baselines.append((f, d))
                else:
                    claims.append((f, d))

    for f, d in claims:
        rel = f.relative_to(root)
        if f.stem != d["id"]:
            problems.append(f"{rel}: file name must equal id {d['id']}")
        if f.parent.name != d.get("risk"):
            problems.append(f"{rel}: folder must equal risk {d.get('risk')}")
        q = d.get("quote")
        if q and _words(q) > MAX_QUOTE_WORDS:
            problems.append(f"{rel}: quote has {_words(q)} words; must be under 25")
        src = d.get("source")
        if src and src not in source_ids:
            problems.append(f"{rel}: unknown source {src}")
    for f, d in baselines:
        rel = f.relative_to(root)
        if f.stem != d.get("id"):
            problems.append(f"{rel}: file name must equal id {d.get('id')}")
        if d.get("source") not in source_ids:
            problems.append(f"{rel}: unknown source {d.get('source')}")
        q = d.get("quote")
        if q and _words(q) > MAX_QUOTE_WORDS:
            problems.append(f"{rel}: quote has {_words(q)} words; must be under 25")
    return problems
