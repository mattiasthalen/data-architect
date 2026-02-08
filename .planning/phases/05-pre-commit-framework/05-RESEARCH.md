# Phase 5: Pre-commit Framework Migration - Research

**Researched:** 2026-02-08
**Domain:** Git hooks management framework (pre-commit)
**Confidence:** HIGH

## Summary

The pre-commit framework is a multi-language pre-commit hook manager that standardizes git hook management across projects. It replaces manual bash script copying with declarative YAML configuration and provides a consistent interface for hook installation and execution. The framework supports multiple hook types (pre-commit, commit-msg, etc.) and can wrap existing tools like Make targets using local hooks with `language: system`.

For this migration, the strategy is straightforward: configure pre-commit to call `make check` as a local hook and use a conventional commit validator for commit messages. This preserves the existing Makefile-based quality checks while gaining framework benefits like standardized installation, hook management, and team consistency.

The uv package manager (0.10.0) integrates well with pre-commit. While pre-commit can be installed via `uv tool install pre-commit`, adding it to dev dependencies provides better reproducibility and version pinning.

**Primary recommendation:** Use local hooks with `language: system` to wrap `make check`, set `default_install_hook_types: [pre-commit, commit-msg]` for automatic installation, and use `compilerla/conventional-pre-commit` for commit message validation.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pre-commit | 4.x+ | Git hook framework | Industry standard for multi-language hook management, 40k+ GitHub stars |
| conventional-pre-commit | Latest | Commit message validation | Maintained hook specifically for Conventional Commits, works with commit-msg stage |

### Installation
```bash
# Add to pyproject.toml dev dependencies
uv add --dev pre-commit

# Or install as a tool (less recommended for team projects)
uv tool install pre-commit
```

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pre-commit framework | Husky (Node.js) | Husky requires Node/npm, less suitable for Python projects |
| pre-commit framework | Manual bash scripts | No dependency management, manual hook installation, harder maintenance |
| conventional-pre-commit | commitlint | Requires Node.js ecosystem, overkill for Python projects |

## Architecture Patterns

### Recommended Configuration Structure

**`.pre-commit-config.yaml` (project root):**
```yaml
default_install_hook_types:
  - pre-commit
  - commit-msg

repos:
  - repo: local
    hooks:
      - id: make-check
        name: Run make check
        entry: make check
        language: system
        pass_filenames: false
        always_run: true

  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.4.0  # Use latest stable version
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: []  # Add --strict, --force-scope, or type restrictions if needed
```

### Pattern 1: Makefile Wrapper Hook
**What:** Local hook that delegates to Make target rather than configuring individual tools
**When to use:** When you have existing Makefile automation and want a single source of truth
**Benefits:**
- Changes to quality checks only require Makefile updates
- Hook configuration stays minimal and declarative
- Make handles parallelization and dependencies
- Developers can run `make check` directly without pre-commit

**Example:**
```yaml
# Source: https://pre-commit.com/ (local hooks documentation)
- repo: local
  hooks:
    - id: make-check
      name: Run make check
      entry: make check
      language: system
      pass_filenames: false  # Make handles file discovery
      always_run: true       # Run on every commit, not just when specific files change
```

### Pattern 2: Hook Type Declaration
**What:** Explicitly declare which hook types should be installed by default
**When to use:** When using non-default hook types like commit-msg
**Benefits:**
- Single `pre-commit install` command installs all needed hooks
- Team doesn't need to remember multiple install commands
- Self-documenting hook requirements

**Example:**
```yaml
# Source: https://pre-commit.com/ (configuration options)
default_install_hook_types:
  - pre-commit    # Default
  - commit-msg    # Non-default, must be declared
```

### Pattern 3: Bootstrap Integration
**What:** Make target that installs dependencies and hooks atomically
**When to use:** Project setup, onboarding new developers
**Implementation:**
```makefile
# Makefile
.PHONY: bootstrap
bootstrap:  ## Install deps + git hooks
	uv sync --dev
	uv run pre-commit install
```

**Why this works:**
- `uv sync --dev` ensures pre-commit is installed
- `uv run pre-commit install` uses the project's pinned pre-commit version
- Single command for complete setup
- No manual hook copying or chmod commands

### Anti-Patterns to Avoid

- **Configuring individual tools in .pre-commit-config.yaml when you have Make:** This duplicates configuration and creates two sources of truth. If tools are already configured in pyproject.toml and orchestrated by Make, let pre-commit call Make.

- **Using `language: python` for local scripts that need project dependencies:** This creates an isolated environment without your project's dependencies. Use `language: system` for scripts that need the project environment.

- **Forgetting `pass_filenames: false` for Make targets:** Make targets like `make check` discover files themselves. Passing filenames causes Make to receive unexpected arguments.

