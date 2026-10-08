"""Probe sintético e opcional de dois limites no SHA fixado do AI Farm Agent.

Executa somente dois módulos Python revisados do checkout upstream. Não chama
LLM, ferramentas de desktop, rede ou handlers de exclusão.
"""

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


UPSTREAM_SHA = "4ffa018f50d25668e6e46726723b0ed6040caf2f"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Módulo indisponível: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def git_output(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, stderr=subprocess.DEVNULL
    ).strip()


def probe(root: Path) -> tuple[dict[str, str], int]:
    if git_output(root, "rev-parse", "HEAD") != UPSTREAM_SHA:
        raise ValueError("Checkout upstream não corresponde ao SHA fixado")
    if git_output(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Há arquivos rastreados alterados no checkout upstream")

    src = root / "ai-farm-agent" / "core"
    # Não grave bytecode na árvore externa durante a importação.
    sys.dont_write_bytecode = True
    versions = load_module("study_project_versions", src / "project_versions.py")
    validator = load_module("study_plan_validator", src / "plan_validator.py")

    results = {}
    with tempfile.TemporaryDirectory(prefix="ai-farm-study-") as temp:
        base = Path(temp)
        project = base / "project"
        project.mkdir()
        outside = base / "outside.md"
        outside.write_text("SYNTHETIC_OUTSIDE", encoding="utf-8")
        link = project / "linked.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            results["read_outside_symlink"] = "SKIPPED"
            results["safe_rel_rejects_symlink"] = "SKIPPED"
        else:
            read = versions.read_project(str(project))
            results["read_outside_symlink"] = (
                "OBSERVED" if read["files"].get("linked.md") == "SYNTHETIC_OUTSIDE"
                else "NOT_OBSERVED"
            )
            results["safe_rel_rejects_symlink"] = (
                "OBSERVED" if versions.safe_rel(str(project), "linked.md") is None
                else "NOT_OBSERVED"
            )

        check = validator.validate_steps(
            "FILE",
            {"task": "listar arquivos", "params": {}},
            [{"action": "delete_file", "params": {"path": str(outside)}}],
            "listar arquivos",
        )
        results["delete_step_for_list_request"] = (
            "OBSERVED" if check.approved else "NOT_OBSERVED"
        )

    if "NOT_OBSERVED" in results.values():
        return results, 1
    if "SKIPPED" in results.values():
        return results, 2
    return results, 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    args = parser.parse_args()
    try:
        results, status = probe(args.upstream.resolve())
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(results, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
