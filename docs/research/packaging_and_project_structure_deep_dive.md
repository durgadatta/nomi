# Packaging & Project Structure: Cross-Language Deep Dive

> Status: source research for Nomi design.
> Purpose: Study how eight major programming-language ecosystems handle packaging,
> modules, dependency management, and project structure — then extract the
> structural invariants, genuine tradeoffs, and specific recommendations for
> Nomi's module/packaging design.

## Table of Contents

1. [Python Packaging](#1-python-packaging)
2. [Cargo (Rust)](#2-cargo-rust)
3. [Go Modules](#3-go-modules)
4. [Mix (Elixir)](#4-mix-elixir)
5. [npm / Node.js](#5-npm--nodejs)
6. [NuGet (.NET/C#)](#6-nuget-net--c)
7. [Nix Flakes](#7-nix-flakes)
8. [Java / Maven / Gradle](#8-java--maven--gradle)
9. [Cross-Language Synthesis](#9-cross-language-synthesis)
10. [Nomi Adopt / Refuse / Adapt Table](#10-nomi-adopt--refuse--adapt-table)
11. [Sources](#sources)

---

## 1. Python Packaging

### Core Design Philosophy

Python's packaging story is an accretion layer, not a designed system. It grew
from `distutils` (2000) to `setuptools` (2004) to `pip` (2011) to `virtualenv`
(2007) to `pyproject.toml` (PEP 518, 2016) across two decades. No single
designer sat down and said "this is how Python packages should work." The
philosophy emerged from the community: **batteries included at the language
level, but packaging is a third-party concern.** This split — the language is
one thing, packaging is another — is Python's original sin in this space and
the root of most of its pain.

### What Worked Exceptionally Well

**The CheeseShop (PyPI) as a discovery surface.** PyPI's search, metadata, and
simple publishing workflow (`twine upload`) made publishing a package trivial.
The low barrier — no account vetting, no namespace squatting policy (until
recently), no review process — meant the ecosystem grew to 500,000+ packages.
Discovery through `pip search` (now removed) and pypi.org became the first
place every Python programmer looks for existing solutions.

**Wheels as a distribution format.** The transition from `egg` to `wheel` (PEP
427, 2012) was Python's most successful packaging reform. Wheels are
standardized ZIP archives with a naming convention
(`{dist}-{version}-{pyver}-{abi}-{platform}.whl`) that encodes exactly what
environment the wheel supports. `manylinux` wheels (PEP 513/571/600) solved the
native-code distribution problem that had plagued Python for 15 years. The
lesson: **a binary distribution format that encodes target platform in the
filename eliminates the "works on my machine" class of packaging bugs.**

**`pyproject.toml` (PEP 518/517/621) as a convergence point.** After 15 years
of `setup.py` (executable Python that could do arbitrary things at install
time), the community converged on a declarative manifest. The key insight was
separating the *build system declaration* from the *project metadata*:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "nomi"
version = "0.1.0"
dependencies = ["lark>=1.1"]
```

This means a tool can read `pyproject.toml` without executing arbitrary
Python — something impossible with `setup.py`. The migration is still in
progress (2026), but the direction is settled.

**Virtual environments as isolation.** The `venv` module (Python 3.3,
standardized in 3.5) is genuinely good: lightweight, per-project Python
installations that don't require copying the interpreter. The activation
script modifies `PATH` and `PYTHONPATH`; deactivation restores them.
Combined with `pip install -r requirements.txt`, this gives reproducible
environments — when tooling is disciplined enough to use them.

### What Failed or Caused Persistent Friction

**The setup.py era: Turing-complete packaging.** For 15 years, installing a
Python package meant executing arbitrary Python code. `setup.py` could read
files from disk, call external commands, inspect the system, and generate code
dynamically. This made static analysis impossible, broke security tools, and
meant `pip install` could fail with an inscrutable traceback from code the user
didn't write. The migration path has been slow because `setup.py` was also the
CLI entry point for building, testing, and publishing — replacing it required
replacing an entire workflow.

**Virtualenv confusion (venv vs virtualenv vs pyenv vs conda vs poetry shell
vs pipenv shell).** The isolation story is fragmented across at least six
tools, each with different conventions for where environments live, how they're
activated, and what they manage. New Python users routinely install packages
globally, break their system Python, and then learn about virtual environments
the hard way. The community has never converged on a single answer for "where
should my project's Python live?"

**Dependency resolution: the pip legacy.** `pip` used a backtracking-free
"install whatever satisfies the constraint first" resolver until 2020. This
meant `pip install A B` could succeed or fail depending on install order, and
`pip install A==1.0; pip install B` could silently downgrade A. The new
resolver (2020) uses proper backtracking but is slower, and the lack of a
lockfile by default means two developers can run `pip install` a week apart and
get different dependency trees. `pip freeze > requirements.txt` captures
exact pins but not transitive dependency reasons — you cannot tell *why*
something is in the list.

**`requirements.txt` vs `setup.py` vs `Pipfile` vs `pyproject.toml`** — four
files that express overlapping concerns. `requirements.txt` is for deployment
(exact pins). `setup.py`/`pyproject.toml` is for library metadata (abstract
dependencies). `Pipfile`/`Pipfile.lock` was an abortive attempt at a unified
format. Every Python project of nontrivial size ends up with at least two
dependency files that must be kept in sync.

**Namespace packages.** Python's PEP 420 implicit namespace packages solved the
"two libraries both want to own `foo.bar`" problem by allowing directories
without `__init__.py` to contribute to a namespace. But the solution created a
new edge case: if you have a local `utils/string.py` and there's an installed
`utils` package, imports behave differently depending on whether `utils/` has
`__init__.py`. This is invisible, hard to debug, and inconsistent across
Python versions.

### The Key Structural Insight for Nomi

**Packaging is too important to be an afterthought.** Python's packaging
story — 20 years of incremental fixes on an ad-hoc foundation — is the single
biggest source of friction for Python programmers. The lesson is not "Python's
specific mistakes" but **"the packaging model must be designed at the same time
as the language, not bolted on later."** Every successful modern language
(Cargo 2015, Go modules 2018, Mix 2012) shipped with a package manager and
build system as part of the language release. Python shipped the language in
1991 and the first real packaging standard in 2000 — a nine-year gap that the
ecosystem never fully recovered from.

---

## 2. Cargo (Rust)

### Core Design Philosophy

Cargo is the gold standard of modern language packaging. Its philosophy is
simple and comprehensive: **there is one way to build, test, document, and
publish Rust code, and it ships with the compiler.** Cargo is not an add-on
tool — you install Rust, you have Cargo. There is no `pip` vs `easy_install`
vs `poetry`, no `setup.py` vs `pyproject.toml`, no virtualenv vs conda.
Everything is Cargo.

### What Worked Exceptionally Well

**Cargo.toml as a single source of truth.** One file encodes everything:
project metadata, dependencies, dev-dependencies, build-dependencies, optional
features, target-specific configuration, workspace membership, and benchmarks.
There is no secondary file for deployment pins, no separate file for
development dependencies, and no file that lists transitive dependencies
(everything is resolved from `Cargo.lock`).

```toml
[package]
name = "nomi"
version = "0.1.0"
edition = "2024"

[dependencies]
lark = "1.1"              # semantic versioning
serde = { version = "1", features = ["derive"] }
clap = { version = "4", optional = true }

[dev-dependencies]
criterion = "0.5"

[features]
default = ["cli"]
cli = ["clap"]

[workspace]
members = ["prototype", "tools/*"]
```

Key properties of this manifest:
- **Version ranges use semantic versioning.** `"1.1"` means `>=1.1.0, <2.0.0`
  (Cargo treats the caret requirement as the default). `"=1.1.0"` pins exactly.
- **Features are additive and composable.** A feature flag enables optional
  dependencies and conditional compilation. Features compose: if A depends on B
  with `feature = ["x"]` and C depends on both A and B, C gets B with "x"
  enabled (feature unification).
- **Dev-dependencies are scoped.** `criterion` is only available during `cargo
  test` and `cargo bench`. It does not appear in the dependency tree of
  downstream consumers.
- **Workspaces share a single `Cargo.lock`.** All members of a workspace resolve
  to the same dependency versions. This eliminates the "different versions of
  the same library in different sub-projects" problem.

**Cargo.lock and deterministic builds.** `Cargo.lock` records the exact
version, source, and checksum of every crate in the dependency tree. Two
developers with the same `Cargo.lock` get byte-for-byte identical `target/`
directories. The lockfile is committed to version control for applications
(binaries) and omitted for libraries (so consumers get the latest compatible
versions). This distinction — lockfile policy depends on whether you're
building a binary or a library — is subtle but correct.

**`cargo add` / `cargo remove`.** Editing `Cargo.toml` by hand was the norm
until `cargo edit` stabilized. Now `cargo add serde --features derive` edits
`Cargo.toml` and runs dependency resolution in one step. The CLI is the
interface; the TOML file is the storage format. The tool never produces invalid
TOML.

**`cargo doc --open`.** Documentation generation is a first-class build target,
not an external tool. `cargo doc` runs rustdoc on the current crate and all
dependencies, producing interlinked HTML. Running `cargo test` also runs
doc-tests (code examples in documentation that are compiled and executed). This
means documentation cannot bit-rot silently — failing doc-tests are failing
tests.

**crates.io integration.** `cargo publish` runs `cargo package` (verify the
crate builds from the packaged source), then uploads to crates.io. `cargo
yank --vers 0.2.1` deprecates a version without deleting it — existing
lockfiles still resolve, but new projects won't pick it up. crates.io is
immutable (published crates can't be overwritten) and requires email
verification. Namespace squatting is managed by a per-account namespacing
policy.

**The editions system.** Rust editions (2015, 2018, 2021, 2024) are opt-in
compiler modes that can introduce breaking syntax changes without fragmenting
the ecosystem. A crate on edition 2018 can depend on a crate on edition 2021
without issues — editions are per-crate, not per-compilation. This is
genuinely innovative and solves the Python 2/3 migration problem: **you can
evolve the language without forking the ecosystem.**

### What Failed or Caused Persistent Friction

**Compile times and dependency bloat.** A medium Rust project routinely pulls
200-400 transitive dependencies. `cargo build` from scratch can take minutes.
The `syn` crate (Rust's parser for Rust) appears in almost every proc-macro
dependency tree and is a known compile-time bottleneck. Cargo's feature
unification — while correct — means enabling a feature in one dependency can
silently enable it for all others, which can bloat compile times unexpectedly.

**Feature unification surprises.** If crate A depends on `serde` with no
features and crate B depends on `serde` with `features = ["derive"]`, the
unified build includes `derive`. This is usually correct but can cause subtle
problems: a crate that conditionally compiles code based on feature flags may
compile differently depending on what other crates happen to be in the tree.
The `weak` dependency feature (stabilized in 2024) partially addresses this but
adds complexity.

**No namespacing on crates.io (historically).** Crate names were flat and
first-come-first-served. `serde` is owned by the serde team, but `serde_derive`
could theoretically be owned by anyone. The ecosystem has managed this through
social norms and a responsive crates.io team, but the lack of namespacing
creates squatting incentives. The `cargo` team has discussed namespaced crates
since 2017; the current approach is "namespaces via renaming" (`serde =
{ package = "serde7", version = "1" }`).

**`build.rs` as a footgun.** Build scripts are arbitrary Rust code that runs at
compile time. They can read environment variables, link native libraries, and
generate code. Like `setup.py`, they are Turing-complete and can do anything —
including break in environments the crate author never tested. The community
has responded with `system-deps` and conventions around `pkg-config`, but
`build.rs` remains the biggest source of non-reproducible builds in the Rust
ecosystem.

### The Key Structural Insight for Nomi

**Ship the build tool with the compiler.** Cargo's success is not primarily
about TOML, or lockfiles, or crates.io. It's about the fact that `rustup`
installs `rustc` and `cargo` together, and every Rust tutorial, book, and
conference talk assumes Cargo. There is no "how do I build Rust code without
Cargo" question because the answer is "you don't." **The package manager must
be as fundamental as the compiler.** Python's packaging is separate from
Python, and the community has paid for that separation for 25 years. Rust's
packaging *is* Rust, and the community has benefited from that unity for a
decade.

---

## 3. Go Modules

### Core Design Philosophy

Go's packaging philosophy is **simplicity maximalism applied to dependency
management.** The Go team refused to ship a package manager for eight years
after Go 1.0 (2012), arguing that the community needed time to discover the
right design through experimentation. The result, Go modules (2018), reflects
the same "less is exponentially more" philosophy as the language: minimum
version selection instead of maximal version resolution, no lockfile in the
traditional sense, and module paths as URLs.

### What Worked Exceptionally Well

**Module paths as URLs.** A Go module's identity is its import path, and the
import path is a URL: `github.com/spf13/cobra`, `golang.org/x/net`. This means:
- The module path *is* the download location. No separate registry URL.
- Private modules work by pointing the path at a private Git server (via
  `GOPRIVATE` and `.netrc` or `GOPROXY`).
- Forking is trivial: `replace github.com/foo/bar => github.com/myfork/bar`
  in `go.mod`.
- Discovery is decentralized — if you know the import path, you know where to
  find the source.

This is a genuinely elegant conflation of identity and location that avoids the
"registry as single point of failure" problem while preserving a global
namespace.

**Minimum Version Selection (MVS).** Go's dependency resolution algorithm is
unique and deliberately simple. Instead of solving for the *maximum* compatible
version (like pip, npm, Cargo), MVS selects the *minimum* version that
satisfies all requirements:

```
A requires B >= 1.2.0
C requires B >= 1.3.0
→ MVS selects B 1.3.0 (minimum that satisfies both)
```

The insight: **in a semantic versioning world where all versions are backward
compatible, the minimum version that satisfies all constraints is always
correct.** MVS is deterministic (no SAT solving), fast (linear in the number of
modules), and produces builds that are stable by default (newer versions of
transitive dependencies are never pulled in unless a direct dependency
explicitly requires them).

**`go.mod` and `go.sum` as a stable pair.** `go.mod` records direct
dependencies and their minimum versions. `go.sum` records the SHA-256 hashes of
all module content (direct and transitive). Together they guarantee that a
build uses exactly the same source code. `go.sum` is not a lockfile — it
doesn't pin versions — but it *does* guarantee content integrity. This
separation of concerns (versions in `go.mod`, integrity in `go.sum`) is
cleaner than Cargo's single `Cargo.lock` or npm's single `package-lock.json`.

**`go mod tidy` as the cleanup command.** Running `go mod tidy` removes unused
dependencies from `go.mod` and adds any missing ones. This is a simple,
memorable command that keeps `go.mod` minimal. The Go philosophy: **the tool
should maintain the manifest, not the human.** Python's `requirements.txt`
requires humans to remember to add and remove entries; Go's `go.mod` is
maintained by `go mod tidy`.

**GOPROXY as a caching and security layer.** The `GOPROXY` protocol provides a
caching proxy between developers and module sources. `proxy.golang.org` (the
public proxy) caches modules indefinitely, even if the original source
disappears. This is a direct response to the npm left-pad incident: **a
centralized, immutable cache prevents dependency disappearance.** Private
organizations can run their own proxies for internal modules and auditing.

**`internal/` packages for module-level encapsulation.** The `internal/`
directory convention provides compilation-enforced encapsulation within a Go
module. A package at `example.com/mymodule/internal/auth` can only be imported
by code within `example.com/mymodule/`. This is a simple, zero-config answer to
"how do I hide implementation details within my module?"

### What Failed or Caused Persistent Friction

**The GOPATH decade (2012-2018).** Before Go modules, all Go code had to live
under `$GOPATH/src`. This enforced a single, global workspace for all projects
and made working on multiple versions of a dependency simultaneously
impossible. The `vendor/` directory (`go vendor`) was a partial fix that
introduced its own problems: vendored dependencies could diverge from
`Gopkg.toml`/`Gopkg.lock`, and the community split across dep, glide, godep,
govendor, and gb before finally converging on modules.

**Major version suffixes in module paths.** Go modules encode major versions in
the import path: `github.com/foo/bar/v2`. This means a v2 module is a
*different module* from a v1 module — they can coexist in the same dependency
graph. This solves the "two consumers need different major versions" problem
cleanly, but at the cost of import-path gymnastics: every import in the v2
module must say `github.com/foo/bar/v2/...`. When you cut a v3, every import
must change again. Tooling (`gofmt -r`, `gomodify`) helps, but the ergonomics
are worse than Cargo's `version = "2"`.

**`replace` directives as a footgun.** The `replace` directive in `go.mod`
redirects a module path to a different location (local directory, fork, or
different version). It is deliberately not propagated to consumers — your
`replace` directives only affect your own build. This is correct for local
development but confusing: a library that uses `replace` for development
testing publishes a `go.mod` without the `replace`, and consumers get the
original dependency, not the replacement. This creates a class of "works in
development, breaks in production" bugs.

**Module path as identity is also module path as lock-in.** Because the module
path is a URL and appears in every import, changing a module's hosting location
requires updating every import site. Moving from GitHub to GitLab requires
changing every `import "github.com/..."` to `import "gitlab.com/..."`. The Go
ecosystem handles this through redirects and the `go-import` meta tag, but the
coupling between source location and code identity is real.

### The Key Structural Insight for Nomi

**Minimum Version Selection is a design philosophy, not just an algorithm.**
MVS encodes a value judgment: builds should be as stable as possible, and newer
versions should only be pulled in by explicit action. This is the opposite of
npm's "latest compatible" / Cargo's "max version" approach, which defaults to
using the newest available version. For a language that cares about
reproducibility and local reasoning (as Nomi does), MVS is the right
philosophical alignment: **the default should be stability, not novelty.**

---

## 4. Mix (Elixir)

### Core Design Philosophy

Mix is Elixir's answer to "what should a build tool look like?" It is a
build tool, task runner, test runner, and package manager in one. The
philosophy is **convention-driven project management with an escape hatch into
the full language.** `mix.exs` is an Elixir script, not a declarative config
file — but the conventions are so strong that 95% of projects never need to
write custom build logic.

### What Worked Exceptionally Well

**`mix new` as complete project scaffolding.** `mix new my_app` creates a
directory with `mix.exs`, `lib/`, `test/`, `.formatter.exs`, `.gitignore`, and
a `README.md`. `mix new my_app --umbrella` creates an umbrella project with an
`apps/` directory. The generated project has a working test, a working `mix
compile`, and a working `mix test` — zero configuration required. The generated
`mix.exs` is readable:

```elixir
defmodule MyApp.MixProject do
  use Mix.Project

  def project do
    [
      app: :my_app,
      version: "0.1.0",
      elixir: "~> 1.17",
      deps: deps()
    ]
  end

  defp deps do
    [
      {:jason, "~> 1.4"},
      {:plug_cowboy, "~> 2.0"},
      {:credo, "~> 1.7", only: [:dev, :test], runtime: false}
    ]
  end
end
```

**Hex.pm and the task system.** `mix hex.publish` publishes a package to
Hex.pm. `mix hex.search term` searches for packages. `hex` is integrated into
Mix as a set of tasks — no separate CLI, no separate account system, no
separate configuration. The `mix help` output lists all available tasks,
including those added by dependencies. This is the "batteries included"
approach done right: **the single `mix` command is the entry point for
everything.**

**Umbrella projects for monorepos.** `mix new --umbrella` creates a project
structure where independent applications live under `apps/` and share a single
`mix.lock`. Each app has its own `mix.exs` and dependency list, but the
umbrella resolves them together. This is Elixir's answer to Cargo workspaces or
npm workspaces — and it was available in Mix 1.0 (2014), years before npm
workspaces (2020) or Cargo workspaces (2015).

**Environment-based dependency scoping.** Dependencies in Mix can be scoped to
specific environments: `only: :dev`, `only: [:dev, :test]`. The `runtime: false`
flag means the dependency is loaded at compile time but not at runtime — the
Elixir equivalent of Cargo's `dev-dependencies`. The environment system (`:dev`,
`:test`, `:prod`) is built into Mix and controls compilation, dependency
loading, and configuration.

**The `config/` directory for hierarchical configuration.** Configuration in
Elixir projects follows a convention: `config/config.exs` for shared config,
`config/dev.exs` for development overrides, `config/prod.exs` for production
overrides, and `config/runtime.exs` for configuration that must be evaluated at
runtime (secrets, environment-specific values). This is a disciplined
alternative to the "one `.env` file per environment" approach that Python and
Node.js use.

### What Failed or Caused Persistent Friction

**`mix.exs` as executable code.** Because `mix.exs` is an Elixir script, it can
contain arbitrary logic: conditional dependencies, environment-variable reads,
git-based dependencies. This is powerful but makes static analysis of
dependencies impossible. Most projects stick to the `deps()` function pattern,
but the escape hatch exists and is used.

**Hex.pm's permission model.** Publishing a hex package is tied to an account.
Revoking or transferring a package requires account access. There is no
namespacing — package names are flat and first-come-first-served. This mirrors
crates.io's historical model and has the same squatting risk, though Elixir's
smaller ecosystem makes it less acute.

**Transitive dependency conflicts.** `mix deps.get` resolves dependency
versions using a simple "highest compatible" strategy. If two dependencies
require conflicting versions of a shared dependency, Mix reports an error and
the developer must manually resolve it. There is no SAT solver and no
automatic conflict resolution — by design. This works for Elixir's ecosystem
size but would break at npm's scale.

**Umbrella project build ordering.** An umbrella builds apps in dependency
order (if A depends on B, B builds first). Circular dependencies between apps
are caught at build time. But the build order is not always intuitive — a
change in a shared library requires rebuilding all consumers, and the error
messages when an app isn't found are not great.

### The Key Structural Insight for Nomi

**Project generation as a learning tool.** `mix new` is not just a file
creator — it's a teaching tool. The generated project shows a new Elixir
developer exactly where code, tests, configuration, and documentation live.
Nomi should adopt this: `nomi new my_project` should produce a working,
testable project in one command, with comments in the generated files that
explain what each file is for.

---

## 5. npm / Node.js

### Core Design Philosophy

npm is the largest package ecosystem in history (3+ million packages) and the
most unplanned. Its philosophy is **"the registry is the platform":** any
package can depend on any other, discovery is through npmjs.com, and
`node_modules` is a recursive directory of installed packages. The Node.js
ecosystem has succeeded at scale despite — and sometimes because of — design
decisions that every other packaging system considers mistakes.

### What Worked Exceptionally Well

**The sheer scale of the ecosystem.** npm has 3+ million packages. A `require`
of almost any JavaScript utility has a published package ready to use. This
scale is a genuine feature: the time from "I need an X" to `npm install X` is
often under 30 seconds. Low barrier to publishing (no review, no vetting,
free) created the network effects.

**Semantic versioning infrastructure.** npm's semver range syntax is the most
expressive in any package manager:
- `^1.2.3` — compatible with 1.2.3 (>=1.2.3 <2.0.0)
- `~1.2.3` — approximately equivalent (>=1.2.3 <1.3.0)
- `>=1.2.3 <2.0.0 || >=3.0.0` — union of ranges
- `1.2.x` — any patch of 1.2
- `latest`, `next`, `beta` — dist-tags

This expressiveness lets library authors communicate compatibility intent
precisely — when it's used correctly. The problem is that it is often not used
correctly (see below).

**`npx` for one-shot execution.** `npx create-react-app my-app` downloads and
executes a package without installing it globally. This eliminated a whole
category of "how do I install this tool globally" problems and the associated
permission and PATH issues. The `npm exec` / `npx` pattern is now standard
across package managers (Cargo's `cargo install` has a similar pattern).

**Workspaces (npm 7+, 2020).** npm workspaces allow a single top-level
`package.json` to manage multiple packages in a monorepo. `npm install` at the
root installs dependencies for all workspaces and hoists shared dependencies to
the root `node_modules`. This is a relatively late addition (npm was 11 years
old) but well-designed: workspace configuration in `package.json`, shared
lockfile, and `npm test --workspaces` runs tests across all packages.

**Audit and security infrastructure.** `npm audit` scans the dependency tree
for known vulnerabilities and suggests fixes. `npm audit fix` automatically
updates packages to patched versions when the semver range allows. The
ecosystem has a shared vulnerability database (GitHub Advisory Database) and
publishing 2FA requirements. This security infrastructure is more mature than
any other language ecosystem.

**`package-lock.json` (npm 5+, 2017).** The lockfile records the exact version,
integrity hash, and resolution URL of every package in the tree. It guarantees
that `npm ci` (clean install) produces an identical `node_modules` tree.
`npm ci` is the CI/CD equivalent of `npm install` — it fails if
`package-lock.json` is out of sync with `package.json`, which catches the
"forgot to commit the lockfile" problem.

### What Failed or Caused Persistent Friction

**`node_modules` size and depth.** A typical React project's `node_modules` is
200-500 MB and contains thousands of directories. The recursive `node_modules`
layout — where `A/node_modules/B/node_modules/C` is possible if A and B need
different versions of C — was necessary for version isolation but created a
directory structure that is hard to inspect, hard to clean, and hard to
understand. `npm dedupe` helps but cannot always flatten the tree.

**The left-pad incident (2016).** A developer unpublished 11 lines of code
(`left-pad`) from npm, breaking thousands of dependent projects — including
React and Babel. This demonstrated that the npm ecosystem's dependency graph
was dangerously fragile: critical infrastructure depended on tiny,
single-maintainer packages with no guarantee of continued availability. The
response — npm's "packages cannot be unpublished after 72 hours" policy — was a
band-aid. The structural problem is that `require` encourages dependency
sprawl.

**Micropackage culture.** npm's ecosystem has packages that implement a single
line of code: `is-positive`, `is-negative`, `is-odd`, `is-even` (where
`is-even` depends on `is-odd`). This is possible because there is zero cost to
creating a package and zero friction to depending on one. Some of this is the
Unix philosophy ("do one thing well") applied to npm packages, but at extreme
scale, the dependency trees become incomprehensible. The median npm package has
79 transitive dependencies.

**`package.json` as a kitchen sink.** A modern `package.json` contains:
dependencies, devDependencies, peerDependencies, optionalDependencies,
scripts, config, jest config, eslint config, babel config, prettier config,
TypeScript config, browserslist, engines, os, cpu, exports, types, main,
module, and browser fields. It is a configuration file, a build script, a
test runner config, a linter config, and a deployment manifest — often 100+
lines. This is not a design failing of npm itself but a consequence of the
ecosystem using `package.json` as the only universally available configuration
surface.

**`peerDependencies` as a confused concept.** npm's `peerDependencies` (npm 3+)
specifies that a package is compatible with a host-provided version of a
dependency but doesn't install it. This is necessary for plugin architectures
(a React component plugin needs React to be present but shouldn't install its
own copy). But `peerDependencies` semantics have changed across npm versions,
causing installation failures that are hard to diagnose. npm 7 auto-installs
peer dependencies; npm 6 didn't. The migration pain was significant.

### The Key Structural Insight for Nomi

**The cost of zero-friction dependency addition is invisible until it isn't.**
npm made adding a dependency as easy as `npm install left-pad`. The result was
a culture where depending on 500+ packages is normal and dependency trees are
too large to audit. Every package manager needs *some* friction at the
"add a dependency" step — not to prevent adding dependencies, but to make the
cost visible. **The dependency tree should be something a single developer can
reason about.** If your project has 800 transitive dependencies, you do not
understand your supply chain, and no tool can fully compensate for that.

---

## 6. NuGet (.NET / C#)

### Core Design Philosophy

NuGet is the .NET ecosystem's package manager, and its philosophy is
**integration with the project system.** Packages are not something you manage
separately from the build — they are part of the project file. The transition
from `packages.config` (XML file listing packages) to `PackageReference`
(MSBuild items in the `.csproj` file) is NuGet's key design evolution: **move
dependency declaration from a separate file into the build system itself.**

### What Worked Exceptionally Well

**PackageReference: dependencies as build items.** In modern .NET projects,
dependencies are MSBuild items in the `.csproj` file:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageReference Include="Serilog" Version="4.0.0" />
  </ItemGroup>
</Project>
```

This means:
- There is one file (`.csproj`) that describes the project, its dependencies,
  its target framework, and its build settings. No separate manifest.
- Dependencies are resolved during the MSBuild restore phase, not as a separate
  step. `dotnet build` implicitly runs `dotnet restore`.
- The `packages.lock.json` (opt-in) provides reproducible restores for CI/CD.

**Centralized Package Management (CPM).** A newer feature where a
`Directory.Packages.props` file at the solution root declares package versions
centrally. Individual projects reference packages by name only, and the version
comes from the central file. This eliminates version drift across projects in a
solution:

```xml
<!-- Directory.Packages.props -->
<Project>
  <ItemGroup>
    <PackageVersion Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageVersion Include="Serilog" Version="4.0.0" />
  </ItemGroup>
</Project>

<!-- In each .csproj: -->
<PackageReference Include="Newtonsoft.Json" />  <!-- version from central file -->
```

**NuGet Gallery (nuget.org) and package immutability.** Published packages are
immutable — once a version is published, it cannot be changed. Packages can be
unlisted (hidden from search, but still downloadable by exact version) or
deprecated (with a message suggesting an alternative). There is a 24-hour
window after publishing during which the package can be deleted, after which it
is permanent.

**Microsoft's ecosystem stewardship.** Because .NET is backed by Microsoft,
NuGet benefits from curated packages (Microsoft.Extensions.*) that provide
standard implementations for dependency injection, logging, configuration,
and HTTP. These are maintained, documented, and versioned together. This is a
form of "blessed dependencies" that smaller ecosystems cannot provide.

### What Failed or Caused Persistent Friction

**The `packages.config` to `PackageReference` migration.** The two formats
coexisted for years, and migration was manual and error-prone. Projects created
with older templates (`packages.config`) behaved differently from new projects
(`PackageReference`) in subtle ways: `packages.config` required a separate
`packages/` directory, used different restore mechanics, and had different
transitive-dependency behavior. This is the same kind of "legacy format
persists forever" problem that Python faces with `setup.py`.

**Assembly binding redirects.** .NET Framework's strong naming and assembly
versioning meant that when two dependencies required different versions of the
same assembly, the runtime needed XML binding redirects in `app.config` /
`web.config`. These were generated by NuGet and were a constant source of
runtime failures when they were incomplete or incorrect. .NET Core / .NET 5+
eliminated this entirely by changing the assembly loading model, but the scars
remain.

**Transitive dependency pinning.** Before CPM, managing transitive dependency
versions required adding explicit `PackageReference` entries for transitive
packages just to pin their versions. This is the "transitive dependency
management" problem that Cargo handles with `[patch]` and CPM now handles with
centralized versioning, but for years, the answer was "add it to your project
file even though you don't directly use it."

**The `dotnet` CLI verb sprawl.** `dotnet restore`, `dotnet build`, `dotnet
run`, `dotnet test`, `dotnet publish`, `dotnet pack`, `dotnet nuget push`,
`dotnet nuget delete`, `dotnet nuget locals`, `dotnet tool install`, `dotnet
tool run` — the CLI has grown organically and the verb space is not obviously
organized. Contrast with Cargo's clean verb set (`build`, `test`, `run`,
`doc`, `publish`, `add`, `remove`) and the difference in discoverability is
clear.

### The Key Structural Insight for Nomi

**Centralized package version management across projects is a real need.**
NuGet's CPM feature solves a problem that every multi-project ecosystem
eventually faces: how to keep dependency versions consistent across dozens of
projects. Nomi should design this in from the start — a single place where
version constraints for the entire workspace are declared, with per-project
overrides where needed.

---

## 7. Nix Flakes

### Core Design Philosophy

Nix flakes represent the **reproducibility maximalist** approach to packaging.
The core philosophy: every build should be a pure function of its declared
inputs, producing the same output on every machine, at every point in time,
forever. Flakes extend this to project structure: a `flake.nix` declares
inputs, outputs, and development shells in a single file, and `flake.lock`
pins every input to an exact content hash.

### What Worked Exceptionally Well

**Content-addressed dependency resolution.** Nix identifies dependencies by
their content hash (SHA-256 of all inputs), not by version string. A package
`foo-1.2.3` that is rebuilt with a different compiler flag gets a different
hash and is a *different package* — there is no ambiguity about which version
is meant. Nix stores every package in `/nix/store/<hash>-<name>-<version>/`,
and the hash changes if any input changes. This means:
- Two users with the same `flake.lock` build the exact same binaries.
- Upgrading a dependency changes its hash, which changes the hashes of
  everything that depends on it (structural sharing means unchanged artifacts
  are reused from the binary cache).
- You can have 50 versions of `openssl` installed simultaneously, each at a
  different path, with no conflicts.

**`flake.nix` as a unified description format.** A flake describes:
- **Inputs** (dependencies — other flakes, Git repos, tarballs)
- **Outputs** (packages, NixOS modules, templates, checks, apps)
- **Dev shells** (development environments with specific tool versions)

```nix
{
  description = "A reproducible Nomi development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in {
        packages.default = pkgs.stdenv.mkDerivation {
          name = "nomi";
          src = self;
          buildInputs = [ pkgs.python3 ];
        };
        devShells.default = pkgs.mkShell {
          buildInputs = [ pkgs.python3 pkgs.lark ];
        };
      }
    );
}
```

**Dev shells as executable environments.** `nix develop` (or `nix shell`)
drops you into a shell where exactly the declared dependencies are available —
no system Python leaking in, no global `node` overriding the pinned version.
This is `virtualenv` done right: the shell is a pure function of the flake.
`direnv` integration makes it automatic when you `cd` into the project
directory.

**Binary cache and substituters.** Nix builds can be substituted from a binary
cache (`cache.nixos.org`). If the hash of every input matches, the build output
is fetched rather than rebuilt. This means CI can build once, and every
developer and deployment gets the cached result. The content-addressable model
makes caching always correct — there is no "cache is stale because a new
version was published" problem because a different version has a different
hash.

**The lockfile as a verifiable artifact.** `flake.lock` records the exact Git
revision and NarHash of every input. Running `nix flake update` updates the
lockfile. Running `nix build` uses the lockfile without network access. This
separation — update and build are distinct operations — means you can inspect,
commit, and review dependency updates before they affect builds.

### What Failed or Caused Persistent Friction

**The Nix language learning curve.** Nix uses its own functional language for
package definitions, and it is not a general-purpose language. It has lazy
evaluation, attribute sets, `with` expressions, and a string interpolation
syntax that is unique to Nix. Learning to read and write Nix derivations is a
significant investment — measured in weeks, not hours. The "write package
definitions in a specialized language" approach gives reproducibility at the
cost of accessibility.

**Flakes are still experimental.** As of 2026, flakes remain behind a feature
flag (`experimental-features = nix-command flakes`). The Nix ecosystem is split
between the "new" flake workflow and the "old" channel workflow. Documentation
is split, tooling is split, and new users encounter both approaches with no
clear guidance on which to use.

**MacOS and platform divergence.** Nix works on macOS, but many packages in
nixpkgs have platform-specific build failures. A `flake.lock` that works on
Linux may not work on macOS because a transitive dependency's build recipe
fails on Darwin. This violates the "works everywhere" promise in practice, even
though the theory is sound.

**No central registry; GitHub as a single point of failure.** Flakes reference
inputs by URL, typically `github:owner/repo`. If GitHub is down, or a repo is
deleted, or a tag is force-pushed, flakes that depend on it break. `flake.lock`
pins to a specific revision, which mitigates the force-push risk, but the
source-of-truth is still GitHub — a centralized dependency.

### The Key Structural Insight for Nomi

**Content-addressed storage makes caching always correct.** Nix's insight is
not about the language or the flakes format — it's about using content hashes
as universal identifiers. When a package's identity is its content hash, you
can cache it anywhere, share it without trust, and verify it without a PKI.
Nomi may not want to go full Nix (the complexity cost is real), but
content-addressed artifacts for Nomi packages is a design direction worth
exploring — especially given Nomi's interest in data boundaries and
reproducible computation.

---

## 8. Java / Maven / Gradle

### Core Design Philosophy

Java's packaging tradition is the oldest of any system analyzed here (Maven
dates to 2004). Its philosophy is **convention over configuration** — if you
put your code in `src/main/java` and your tests in `src/test/java`, the build
system knows what to do. The POM (Project Object Model) is the declarative
description of the project, and Maven Central is the universal registry.

### What Worked Exceptionally Well

**Maven Central's longevity and stability.** Maven Central has been operating
continuously since 2004 with zero data loss incidents. Packages published in
2005 are still downloadable today. The requirements for publishing (domain
verification, PGP signing, Javadoc, sources JAR) are higher than npm/PyPI, but
the result is a registry where you can depend on a 15-year-old artifact and it
will be there, with sources and documentation.

**`pom.xml` as a universal project descriptor.** A Maven POM declares:
- Coordinates: `groupId`, `artifactId`, `version` (GAV)
- Dependencies with scope (`compile`, `test`, `provided`, `runtime`)
- Build configuration (compiler settings, plugins, resources)
- Parent POM reference (inheritance of configuration)
- Multi-module aggregation

```xml
<project>
  <groupId>com.nomi</groupId>
  <artifactId>nomi-core</artifactId>
  <version>0.1.0-SNAPSHOT</version>

  <dependencies>
    <dependency>
      <groupId>com.google.guava</groupId>
      <artifactId>guava</artifactId>
      <version>33.0.0-jre</version>
    </dependency>
    <dependency>
      <groupId>org.junit.jupiter</groupId>
      <artifactId>junit-jupiter</artifactId>
      <version>5.10.0</version>
      <scope>test</scope>
    </dependency>
  </dependencies>
</project>
```

**Dependency scopes.** Maven's scope system is the most sophisticated in any
package manager:
- `compile` — available everywhere (default)
- `test` — only in test compilation and execution
- `provided` — available at compile time, provided by the runtime (like
  servlet-api)
- `runtime` — not needed for compilation, needed for execution (JDBC drivers)

This is the same concept as Cargo's `[dev-dependencies]` and npm's
`devDependencies`, but Maven had it from the beginning (2004).

**The Bill of Materials (BOM) pattern.** A BOM POM declares a set of
compatible dependency versions without pulling them all in. You depend on the
BOM, and then you declare the specific artifacts you use without specifying
versions. This is Java's answer to "how do I keep 50 Spring libraries at
compatible versions?" and it works well:

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-dependencies</artifactId>
      <version>3.3.0</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

**Gradle's incremental improvements.** Gradle (2012) replaced Maven's verbose
XML with Groovy/Kotlin DSLs, added incremental compilation, build caching, and
a daemon for fast startup. `build.gradle.kts` is more concise and programmable
than `pom.xml`, but Gradle preserves the same repository and dependency
concepts. The lesson: **you can change the build language without changing the
packaging model.**

### What Failed or Caused Persistent Friction

**Maven's XML verbosity and rigidity.** A minimal `pom.xml` is 20 lines. A
typical project POM is 200+ lines. The XML is verbose, the plugin configuration
is XML-inside-XML, and Maven's lifecycle bindings (validate, compile, test,
package, verify, install, deploy) are rigid. If your build step doesn't fit
Maven's lifecycle, you write a plugin — which requires a separate Maven project
in Java. This is a high barrier for what should be a one-line script.

**Maven vs Gradle ecosystem split.** The Java ecosystem has been split between
Maven and Gradle for over a decade. Android chose Gradle. Spring chose Maven
(with Gradle support). Kotlin prefers Gradle. The result: every Java developer
needs to be literate in both, and migration between them is painful. This is
the same fragmentation pattern that Python's `setup.py` vs `pyproject.toml` and
Go's `dep` vs `modules` suffered from.

**Diamond dependency conflicts.** Maven's "nearest definition wins" strategy
for resolving conflicting transitive dependency versions is simple but
surprising: if A -> B -> C:2.0 and A -> D -> C:1.0, Maven chooses C:1.0
(nearest to A in the dependency tree). This can silently break code that
depends on C:2.0's API. Gradle defaults to "highest version wins" which is
also surprising but in a different way. The structural problem is that Java
has no mechanism for two versions of the same library to coexist in a single
classloader.

**`SNAPSHOT` version chaos.** Maven's `SNAPSHOT` versions (`1.0-SNAPSHOT`)
are mutable — every build downloads the latest snapshot from the repository.
This was intended for rapid development but creates non-reproducible builds:
two builds with the same `pom.xml` can produce different results depending on
when someone last published the snapshot. Modern practice is to avoid
`SNAPSHOT` dependencies entirely, but they persist in older projects.

**Gradle's performance complexity.** Gradle is fast when configured correctly
(build cache, configuration cache, parallel execution, daemon). But getting the
configuration right requires deep Gradle knowledge, and the documentation
describes an ideal configuration that few projects achieve. The "fast builds"
promise is gated on expertise.

### The Key Structural Insight for Nomi

**Convention over configuration is the right philosophy for project structure.**
Maven's "put source in `src/main/java`, tests in `src/test/java`" is 20 years
old and still the standard for every JVM language. It eliminated the "where do
I put files?" question for an entire ecosystem. Nomi should define a project
layout convention and enforce it with tooling — not as a restriction, but as a
default that eliminates trivial decisions. Every project should look the same
at the directory level.

---

## 9. Cross-Language Synthesis

### 9.1 Structural Invariants (Patterns Across All Successful Systems)

These are features that appear in every mature packaging system, regardless of
language or era. They represent convergence, not fashion — a new packaging
system that omits them will eventually add them.

**1. A single, declarative manifest file at the project root.**
Every system converges on this. The format varies (TOML for Cargo, JSON for
npm, XML for Maven, Elixir script for Mix, `.go` format for Go), but the
pattern is universal: one file that a tool can read to understand the project's
identity, dependencies, and build configuration. The older systems (Python's
`setup.py`, Java's Ant) started without this and migrated toward it.

**2. A lockfile separate from the manifest.**
Every system eventually adds this. The manifest declares *what* you depend on;
the lockfile records *exactly what was resolved.* Cargo has `Cargo.lock`, Go
has `go.sum` (integrity only), npm has `package-lock.json`, Mix has `mix.lock`,
Nix has `flake.lock`. Python is the notable holdout that still lacks a
universal lockfile format. A packaging system without a lockfile eventually
suffers from "works on my machine" builds.

**3. A central registry with immutable published artifacts.**
Every ecosystem discovers that mutability in the registry is a disaster. npm's
left-pad incident (unpublishable packages), Maven's SNAPSHOT chaos (mutable
versions), and PyPI's historical deletion policy all converged toward
immutability. Artifacts can be deprecated, yanked, or hidden — but never
deleted. The exact policy varies (npm's 72-hour window, NuGet's 24-hour
window, crates.io's immediate yank-but-not-delete), but the principle is
universal.

**4. Semantic versioning (or something like it) as the compatibility language.**
Every system uses version numbers to communicate compatibility. npm, Cargo,
and Mix use semver explicitly. Maven and NuGet use a looser convention but the
concept is the same: a breaking change means a new major version. Python's PEP
440 is a formalization that postdates the practice. The universality of version
numbers as compatibility signals is striking — no system has proposed an
alternative that gained traction.

**5. Development-only and runtime-only dependency separation.**
Every system distinguishes between dependencies needed to build/test the
project and dependencies needed to run it. Cargo has `[dev-dependencies]`, npm
has `devDependencies`, Maven has `<scope>test</scope>`, Mix has `only: :test`.
This is not optional — if users install your library and pull in your test
framework, that is a broken packaging model.

**6. A standard project layout convention.**
The directory structure for a project with source code, tests, and
configuration is one of the first things a packaging system defines. Maven's
`src/main/java` + `src/test/java` is the oldest and most influential. Cargo's
`src/main.rs` + `src/lib.rs` + `tests/` is the most elegant. Go's
one-directory-per-package is the simplest. The convention matters more than the
specific layout — it means tooling can find code without configuration.

**7. The package manager ships with the compiler/runtime.**
Every language released after 2010 that succeeded at packaging (Rust, Go, Zig,
Elixir) shipped the package manager as part of the language distribution.
Languages where packaging is a separate project (Python, C/C++, Java before
Maven) have permanently fragmented packaging ecosystems.

### 9.2 Genuine Design Forks (Where Ecosystems Made Different Tradeoffs)

These are places where different packaging systems made genuinely different
choices, and both choices are defensible. They represent the design space Nomi
must navigate.

**1. Manifest format: declarative data vs executable code.**
| Approach | Systems | Pros | Cons |
|----------|---------|------|------|
| Declarative data (TOML/JSON/XML) | Cargo, npm, Maven, NuGet | Static analysis, tool-safe editing | Limited expressiveness, needs config language |
| Executable code in the language | Mix (Elixir), setuptools (Python), Gradle (Groovy/Kotlin) | Full power, no second language | Static analysis impossible, harder to tool |

The systems that chose executable manifests all eventually added constraints to
rein in the expressiveness. The systems that chose declarative manifests all
eventually added escape hatches for the cases that don't fit. The sweet spot is
a declarative manifest with a well-defined escape hatch — like Cargo's
`build.rs` (constrained to build-time only, not dependency resolution).

**2. Dependency resolution: SAT solver vs MVS vs backtracking vs highest-wins.**
| Algorithm | Systems | Properties |
|-----------|---------|------------|
| SAT solving (Pubgrub) | Pub (Dart), modern pip, modern npm | Complete, can be slow, opaque error messages |
| Minimum Version Selection | Go modules | Fast, deterministic, stable by default |
| Backtracking with heuristics | Cargo | Complete, heuristic-dependent, good errors |
| Nearest-definition / highest-version | Maven, Gradle | Fast, simple, can be surprising |

Each approach makes a different bet on the stability vs novelty tradeoff. MVS
is the most conservative (stick to the minimum version), backtracking
algorithms are the most accommodating (find *some* solution), and SAT solvers
are the most principled (find a complete solution or prove none exists).

**3. Dependency identity: name vs URL.**
| Identity model | Systems | Tradeoff |
|----------------|---------|----------|
| Name (registry-scoped) | Cargo, npm, NuGet, PyPI, Hex | Simple, flat, enables squatting |
| URL (path is identity) | Go modules, Nix flakes | Decentralized, self-describing, ties identity to location |
| Namespaced name (org/name) | Maven (groupId:artifactId), npm scopes | Solves flat namespace problem, adds prefix |

Go's URL-as-identity is the most radical choice. It means a module's import
path *is* its download location, and private modules work by pointing the URL
at a private Git server. The cost is that changing hosting requires changing
every import. Maven's `groupId:artifactId` is the most practical — a namespaced
name that is decoupled from hosting location.

**4. Multi-project structure: workspace vs umbrella vs solution.**
| Model | Systems | Characteristic |
|-------|---------|----------------|
| Workspace (shared lockfile, independent config) | Cargo, npm, Yarn, pnpm | Members share dependency resolution but have own manifests |
| Umbrella (nested apps, shared config) | Mix (Elixir) | Each app has full independence, root orchestrates |
| Solution (project references, shared version management) | .NET (NuGet + CPM) | Centralized version management, project-level dependency declaration |
| Multi-module (parent POM, inheritance) | Maven, Gradle | Parent defines common config, children inherit |

All four models work. The key requirement is that they *exist* — a packaging
system that doesn't have a multi-project story (Python's is still weak) forces
users into ad-hoc solutions.

**5. Feature flags / conditional compilation.**
Cargo has the most sophisticated feature system: optional dependencies, feature
flags, feature unification, and `cfg` attributes for conditional compilation.
Mix has environment-based dependency scoping (`only: :test`). npm has `os`,
`cpu`, and `engines` fields for platform constraints. Maven has profiles. No
two systems agree on how features should work.

**6. Patching/overriding dependencies.**
Cargo's `[patch]` section allows overriding any dependency in the tree with a
custom version — essential for testing against a fork. Go's `replace` directive
does the same but deliberately doesn't propagate to consumers (a library's
`replace` doesn't affect its dependents). npm's `overrides` (npm 8.3+) provides
selective version pinning in the dependency tree. The tradeoff is between
developer convenience (easy patching) and consumer safety (patching should not
leak).

**7. Build scripts / code generation.**
Cargo has `build.rs` (arbitrary Rust, runs before compilation). npm has
`scripts` in `package.json` (shell commands). Maven has plugins (Java code,
packaged as Maven artifacts). Gradle uses the build language itself (Groovy or
Kotlin). Mix uses Elixir tasks. The spectrum runs from "arbitrary code you
write" (Cargo) to "pre-built plugins you configure" (Maven) to "shell commands
in the manifest" (npm). Each has different tradeoffs for power, portability,
and reproducibility.

### 9.3 The Manifest File Design Space

The manifest file is the primary human interface to the packaging system. The
format choice has deep consequences.

**TOML** (Cargo, Poetry, pyproject.toml):
- Pro: Hierarchical, comments, clear types (string vs array vs table), the
  de facto standard for new packaging systems.
- Con: Verbose for deeply nested structures; not a universal data format (no
  JSON Schema equivalent).

**JSON** (npm, Composer):
- Pro: Universal parsers, JSON Schema for validation, familiar to every web
  developer.
- Con: No comments (JSONC partially addresses this), verbose for humans,
  trailing comma sensitivity.

**XML** (Maven, NuGet packages.config):
- Pro: Schema validation (XSD), namespaces, document-oriented, well-understood
  namespace model.
- Con: Verbose, hard to read, hard to write by hand, deeply nested syntax for
  simple things.

**Custom format** (Go modules `go.mod`, Nix `flake.nix`):
- Pro: Can be optimized for the specific use case, can embed language semantics.
- Con: New syntax to learn, no existing tooling, parser must be written and
  maintained.

**Executable code** (Mix `mix.exs`, Gradle `build.gradle.kts`, setuptools
`setup.py`):
- Pro: No second language, full expressiveness, can call functions for complex
  cases.
- Con: Not statically analyzable, harder to auto-edit with tooling, can do
  anything (including break the build system).

**The emerging consensus:** TOML for declarative manifests, with a well-defined
extension mechanism for build logic that cannot be expressed declaratively.
Cargo's combination (`Cargo.toml` + `build.rs`) is the closest to an optimal
design: the manifest is pure data (TOML), and the escape hatch is a separate
file with a clear contract.

### 9.4 Dependency Resolution Strategies Compared

| Dimension | MVS (Go) | Pubgrub (Dart, modern pip/npm) | Cargo resolver | Maven nearest-wins |
|-----------|----------|-------------------------------|----------------|-------------------|
| **Completeness** | Always terminates (linear) | Complete (SAT) | Complete (backtracking) | Always terminates |
| **Performance** | O(n) in dependency count | Worst-case exponential; fast in practice | Backtracking + heuristics; fast in practice | O(n) in tree depth |
| **Determinism** | Fully deterministic | Deterministic given same registry state | Deterministic given same lockfile | Deterministic |
| **Stability bias** | Prefers oldest compatible | Prefers newest compatible | Prefers newest compatible | Depends on tree structure |
| **Error messages** | Simple (version not found) | Detailed conflict explanations | Reasonable | Silent version conflicts |
| **Philosophy** | "Minimum change" | "Find the best solution" | "Find a good solution fast" | "Simplicity over correctness" |

The key axis is **stability vs novelty.** MVS says "don't upgrade anything
unless forced." Pubgrub and Cargo say "use the newest compatible versions."
Both are defensible, but the MVS approach is better aligned with Nomi's
emphasis on local reasoning and predictable behavior: **a build should not
change because a new version of a transitive dependency was published.**

### 9.5 The Workspace / Monorepo Question

Every packaging system eventually needs to support multi-project repositories.
The patterns that emerge:

**Shared lockfile + independent manifests** (Cargo, npm, Yarn):
- Each project has its own manifest declaring its dependencies.
- A workspace-level lockfile pins versions across all projects.
- `cargo test --workspace` tests everything.
- Strengths: simple to understand, each project is independently publishable.
- Weaknesses: version drift if a project is moved out of the workspace.

**Parent POM / centralized version management** (Maven, .NET CPM):
- A parent or central file declares versions for all projects.
- Individual projects declare the packages they use (by name only, or with
  version inherited).
- Strengths: enforces version consistency across the entire codebase.
- Weaknesses: version changes affect all projects; requires coordination.

**Umbrella projects** (Mix):
- A root project with independent "apps" underneath.
- Each app has its own dependency list; the umbrella resolves them together.
- Strengths: each app is a full-fledged project; eventual extraction is easy.
- Weaknesses: more boilerplate for small sub-projects.

**The single-repo-with-multiple-crates pattern** (Cargo, common in Rust):
- Multiple crates in one repo; often a `core` crate and several `*-impl` crates.
- Workspace-level `Cargo.toml` with `[workspace] members`.
- `cargo publish` for each crate independently.
- This is the most flexible pattern and the one that scales best.

For Nomi, the Cargo workspace model is the strongest starting point: shared
lockfile, independent manifests, workspace-level commands, and the ability to
publish each package independently.

### 9.6 Immutability and Reproducibility

The reproducibility spectrum:

```
Ad-hoc reproducibility  ────────────────────────────────  Hermetic reproducibility
(pip freeze > requirements.txt)                           (Nix flakes)
         │                          │                          │
   Python pip                Cargo + lockfile          Nix content-addressed
   (lockfile optional,       (lockfile standard,       (every input hashed,
    no integrity hashes)      registry immutable)       binary cache, pure builds)
```

**Lockfiles** are the minimum viable reproducibility mechanism. A lockfile says
"use exactly these versions." Without integrity hashes, it's still vulnerable
to registry tampering or source changes.

**Integrity hashes** (npm's `integrity`, Go's `go.sum`, Cargo's checksum in
`Cargo.lock`) add content verification. Even if the registry returns a
different file, the build will fail because the hash doesn't match.

**Vendoring** (Go's `vendor/`, Rust's `cargo vendor`, npm's `node_modules` that
you commit) makes the build fully offline by storing dependencies in the
repository. This gives maximum control at the cost of repository size and merge
conflicts.

**Content-addressed storage** (Nix) makes caching and sharing always correct.
Every artifact is identified by its content hash, so there is no "did someone
republish this version?" question — a different artifact has a different hash.

**Binary transparency / reproducible builds** (Debian, Nix, Bazel) verifies
that the source produces the claimed binary. This is the highest bar: given
source + build instructions, can you reproduce the binary byte-for-byte?

For Nomi, the baseline should be **lockfile + integrity hashes** (the Cargo/Go
model). Content-addressed storage and reproducible builds are aspirational
layers that can be added incrementally.

### 9.7 Anti-Patterns (Packaging Mistakes That Consistently Hurt Ecosystems)

**1. Mutable published artifacts.**
Maven's SNAPSHOT versions, npm's old deletion policy, PyPI's historical lack
of immutability — every ecosystem that allowed mutation of published artifacts
regretted it. Immutability must be the default from day one.

**2. Multiple competing package managers.**
Python (pip, poetry, pipenv, conda, uv), Java (Maven, Gradle, Ant+Ivy, sbt),
and JavaScript (npm, yarn, pnpm, bun) all suffered from ecosystem
fragmentation. A language should ship ONE package manager, and it should be the
only one that matters.

**3. The package manager as a separate project from the language.**
Python and C/C++ are the canonical examples. When packaging is not part of the
language distribution, it becomes a community effort with competing standards,
slow adoption, and fragmentation that lasts decades.

**4. Turing-complete dependency resolution.**
Python's `setup.py` and Cargo's `build.rs` can do arbitrary computation during
dependency resolution or build. This makes static analysis, security auditing,
and reproducible builds impossible. Dependency resolution should be a pure
function of the manifest and the registry state.

**5. No lockfile.**
Python's `pip freeze > requirements.txt` is not a lockfile — it doesn't
distinguish direct from transitive dependencies, doesn't include integrity
hashes, and is manually maintained. Every modern packaging system includes a
lockfile. A language that launches without one will add one within five years,
and the migration will be painful.

**6. Global dependency storage without isolation.**
Python's system site-packages, Node.js's global `node_modules`, Go's old
`GOPATH` — storing dependencies in a global location that all projects share is
a reproducibility disaster. Every project must have an isolated dependency
resolution.

**7. Dependency sprawl from zero-friction addition.**
npm's `npm install left-pad` culture created dependency trees that no single
human can audit. The packaging system should make adding a dependency easy, but
not invisible. The cost of a new dependency — the lines of code, the transitive
dependencies, the maintenance burden — should be visible.

**8. Breaking the lockfile format without migration tooling.**
npm changed `package-lock.json` format across versions without reliable
migration, causing CI failures and merge conflicts. Cargo's lockfile format has
been stable across major releases. Lockfile format stability is a critical
design constraint.

**9. Version numbers that don't mean anything.**
Languages without a semver convention (or where semver is routinely ignored)
create ecosystems where every upgrade is a gamble. The packaging system should
enforce or strongly encourage semantic versioning semantics — not just the
syntax of `MAJOR.MINOR.PATCH`, but the meaning that a major version bump *must*
indicate a breaking change.

---

## 10. Nomi Adopt / Refuse / Adapt Table

| # | Insight | Action | Rationale |
|---|---------|--------|-----------|
| 1 | **One manifest per project** (Cargo, npm, Go, Mix — all converge here) | **Adopt** | A single `Nomi.toml` at the project root declares identity, dependencies, and build settings. The unified-manifest pattern is universal; no successful ecosystem diverges from it. |
| 2 | **Lockfile with integrity hashes** (Cargo, npm, Go, Nix) | **Adopt** | `Nomi.lock` records exact versions + SHA-256 hashes of all dependencies. This is the Cargo/Go model: manifest for intent, lockfile for reproducibility. Integrity hashes prevent supply-chain tampering. |
| 3 | **Package manager ships with the compiler** (Cargo, Go, Elixir) | **Adopt** | `nomi build`, `nomi test`, `nomi run`, `nomi add dep`, `nomi publish` — the compiler and the package manager are the same CLI. This is the single most important packaging decision. |
| 4 | **TOML as the manifest format** (Cargo, pyproject.toml) | **Adopt** | TOML is readable, supports comments, distinguishes types, and is the emerging consensus. JSON lacks comments; XML is verbose; custom formats require custom tooling. TOML is the right default. |
| 5 | **Workspaces with shared lockfile** (Cargo, npm, Yarn) | **Adopt** | A `Nomi.toml` with `[workspace] members = [...]` and a single workspace-level lockfile. Each member has its own manifest; the workspace resolves them together. Cargo's workspace model is the best reference implementation. |
| 6 | **Minimum Version Selection** (Go modules) | **Adapt** | Adopt the MVS philosophy of "prefer stability over novelty," but add an explicit `nom update` command to selectively upgrade. MVS aligns with Nomi's local-reasoning emphasis. The Go implementation is the reference, but Nomi should provide better tooling messages for "why was this version selected?" |
| 7 | **Central registry with immutable artifacts** (crates.io, Maven Central, Hex) | **Adopt** | Published packages are immutable and yankable (not deletable). A 24-hour grace period for deleting accidentally published versions, then permanent. This is the crates.io policy and it is the right one. |
| 8 | **Dev-dependency separation** (Cargo's `[dev-dependencies]`, Maven's `<scope>test</scope>`) | **Adopt** | `[nom-dependencies]` for normal deps, `[dev-dependencies]` for test/build-only deps. Distinguish compile-time from runtime deps (Maven-style scopes). This is universally adopted and universally correct. |
| 9 | **Executable build scripts** (Cargo's `build.rs`) | **Adapt** | Allow a `build.nomi` file for build-time code generation, but constrain it to produce only declared outputs. The escape hatch is necessary (codegen, native linking), but Nomi should make the contract explicit: `build.nomi` receives inputs and produces outputs declared in `Nomi.toml`. |
| 10 | **npm-style zero-friction dependency addition** | **Refuse** | `nomi add` should show what is being added: number of new transitive deps, total lines of code, license summary, and recent maintenance activity. The goal is not to block dependency addition but to make its cost visible — the opposite of npm's invisible dependency sprawl. |
| 11 | **SNAPSHOT / mutable versions** (Maven) | **Refuse** | No mutable version strings. Every version is immutable once published. Development against unreleased dependencies uses path dependencies within a workspace (`dep = { path = "../other-crate" }`) — Cargo's solution. |
| 12 | **Patching dependencies that propagate to consumers** (Go's `replace` non-propagation model) | **Adapt** | Adopt Go's model: `[patch]` in `Nomi.toml` allows overriding a dependency for local development, but patches are NOT published to the registry. Consumers of a library should never inherit the library author's local patches. |
| 13 | **Feature flags / conditional compilation** (Cargo) | **Adapt** | Adopt Cargo's `[features]` model with feature unification, but with better tooling visibility: `nomi explain` should show which features are enabled and why. Feature unification is powerful but opaque; tooling can make it transparent. |
| 14 | **Maven-style parent POM / project inheritance** | **Refuse** | Project inheritance (parent POM defines config, children inherit) creates invisible coupling. Prefer composition: a shared workspace configuration that projects explicitly opt into, not inherit from. The Cargo workspace model is composition; the Maven parent POM model is inheritance. |
| 15 | **Module path as URL** (Go) | **Adapt** | Use URL-like paths for import identity (`nomi.dev/std/net`), but decouple identity from download location via a registry that maps identities to sources. This keeps Go's readable identity model without Go's identity-location coupling. |
| 16 | **Project generator** (Mix's `mix new`) | **Adopt** | `nomi new my_project` creates a working project with `Nomi.toml`, `src/`, `tests/`, and a `nom.nomi` entry point. The generated project compiles and tests pass without modification. Mix's project generation is the best reference: it teaches project structure by example. |
| 17 | **Declarative dev environments** (Nix flakes) | **Adapt** | Adopt the concept of a declared development environment (`[dev]` section in `Nomi.toml` specifying required tool versions), but not the Nix language or content-addressed storage. Nomi's dev environment should be simpler: "these versions of these tools, in an isolated shell." |

---

## Sources

- Python packaging: [PEP 518](https://peps.python.org/pep-0518/), [PEP 517](https://peps.python.org/pep-0517/), [PEP 621](https://peps.python.org/pep-0621/), [PEP 427](https://peps.python.org/pep-0427/)
- Cargo: [The Cargo Book](https://doc.rust-lang.org/cargo/), [Cargo.toml manifest format](https://doc.rust-lang.org/cargo/reference/manifest.html), [Feature resolver v2](https://doc.rust-lang.org/cargo/reference/features.html)
- Go modules: [Go Modules Reference](https://go.dev/ref/mod), [Minimum Version Selection](https://research.swtch.com/vgo-mvs), Russ Cox's [Go & Versioning](https://research.swtch.com/vgo) series
- Mix: [Mix Documentation](https://hexdocs.pm/mix/), [Hex.pm](https://hex.pm/), [Umbrella projects](https://elixir-lang.org/getting-started/mix-otp/dependencies-and-umbrella-projects.html)
- npm: [package.json specification](https://docs.npmjs.com/cli/v10/configuring-npm/package-json), [package-lock.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json), [npm blog on left-pad](https://blog.npmjs.org/post/141577284765/kik-left-pad-and-npm)
- NuGet: [PackageReference](https://learn.microsoft.com/en-us/nuget/consume-packages/package-references-in-project-files), [Central Package Management](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management)
- Nix: [Nix Flakes](https://nixos.wiki/wiki/Flakes), [Nix Pills](https://nixos.org/guides/nix-pills/), Dolstra et al., "Nix: A Safe and Policy-Free System for Software Deployment" (2004)
- Maven: [Maven POM Reference](https://maven.apache.org/pom.html), [Maven Central](https://central.sonatype.org/)
- Gradle: [Gradle User Manual](https://docs.gradle.org/current/userguide/userguide.html), [Gradle vs Maven comparison](https://gradle.org/maven-vs-gradle/)

---

*This document synthesizes research across eight packaging ecosystems. It is not a
specification — it is source material for Nomi's module/packaging design. File
under `docs/research/`. Companion docs: `standard_library_design_comparative.md`
(stdlib design), `go_design_philosophy_deep_dive.md` (Go specifics),
`cross_language_synthesis_master.md` (capstone synthesis).*