- **Not declaring commit-msg in default_install_hook_types:** The commit-msg hook type is not installed by default. Omitting it means `pre-commit install` won't set up commit message validation.

- **Using `--hook-type` flags in bootstrap scripts:** If `default_install_hook_types` is set in config, plain `pre-commit install` installs all declared types. Using flags duplicates logic and risks drift.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Conventional commit validation | Bash regex parser | compilerla/conventional-pre-commit | Handles edge cases (fixup!, revert, merge commits), supports scopes, provides clear error messages, maintained |
| Hook installation | Bash scripts that copy hooks | pre-commit install | Handles hook types, preserves existing hooks, provides uninstall, standard across projects |
| Multi-tool orchestration | Bash script that chains commands | Make target + pre-commit wrapper | Make handles parallelization, dependency tracking, and cross-platform differences |
| Environment isolation | Manual virtualenv creation | pre-commit's language support | Automatic, cached, handles multiple languages, version-specific |

**Key insight:** Git hooks have subtle behaviors (hook types, exit codes, file arguments, merge commits) that are easy to get wrong. Pre-commit handles these edge cases consistently. Custom bash scripts accumulate workarounds over time and become maintenance burdens.

## Common Pitfalls

### Pitfall 1: Wrong Language Declaration
**What goes wrong:** Using `language: python` or other isolated languages for local tools that need project dependencies
**Why it happens:** Developers expect pre-commit to use the project environment by default
**How to avoid:** Use `language: system` for hooks that call project tools (make, pytest, mypy, etc.). This uses the system Python with project dependencies installed.
**Warning signs:** Hook fails with import errors despite dependencies being installed, hook creates unexpected virtualenv in `.git/hooks`

### Pitfall 2: Missing `pass_filenames: false` for Make Hooks
**What goes wrong:** Pre-commit passes filenames as arguments to `make check`, causing "unknown target" errors
**Why it happens:** Pre-commit's default is `pass_filenames: true` because most hooks process specific files
**How to avoid:** Set `pass_filenames: false` for any hook that doesn't accept file arguments (Make targets, test runners, full-project linters)
**Warning signs:** Hook fails with "No rule to make target 'src/file.py'", works when run manually without arguments

### Pitfall 3: Forgetting commit-msg Hook Type
**What goes wrong:** Commit message validation doesn't run despite being configured
**Why it happens:** Only `pre-commit` hook type is installed by default
**How to avoid:** Add `default_install_hook_types: [pre-commit, commit-msg]` at top level of `.pre-commit-config.yaml`
**Warning signs:** Invalid commits are not rejected, `ls -la .git/hooks/` shows no `commit-msg` file

### Pitfall 4: Not Using `always_run: true` for Full-Project Checks
**What goes wrong:** `make check` only runs when certain file types are staged
**Why it happens:** Pre-commit tries to optimize by running hooks only on matching files
**How to avoid:** Set `always_run: true` for hooks that need to run on every commit regardless of changed files
**Warning signs:** Pre-commit skips hook with "no files to check", even though hook should always run

### Pitfall 5: Using `pre-commit install --install-hooks` in CI
**What goes wrong:** CI installs hook environments unnecessarily, slowing down builds
**Why it happens:** `--install-hooks` downloads and installs all hook dependencies, but CI should use `pre-commit run --all-files` directly
**How to avoid:** In CI, skip installation and run directly: `uv run pre-commit run --all-files`
**Warning signs:** CI logs show "installing environment for...", unnecessary network requests

### Pitfall 6: System vs Unsupported Language Confusion
**What goes wrong:** Documentation references both `language: system` and `language: unsupported`
**Why it happens:** Pre-commit is gradually deprecating `system` in favor of more semantically clear `unsupported`
**How to avoid:** Use `language: system` (still supported, more familiar) or `language: unsupported` (newer, clearer naming). Both work identically.
**Warning signs:** None currently, both are supported

## Code Examples

Verified patterns from official sources:

### Complete .pre-commit-config.yaml
```yaml
# Source: https://pre-commit.com/ (configuration documentation)
# Location: .pre-commit-config.yaml (project root)

# Ensure both pre-commit and commit-msg hooks are installed
default_install_hook_types:
  - pre-commit
  - commit-msg

repos:
  # Local hook that wraps Makefile
  - repo: local
    hooks:
      - id: make-check
        name: Run make check (lint + type + test)
        entry: make check
        language: system
        pass_filenames: false  # Make discovers files itself
        always_run: true       # Run on every commit
        verbose: true          # Show Make output

  # Conventional commit validation
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.4.0  # Check for latest: https://github.com/compilerla/conventional-pre-commit/releases
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        # Optional args:
        # args: [--strict]  # Reject fixup! and merge commits
        # args: [--force-scope]  # Require scope in every commit
        # args: [feat, fix, docs, test, chore]  # Restrict to specific types
```

