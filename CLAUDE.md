# CLAUDE.md

## Repository Overview

This is the Ed-Fi Alliance DevSecOps monorepo containing reusable CI/CD templates, code quality configurations, and compliance tooling for Ed-Fi organization repositories. It serves as a standards distribution point — language-specific subdirectories publish configurations that other Ed-Fi repositories consume.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `javascript/` | ESLint, Prettier, TypeScript configs and GitHub Actions templates (build/test, CodeQL) for JS/TS projects |
| `dotnet/` | `Directory.Build.props`, editor configs, and workflow templates for .NET projects; split into `open/` and `closed/` subdirectories |
| `python/` | flake8, mypy, and black configs plus workflow templates for Python projects |
| `common/` | Shared GitHub Actions workflow template for dependency review |
| `edfi-repo-auditor/` | Python CLI tool that audits Ed-Fi repositories for governance compliance — has its own `CLAUDE.md` |
| `metrics/` | Jupyter notebooks for Ed-Fi tech team operational metrics (Poetry-based Python project) |
| `ec2-shutdown/` | AWS cloud resource management tooling |

## Code Standards

From `.github/copilot-instructions.md`:

- **Never modify `pyproject.toml` or `poetry.lock`** unless explicitly asked.
- **Do not reformat existing code** unless explicitly asked; respect `.editorconfig`.
- Python projects use Poetry, black, flake8, mypy, pytest, and require type hints on all function signatures.

## GitHub Actions Patterns

Each language directory follows the same three-workflow pattern:

- `test.yml` — build and run tests
- `codeql.yml` — CodeQL security scanning
- References `../common/sample-dependencies-workflow.yml` for dependency review

These templates are meant to be copied into consuming repositories, not run from this repo directly.
