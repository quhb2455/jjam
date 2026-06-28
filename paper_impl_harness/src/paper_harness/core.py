from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomllib
from pypdf import PdfReader


IGNORED_PARTS = {
    ".git",
    ".paper-harness",
    ".venv",
    "_useless",
    "build",
    "dist",
    "node_modules",
}

DOCUMENT_TEMPLATES = (
    "paper_summary.md",
    "feasibility_report.md",
    "implementation_plan.md",
    "paper_code_alignment.md",
    "validation_report.md",
    "implementation_notes.md",
)

JSON_TEMPLATES = (
    "feasibility.json",
    "implementation-manifest.json",
    "alignment.json",
    "validation.json",
)

RESERVED_IMPLEMENTATION_PARTS = {".paper-harness", "_useless", "harness"}


class HarnessError(RuntimeError):
    """An actionable harness failure."""


@dataclass(frozen=True)
class Config:
    repo_root: Path
    harness_root: Path
    workspace_root: Path
    input_dir: Path
    output_dir: Path
    state_dir: Path
    docs_dir: Path
    timeout_seconds: int
    minimum_document_bytes: int


@dataclass(frozen=True)
class CheckResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def load_config(
    repo_root: Path,
    workspace: Path | str | None = None,
    harness_root: Path | None = None,
) -> Config:
    repo_root = repo_root.resolve()
    harness_root = (harness_root or repo_root / "paper_impl_harness").resolve()
    config_path = harness_root / "paper-harness.toml"
    if not config_path.is_file():
        raise HarnessError(f"Missing configuration: {config_path}")
    with config_path.open("rb") as handle:
        raw = tomllib.load(handle)
    repository = raw.get("repository", {})
    workspace_settings = raw.get("workspace", {})
    validation = raw.get("validation", {})
    input_dir = _inside_root(repo_root / repository.get("input_dir", "papers"), repo_root)
    output_dir = _inside_root(repo_root / repository.get("output_dir", "implementations"), repo_root)
    workspace_arg = workspace
    workspace_root = output_dir if workspace_arg is None else _inside_root(repo_root / workspace_arg, output_dir)
    if workspace_arg is not None and workspace_root == output_dir:
        raise HarnessError("A paper workspace must be a child directory of implementations/.")
    return Config(
        repo_root=repo_root,
        harness_root=harness_root,
        workspace_root=workspace_root,
        input_dir=input_dir,
        output_dir=output_dir,
        state_dir=workspace_root / workspace_settings.get("state_dir", ".paper-harness"),
        docs_dir=workspace_root / workspace_settings.get("docs_dir", "docs"),
        timeout_seconds=int(validation.get("command_timeout_seconds", 300)),
        minimum_document_bytes=int(validation.get("minimum_document_bytes", 120)),
    )