### Updated Makefile Bootstrap Target
```makefile
# Source: Pattern from https://docs.astral.sh/uv/guides/integration/pre-commit/
# Location: Makefile

.PHONY: bootstrap
bootstrap:  ## Install deps + git hooks
	uv sync --dev
	@echo "Installing pre-commit hooks..."
	uv run pre-commit install
	@echo "Done! Git hooks installed via pre-commit framework."
```

### Hook Installation Commands
```bash
# Source: https://pre-commit.com/ (CLI documentation)

# Initial setup (installs hooks declared in default_install_hook_types)
uv run pre-commit install

# Manual run on all files (useful for testing)
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run make-check --all-files

# Update hook repositories to latest versions
uv run pre-commit autoupdate

# Uninstall hooks (preserves legacy hooks if they existed)
uv run pre-commit uninstall
```

### Migration Script (if needed)
```bash
# Source: Derived from https://pre-commit.com/ (uninstall behavior)
# Optional: Explicitly remove legacy hooks before installing pre-commit

# Backup existing hooks
cp .git/hooks/pre-commit .git/hooks/pre-commit.backup 2>/dev/null || true
cp .git/hooks/commit-msg .git/hooks/commit-msg.backup 2>/dev/null || true

# Remove legacy hooks
rm -f .git/hooks/pre-commit
rm -f .git/hooks/commit-msg

# Install pre-commit (it will create new hook scripts)
uv run pre-commit install

# Legacy scripts in scripts/hooks/ can be removed after verification
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `language: system` | `language: unsupported` | v4.4.0+ | Both work, `unsupported` is clearer terminology |
| Manual `--hook-type` flags | `default_install_hook_types` config | v2.10.0+ | Single install command, self-documenting config |
| `pre-commit install --install-hooks` | `pre-commit install` (lazy install) | Always available | Faster initial setup, hooks install on first use |
| Repository-specific hooks | Local hooks with `repo: local` | v1.0.0+ | No separate repo needed for project-specific hooks |

**Current best practices (2026):**
- Use `default_install_hook_types` instead of multiple `--hook-type` flags
- Use `language: system` (familiar) or `language: unsupported` (clearer) interchangeably
- Use local hooks for project-specific tooling
- Let hooks install lazily (on first run) rather than using `--install-hooks`
- Add pre-commit to dev dependencies, not as a tool install

**Deprecated/outdated:**
- `language: system` is being soft-deprecated in favor of `language: unsupported` (but still works)
- Copying hooks manually with bash scripts (pre-commit framework is standard)
- Using `--hook-type` flags when `default_install_hook_types` is available

## Open Questions

None. The migration path is well-documented and the patterns are established.

## Sources

### Primary (HIGH confidence)
- [pre-commit.com](https://pre-commit.com/) - Official documentation, configuration options, hook creation guide
- [compilerla/conventional-pre-commit](https://github.com/compilerla/conventional-pre-commit) - Conventional commit hook configuration and usage
- [Astral uv pre-commit integration guide](https://docs.astral.sh/uv/guides/integration/pre-commit/) - Official uv integration documentation

### Secondary (MEDIUM confidence)
- [pre-commit: How to create hooks for unsupported tools - Adam Johnson](https://adamj.eu/tech/2023/02/09/pre-commit-hooks-unsupported-tools/) - System/unsupported language guidance
- [How to setup git hooks(pre-commit, commit-msg) in my project? | Medium](https://medium.com/@0xmatriksh/how-to-setup-git-hooks-pre-commit-commit-msg-in-my-project-11aaec139536) - Hook type installation examples
- [Common Pre-Commit Errors and How to Solve Them | Stefanie Molin](https://stefaniemolin.com/articles/devx/pre-commit/troubleshooting-guide/) - Pitfalls and troubleshooting
- [Using uv with pre-commit](https://docs.astral.sh/uv/guides/integration/pre-commit/) - UV integration patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Pre-commit is industry standard, conventional-pre-commit is established solution
- Architecture: HIGH - Local hooks with language: system is documented pattern for Makefile integration
- Pitfalls: HIGH - Common issues are well-documented in official troubleshooting guides and community resources

**Research date:** 2026-02-08
**Valid until:** 2026-03-08 (30 days - stable, mature framework with infrequent breaking changes)

**Environment context:**
- Python: 3.11.14
- uv: 0.10.0
- Project uses: Makefile, pyproject.toml, uv for package management
- Current hooks: bash scripts in scripts/hooks/ (pre-commit, commit-msg)