def _inside_root(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise HarnessError(f"Path must stay inside the repository: {path}") from exc
    return resolved


def discover_pdf(config: Config, explicit: str | None = None) -> Path:
    if explicit:
        candidate = _inside_root(config.repo_root / explicit, config.input_dir)
        if not candidate.is_file() or candidate.suffix.lower() != ".pdf":
            raise HarnessError(f"Paper PDF not found: {candidate}")
        return candidate

    candidates = sorted(
        path
        for path in config.input_dir.rglob("*.pdf")
        if not any(part in IGNORED_PARTS for part in path.relative_to(config.input_dir).parts)
    )
    if not candidates:
        raise HarnessError("No paper PDF found. Add one or pass its path to `prepare`.")
    if len(candidates) > 1:
        names = ", ".join(str(path.relative_to(config.repo_root)) for path in candidates)
        raise HarnessError(f"Multiple PDFs found ({names}). Pass one path to `prepare`.")
    return candidates[0].resolve()


def slugify_title(title: str, fallback: str) -> str:
    normalized = unicodedata.normalize("NFKC", title).strip().lower()
    slug = re.sub(r"[^\w]+", "-", normalized, flags=re.UNICODE).strip("-_")
    slug = re.sub(r"-+", "-", slug)[:100].rstrip("-")
    if not slug:
        slug = re.sub(r"[^\w]+", "-", fallback.lower(), flags=re.UNICODE).strip("-_")
    if not slug:
        raise HarnessError("Could not derive an output directory name; pass --output explicitly.")
    return slug


def select_workspace(config: Config, pdf: Path, title: str | None, output: str | None) -> Path:
    if output:
        selected = _inside_root(config.repo_root / output, config.output_dir)
        if selected == config.output_dir:
            raise HarnessError("--output must name a child directory under implementations/.")
        return selected
    if not title or not title.strip():
        raise HarnessError("The exact paper title is required. Pass it with --title.")
    return config.output_dir / slugify_title(title, pdf.stem)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _clean_metadata(value: Any) -> str:
    return "" if value is None else str(value).strip()


def extract_paper(config: Config, pdf: Path, title: str) -> dict[str, Any]:
    try:
        reader = PdfReader(str(pdf))
    except Exception as exc:  # pypdf exposes several parser-specific failures
        raise HarnessError(f"Could not read PDF {pdf.name}: {exc}") from exc

    extracted: list[str] = []
    empty_pages: list[int] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if not text.strip():
            empty_pages.append(index)
        extracted.append(f"\n\n===== PAGE {index} =====\n\n{text.strip()}")

    metadata = reader.metadata or {}
    metadata_title = _clean_metadata(metadata.get("/Title"))
    manifest = {
        "schema_version": 1,
        "pdf": "paper.pdf",
        "source_pdf": str(pdf.relative_to(config.repo_root)),
        "sha256": _sha256(pdf),
        "pages": len(reader.pages),
        "title": title.strip(),
        "metadata_title": metadata_title,
        "author": _clean_metadata(metadata.get("/Author")),
        "empty_text_pages": empty_pages,
        "extraction_warning": (
            "Some pages yielded no text; inspect the original PDF and use OCR if needed."
            if empty_pages
            else "Text extraction does not preserve figures, equations, or layout; inspect the PDF."
        ),
    }
    config.state_dir.mkdir(parents=True, exist_ok=True)
    (config.state_dir / "paper.txt").write_text("".join(extracted).lstrip(), encoding="utf-8")
    _write_json(config.state_dir / "paper-manifest.json", manifest)
    return manifest


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HarnessError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise HarnessError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise HarnessError(f"Expected a JSON object in {path}")
    return value


def scaffold(config: Config, manifest: dict[str, Any]) -> list[Path]:
    template_dir = config.harness_root / "harness" / "templates"
    config.docs_dir.mkdir(parents=True, exist_ok=True)
    config.state_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for name in DOCUMENT_TEMPLATES:
        destination = config.docs_dir / name
        if not destination.exists():
            shutil.copyfile(template_dir / name, destination)
            created.append(destination)
    for name in JSON_TEMPLATES:
        destination = config.state_dir / name
        if destination.exists():
            continue
        data = _read_json(template_dir / name)
        if name == "feasibility.json":
            data["paper"] = {
                "title": manifest["title"],
                "pdf": manifest["pdf"],
                "sha256": manifest["sha256"],
                "pages": manifest["pages"],
            }
        _write_json(destination, data)
        created.append(destination)
    return created


def prepare(config: Config, pdf: Path, title: str) -> tuple[dict[str, Any], list[Path]]:
    previous_manifest_path = config.state_dir / "paper-manifest.json"
    if previous_manifest_path.is_file():
        previous = _read_json(previous_manifest_path)
        current_digest = _sha256(pdf)
        if previous.get("sha256") != current_digest:
            raise HarnessError(
                "This output workspace already contains evidence for a different PDF. "
                "Choose another --output or archive the existing workspace."
            )
    config.workspace_root.mkdir(parents=True, exist_ok=True)
    destination_pdf = config.workspace_root / "paper.pdf"
    if pdf.resolve() != destination_pdf.resolve():
        shutil.copy2(pdf, destination_pdf)
    manifest = extract_paper(config, pdf, title)
    return manifest, scaffold(config, manifest)


def _nonempty_strings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def check_assessment(config: Config) -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = _read_json(config.state_dir / "feasibility.json")
    except HarnessError as exc:
        return CheckResult([str(exc)], warnings)

    decision = data.get("decision")
    if decision not in {"feasible", "partial", "not_feasible"}:
        errors.append("feasibility.json decision must be feasible, partial, or not_feasible")
    scores = data.get("scores")
    required_scores = {
        "method_specification",
        "resource_feasibility",
        "data_asset_access",
        "evaluation_feasibility",
        "dependency_feasibility",
    }
    if not isinstance(scores, dict) or set(scores) != required_scores:
        errors.append("feasibility.json must contain exactly the five rubric scores")
    elif any(not isinstance(score, int) or score < 0 or score > 2 for score in scores.values()):
        errors.append("each feasibility score must be an integer from 0 to 2")
    elif decision == "feasible" and any(
        scores[key] == 0 for key in ("method_specification", "data_asset_access", "evaluation_feasibility")
    ):
        errors.append("a feasible decision cannot score zero for method, data/assets, or evaluation")
    elif decision == "partial" and scores["method_specification"] == 0:
        errors.append("a partial implementation still requires a reconstructable central method")
    scope = data.get("implementation_scope", {})
    if decision in {"feasible", "partial"} and not _nonempty_strings(scope.get("included")):
        errors.append("implementation_scope.included must define the supported implementation")
    if decision == "partial" and not _nonempty_strings(scope.get("excluded")):
        errors.append("partial decisions must list excluded scope")
    if decision == "not_feasible" and not _nonempty_strings(data.get("binding_constraints")):
        errors.append("not_feasible decisions must list binding constraints")
    evidence = data.get("paper_evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("feasibility.json paper_evidence must cite at least one paper location")
    elif any(not isinstance(item, dict) or not str(item.get("location", "")).strip() or not str(item.get("finding", "")).strip() for item in evidence):
        errors.append("each paper_evidence item needs non-empty location and finding")
    try:
        paper_manifest = _read_json(config.state_dir / "paper-manifest.json")
    except HarnessError as exc:
        errors.append(str(exc))
    else:
        paper_identity = data.get("paper", {})
        if paper_identity.get("sha256") != paper_manifest.get("sha256"):
            errors.append("feasibility.json paper.sha256 does not match the prepared PDF")
        if paper_identity.get("pdf") != paper_manifest.get("pdf"):
            errors.append("feasibility.json paper.pdf does not match the prepared PDF")
    errors.extend(_check_document(config.docs_dir / "paper_summary.md", config))
    errors.extend(_check_document(config.docs_dir / "feasibility_report.md", config))
    if decision == "not_feasible":
        warnings.append("Assessment says not_feasible: stop implementation and deliver the unblock plan.")
    return CheckResult(errors, warnings)


def _check_document(path: Path, config: Config) -> list[str]:
    if not path.is_file():
        return [f"missing document: {path.relative_to(config.workspace_root)}"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if len(text.encode("utf-8")) < config.minimum_document_bytes:
        errors.append(f"document is too small to be complete: {path.relative_to(config.workspace_root)}")
    if "TODO" in text or "<!-- Replace" in text:
        errors.append(f"document still contains template placeholders: {path.relative_to(config.workspace_root)}")
    return errors


def _path_list(config: Config, data: dict[str, Any], key: str, errors: list[str]) -> list[Path]:
    values = data.get(key)
    if not _nonempty_strings(values):
        errors.append(f"implementation-manifest.json {key} must be a non-empty string list")
        return []
    paths: list[Path] = []
    for value in values:
        try:
            path = _inside_root(config.workspace_root / value, config.workspace_root)
        except HarnessError as exc:
            errors.append(str(exc))
            continue
        if not path.is_file():
            errors.append(f"manifest path does not exist: {value}")
        relative_parts = path.relative_to(config.workspace_root.resolve()).parts
        if any(part in RESERVED_IMPLEMENTATION_PARTS for part in relative_parts) or relative_parts[:2] == (
            "src",
            "paper_harness",
        ):
            errors.append(f"manifest {key} points to harness/archive code, not paper code: {value}")
        paths.append(path)
    return paths


def check_final(config: Config) -> CheckResult:
    assessment = check_assessment(config)
    errors = list(assessment.errors)
    warnings = list(assessment.warnings)
    try:
        feasibility = _read_json(config.state_dir / "feasibility.json")
    except HarnessError:
        return CheckResult(errors, warnings)
    if feasibility.get("decision") == "not_feasible":
        errors.append("final implementation gate is not applicable to a not_feasible assessment")
        return CheckResult(errors, warnings)

    try:
        implementation = _read_json(config.state_dir / "implementation-manifest.json")
        alignment = _read_json(config.state_dir / "alignment.json")
        validation = _read_json(config.state_dir / "validation.json")
    except HarnessError as exc:
        errors.append(str(exc))
        return CheckResult(errors, warnings)

    if implementation.get("status") != "complete":
        errors.append("implementation-manifest.json status must be complete")
    if not str(implementation.get("language", "")).strip():
        errors.append("implementation-manifest.json language must be documented")
    _path_list(config, implementation, "source_files", errors)
    _path_list(config, implementation, "test_files", errors)
    if not _nonempty_strings(implementation.get("entrypoints")):
        errors.append("implementation-manifest.json entrypoints must be non-empty")
    commands = implementation.get("validation_commands")
    if not isinstance(commands, list) or not commands:
        errors.append("at least one validation command is required")
    else:
        for item in commands:
            if not isinstance(item, dict) or not str(item.get("name", "")).strip() or not _nonempty_strings(item.get("command")):
                errors.append("each validation command needs a name and non-empty command array")
    environment = implementation.get("environment", {})
    for key in ("setup", "seed", "device"):
        if not isinstance(environment, dict) or not str(environment.get(key, "")).strip():
            errors.append(f"implementation-manifest.json environment.{key} must be documented (use 'not applicable' if needed)")

    claims = alignment.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("alignment.json must contain at least one claim")
    else:
        valid_levels = {"structural", "numerical", "empirical"}
        valid_statuses = {"verified", "unverified", "deviates"}
        for index, claim in enumerate(claims, start=1):
            prefix = f"alignment claim {index}"
            if not isinstance(claim, dict) or not str(claim.get("claim", "")).strip():
                errors.append(f"{prefix} needs a claim")
                continue
            if claim.get("evidence_level") not in valid_levels:
                errors.append(f"{prefix} has invalid evidence_level")
            if claim.get("status") not in valid_statuses:
                errors.append(f"{prefix} has invalid status")
            for evidence_key in ("paper_evidence", "code_evidence", "validation_evidence"):
                if not isinstance(claim.get(evidence_key), list) or not claim[evidence_key]:
                    errors.append(f"{prefix} needs {evidence_key}")
            for item in claim.get("paper_evidence", []):
                if not isinstance(item, dict) or not str(item.get("location", "")).strip() or not str(item.get("detail", "")).strip():
                    errors.append(f"{prefix} paper evidence needs location and detail")
            for item in claim.get("code_evidence", []):
                path_value = item.get("path", "") if isinstance(item, dict) else ""
                try:
                    code_path = (
                        _inside_root(config.workspace_root / str(path_value), config.workspace_root)
                        if path_value
                        else None
                    )
                except HarnessError as exc:
                    errors.append(f"{prefix}: {exc}")
                    code_path = None
                if code_path is None or not code_path.is_file():
                    errors.append(f"{prefix} references missing code path: {path_value or '<empty>'}")
                if not isinstance(item, dict) or not str(item.get("symbol", "")).strip() or not str(item.get("detail", "")).strip():
                    errors.append(f"{prefix} code evidence needs symbol and detail")
            for item in claim.get("validation_evidence", []):
                path_value = item.get("path", "") if isinstance(item, dict) else ""
                try:
                    validation_path = (
                        _inside_root(config.workspace_root / str(path_value), config.workspace_root)
                        if path_value
                        else None
                    )
                except HarnessError as exc:
                    errors.append(f"{prefix}: {exc}")
                    validation_path = None
                if validation_path is None or not validation_path.is_file():
                    errors.append(f"{prefix} references missing validation path: {path_value or '<empty>'}")
                if not isinstance(item, dict) or not str(item.get("test", "")).strip() or not str(item.get("detail", "")).strip():
                    errors.append(f"{prefix} validation evidence needs test/command and detail")
            if claim.get("status") == "deviates" and not str(claim.get("deviation", "")).strip():
                errors.append(f"{prefix} marked deviates but has no deviation explanation")

    if validation.get("overall_status") not in {"passed", "partial"}:
        errors.append("validation.json overall_status must be passed or partial at delivery")
    if validation.get("review_pass_completed") is not True:
        errors.append("validation.json must confirm an independent review pass")
    for level in ("structural", "numerical", "empirical"):
        section = validation.get(level, {})
        if section.get("status") not in {"passed", "partial", "failed", "not_run", "not_applicable"}:
            errors.append(f"validation.json {level}.status is invalid")
        if section.get("status") in {"passed", "partial"} and not _nonempty_strings(section.get("evidence")):
            errors.append(f"validation.json {level}.evidence is required for {section.get('status')}")
    if validation.get("structural", {}).get("status") not in {"passed", "partial"}:
        errors.append("structural validation must be passed or partial at delivery")

    for name in DOCUMENT_TEMPLATES:
        errors.extend(_check_document(config.docs_dir / name, config))
    errors.extend(_check_document(config.workspace_root / "README.md", config))
    return CheckResult(errors, warnings)


def run_validation_commands(config: Config) -> list[dict[str, Any]]:
    data = _read_json(config.state_dir / "implementation-manifest.json")
    results: list[dict[str, Any]] = []
    for item in data.get("validation_commands", []):
        name = str(item.get("name", "unnamed"))
        command = item.get("command", [])
        if not _nonempty_strings(command):
            results.append({"name": name, "command": command, "returncode": None, "error": "invalid command"})
            continue
        try:
            completed = subprocess.run(
                command,
                cwd=config.workspace_root,
                text=True,
                capture_output=True,
                timeout=config.timeout_seconds,
                check=False,
            )
            results.append(
                {
                    "name": name,
                    "command": command,
                    "returncode": completed.returncode,
                    "stdout": completed.stdout[-12000:],
                    "stderr": completed.stderr[-12000:],
                }
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            results.append({"name": name, "command": command, "returncode": None, "error": str(exc)})
    _write_json(config.state_dir / "check-results.json", results)
    return results


def status(config: Config) -> list[tuple[str, str]]:
    paths = {
        "paper extraction": config.state_dir / "paper.txt",
        "feasibility": config.state_dir / "feasibility.json",
        "implementation": config.state_dir / "implementation-manifest.json",
        "alignment": config.state_dir / "alignment.json",
        "validation": config.state_dir / "validation.json",
        "README": config.workspace_root / "README.md",
    }
    output: list[tuple[str, str]] = []
    for label, path in paths.items():
        if not path.exists():
            state = "missing"
        elif path.suffix == ".json":
            try:
                data = _read_json(path)
                state = str(data.get("decision") or data.get("status") or data.get("overall_status") or "present")
            except HarnessError:
                state = "invalid"
        else:
            state = "present"
        output.append((label, state))
    return output
