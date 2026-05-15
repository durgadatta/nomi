# Deployment and Operations: Cross-Language Deep Dive

> Status: source research for Nomi design.
> Purpose: Study how ten deployment and operations systems work across programming
> language ecosystems — from static binary compilation to serverless functions to
> system package managers — and extract the structural invariants, genuine
> tradeoffs, and concrete recommendations for Nomi's deployment posture, both
> near-term (Python-hosted) and long-term (standalone toolchain).

## Table of Contents

1. [Go Binaries](#1-go-binaries)
2. [Python Packaging for Deployment](#2-python-packaging-for-deployment)
3. [Node / Deno / Bun Deploys](#3-node--deno--bun-deploys)
4. [Docker and Containerization](#4-docker-and-containerization)
5. [Serverless / FaaS](#5-serverless--faas)
6. [Rust Deployment](#6-rust-deployment)
7. [Java / JVM Deployment](#7-java--jvm-deployment)
8. [Nix / NixOS for Deployment](#8-nix--nixos-for-deployment)
9. [Wasm and Edge Deployment](#9-wasm-and-edge-deployment)
10. [Homebrew and Package Managers](#10-homebrew-and-package-managers)
11. [Cross-Language Synthesis](#11-cross-language-synthesis)
12. [Nomi Adopt / Refuse / Adapt Table](#12-nomi-adopt--refuse--adapt-table)
13. [Sources](#sources)

---

## 1. Go Binaries

### Core Deployment Philosophy

Go's deployment philosophy is simple to the point of radicalism: **compile
everything into a single static binary, then copy that binary to the target
machine.** There is no runtime to install. No shared libraries to link. No
virtual environment to activate. No package manager to invoke on the target.
`go build` produces a self-contained executable, and that executable is your
deployable artifact.

This philosophy emerged deliberately from Google's production experience. The Go
team — Pike, Griesemer, Thompson, and later Cox — had lived through C++ build
hell, Python dependency drift, and Java classpath nightmares at Google scale.
They designed Go's deployment story as a reaction: the compiler statically links
_everything_, including the Go runtime (scheduler, GC, maps, channels) and all
transitive dependencies. The resulting binary needs only the OS kernel.

```bash
# Build for the current platform
go build -o myapp .

# Cross-compile for Linux on ARM64
GOOS=linux GOARCH=arm64 go build -o myapp-linux-arm64 .

# Cross-compile for Windows
GOOS=windows GOARCH=amd64 go build -o myapp.exe .

# Build with stripped debug info for smaller size
go build -ldflags="-s -w" -o myapp .

# Truly static (no libc dependency — requires CGO_ENABLED=0)
CGO_ENABLED=0 go build -o myapp-static .
```

Cross-compilation works out of the box. No cross-toolchain installation, no
sysroot configuration, no target triple hunting. Just two environment variables.
This is possible because Go ships its own linker (`cmd/link`) and does not
depend on the system linker for pure-Go programs. The compiler cross-compiles to
every supported `$GOOS/$GOARCH` pair from any host platform.

### What Worked Exceptionally Well

1. **The Dockerfile that is a single `COPY` line.** A Go service's Dockerfile can
   be a multi-stage build that compiles in one stage, then copies a single binary
   into a `scratch` or `distroless` base image. The resulting image is 5-20 MB
   instead of 500 MB. No package manager, no shell, no OS distribution — just the
   binary and the kernel interface.

2. **Zero runtime dependency drift.** Because the runtime is compiled into the
   binary, the binary that passed tests is byte-for-byte the binary that runs in
   production. There is no "production has libc 2.31 but CI has 2.35" problem
   (with `CGO_ENABLED=0`). There is no "the JVM got updated between staging and
   prod" problem.

3. **Cross-compilation as a first-class feature.** Go cross-compilation predates
   Docker multi-arch builds by years. The ability to build Linux binaries from a
   macOS laptop with zero toolchain setup is a genuine productivity multiplier.
   CI/CD pipelines can produce binaries for every target in a single `go build`
   matrix.

4. **`go install` as distribution.** The pattern `go install
   example.com/cmd/tool@latest` downloads, compiles, and installs a CLI tool in
   one command. It is the simplest distribution mechanism for Go-native CLI tools:
   users need the Go toolchain, but they don't need to clone a repo, read a
   README, or install a package manager. The binary lands in `$GOPATH/bin`.

### What Failed or Caused Persistent Friction

1. **Binary size.** A minimal Go "hello world" is ~1.5 MB (stripped). A
   real-world HTTP service with a few dependencies is 10-25 MB. For server
   deployments this is fine. For CLI tools distributed to end users, it is
   noticeable compared to Rust (~400 KB stripped) or C (~16 KB). The Go runtime
   (GC, scheduler, goroutine stacks, reflection tables) adds a non-trivial floor.

2. **Plugin limitations.** Go's plugin system (`plugin` package, `-buildmode=plugin`)
   is Linux-only, fragile across compiler versions, and rarely used in practice.
   The single-binary model makes dynamic loading genuinely hard because the Go
   runtime assumes a single, coherent binary. Plugins compiled with Go 1.21
   cannot be loaded by a binary compiled with Go 1.22. This means Go applications
   that want extensibility must embed a scripting language (Lua, Starlark,
   JavaScript via goja) or use a subprocess model.

3. **CGO: the escape hatch that breaks the model.** `CGO_ENABLED=1` (the default
   on most platforms!) dynamically links libc. This means a binary built on one
   Linux distribution may not run on another with a different glibc version. The
   "just copy the binary" promise breaks the moment CGO enters the picture. The
   Go community has responded with `CGO_ENABLED=0` as a best practice for
   deployable binaries, but many popular packages (notably `go-sqlite3` and parts
   of the `net` package historically) require CGO.

4. **Platform-specific code requires build tags.** File names like
   `socket_linux.go` and `socket_darwin.go` combined with `//go:build` tags
   work, but they are a source-level mechanism. There is no runtime platform
   dispatch — the code is selected at compile time. This is clean for simple
   cases but awkward when a single source file needs small platform variations.

### Key Structural Insight for Nomi

The single-binary model is not about performance or size — it is about
**eliminating the gap between the artifact you tested and the artifact that
runs.** Every deployment system that introduces a boundary between "build time"
and "runtime" introduces a place where drift can occur. Go eliminates that
boundary. Nomi should treat this as a design target: the deployable artifact
should be structurally identical to the tested artifact.

---

## 2. Python Packaging for Deployment

### Core Deployment Philosophy

Python's deployment philosophy is the inverse of Go's: **ship source code and
reconstruct the environment at deploy time.** The unit of deployment is not a
binary but a set of source files plus a dependency specification, installed into
a controlled environment. This is a consequence of Python's dynamic nature — no
ahead-of-time compiler, no static linking, no single binary output — but it also
reflects a cultural preference for source distribution that predates modern
deployment practice.

Python's deployment toolchain has accreted across two decades and now has
multiple layers: virtual environments for isolation, `pip` for dependency
resolution, wheels for pre-built distribution, `pyproject.toml` for declarative
metadata, and a growing family of "freeze into something deployable" tools.

### What Worked Exceptionally Well

1. **Virtual environments as lightweight isolation.** `python3 -m venv .venv`
   creates a self-contained Python installation in under a second. It copies
   nothing — it creates a directory with a symlink to the system interpreter and
   a `site-packages` directory for project-specific packages. Activation modifies
   `PATH`; deactivation restores it. The model is simple, fast, and sufficient
   for development. For deployment, it is the basis for every Python-on-server
   strategy.

2. **Wheels as pre-built distribution.** A `.whl` file is a ZIP archive with a
   standardized naming convention: `{package}-{version}-{python_tag}-{abi_tag}-{platform_tag}.whl`.
   `manylinux` wheels (PEP 600) bundle native extensions compiled against an
   ancient glibc, ensuring compatibility with any modern Linux distribution.
   `pip install` can fetch and install a wheel in under a second, and the target
   platform is encoded in the filename.

3. **Requirements pinning for reproducible environments.** `pip freeze >
   requirements.txt` captures the exact version of every installed package,
   transitive dependencies included. Combined with `pip install -r
   requirements.txt`, this gives byte-for-byte reproducible environments — within
   the same Python version and platform. `pip-tools` and `pip-compile` extend
   this with hash-checking mode (`--generate-hashes`) for supply-chain security.

4. **Docker as the "solved" deployment story.** The modern Python deployment
   answer is: write a `Dockerfile` that starts from `python:3.12-slim`, copies
   `requirements.txt`, runs `pip install`, copies the source, and defines a
   `CMD`. This works reliably, leverages Docker's caching for fast rebuilds, and
   sidesteps most of Python's deployment complexity. The Docker layer IS the
   deployment artifact.

### What Failed or Caused Persistent Friction

1. **The freeze-it-all family has no winner.** `PyInstaller` bundles the Python
   interpreter, all dependencies, and your code into a single executable. It
   works — but the resulting binary is 50-100 MB for a trivial script, startup
   time includes extracting the bundle to a temp directory, and platform support
   is uneven. `Nuitka` compiles Python to C and emits a native binary, but
   compilation is slow and some dynamic patterns break. `shiv` and `pex` create
   self-contained ZIP applications (PEX files) that include dependencies but
   still need a compatible Python interpreter on the target. `cx_Freeze` is
   another entry in the same space. None of these is the standard answer.

2. **Native extensions break the "pure Python" story.** A `pip install` that
   compiles C extensions needs a C compiler, Python headers, and development
   libraries on the target machine. Wheels solve this for popular platforms and
   packages, but any package without a pre-built wheel for the target platform
   triggers a source build. This is the deployment equivalent of "works on my
   machine."

3. **Dependency resolution is NP-hard.** `pip`'s original resolver was a greedy
   algorithm that could produce unsatisfiable environments without warning. The
   2020 resolver rewrite (pip 20.3) added proper backtracking, but resolution
   can still take minutes for complex dependency graphs. `poetry` and `pipenv`
   improved the UX but added another tool to learn. `uv` (2024) is the first
   resolver that is genuinely fast (Rust, incremental resolution), but it
   represents yet-another-tool in a fragmented landscape.

4. **Python version coupling.** A `requirements.txt` pins package versions but
   not the Python version. A project that works on Python 3.11 may break on 3.12
   due to removed APIs or changed semantics. `pyproject.toml`'s
   `requires-python` field declares the constraint but doesn't enforce it —
   enforcement requires `pip` or a version manager. Tools like `pyenv` fill this
   gap but are yet another thing to install.

### Key Structural Insight for Nomi

Python's deployment complexity is a consequence of its dynamic nature, not an
accident of tooling. A dynamic language cannot produce a static binary in the
same way a compiled language can — the interpreter IS the runtime dependency.
The "right" deployment story for a dynamic language is: version-pinned
dependencies + container image + deterministic build. Nomi's near-term
Python-hosted deployment will inherit Python's story. Nomi's long-term
standalone story can aim for Go/Rust-style artifacts.

---

## 3. Node / Deno / Bun Deploys

### Core Deployment Philosophy

The JavaScript ecosystem has three distinct deployment philosophies, reflecting
the runtime's evolution from browser-only to universal:

- **Node/npm**: ship source + `package.json` + `package-lock.json`, run `npm ci`
  on the target (or in a Docker container). The deployable unit is a directory
  tree with `node_modules`.
- **Deno**: ship source files with URL imports (no `node_modules`), or use `deno
  compile` to produce a single binary.
- **Bun**: ship source like Node, or use `bun build --compile` for a single
  binary. Bun also serves as a drop-in Node replacement with faster startup.

The Node model dominates production deployment. Deno's and Bun's binary
compilation are gaining traction for CLI tool distribution.

### What Worked Exceptionally Well

1. **Lockfiles for reproducibility.** `package-lock.json` (npm) and `yarn.lock`
   (Yarn) record the exact resolved URL and integrity hash of every dependency,
   transitive dependencies included. `npm ci` installs exactly what the lockfile
   specifies — no resolution, no version drift. This is the JavaScript
   ecosystem's single most important deployment innovation: the lockfile makes
   "works on my machine" a solvable problem.

2. **`deno compile` as a single-binary distribution channel.** `deno compile`
   bundles the Deno runtime (V8 + Rust core), all TypeScript/JavaScript source,
   and an embedded file system into a single executable. The resulting binary is
   40-60 MB (the V8 engine is large) but is genuinely self-contained. No runtime
   to install, no `node_modules` to ship. This is the best JS-to-binary story
   available today.

3. **Serverless-first design in modern frameworks.** Next.js, SvelteKit,
   Astro, and Remix all design for serverless deployment as a first-class target.
   `next build` produces a `.next/` directory with split bundles optimized for
   cold starts. Vercel's infrastructure reads this output directly. The
   framework IS the deployment specification.

4. **npm packages as deployable units.** An npm package is a directory with a
   `package.json` and source files. Publishing is `npm publish`. Installing in
   production is `npm ci --production`. The simplicity of publishing — no build
   step required for pure-JS packages — means deploying an npm library is
   trivial.

### What Failed or Caused Persistent Friction

1. **`node_modules` bloat.** A typical Node project's `node_modules` is 200-500
   MB for hundreds of packages (many are one-liners — `left-pad` was 11 lines).
   This makes Docker builds slow, makes `npm ci` take 30-60 seconds even on fast
   hardware, and makes the "just copy the directory" deployment model
   heavyweight.

2. **Runtime version coupling.** Node 18, 20, 22, 24 — each LTS line has
   subtly different APIs. `package.json`'s `engines.node` field declares the
   requirement, but it is advisory. A project developed on Node 22 may use APIs
   not present in Node 20, and the error appears at runtime. `.nvmrc` and
   `nvm use` handle this in development but not in production.

3. **Bundle size in the browser.** Tree-shaking (removing unused code) is
   essential for browser deployment but works inconsistently. Dynamic imports,
   CommonJS interop, and side-effectful modules defeat tree-shaking. Webpack,
   Rollup, esbuild, and Turbopack all have different tree-shaking behavior,
   making it hard to predict what actually ends up in the final bundle.

4. **Deno's URL imports break the lockfile model.** Deno originally had no
   lockfile — URL imports were cached in `DENO_DIR` with no integrity checking.
   `deno.lock` (added 2023) fixed this, but the URL-import philosophy means
   there is no single registry (no PyPI/npm equivalent) for Deno packages. This
   makes supply-chain auditing harder.

### Key Structural Insight for Nomi

The JavaScript ecosystem demonstrates that a lockfile is the minimum viable
reproducibility primitive. Whether you ship source, a container, or a binary,
you need a content-addressed record of exactly what was resolved during the
build. Nomi should have a lockfile from day one.

---

## 4. Docker and Containerization

### Core Deployment Philosophy

Docker's deployment philosophy is: **ship the entire userspace, not just the
application.** A container image is a stack of immutable layers — OS
distribution, system libraries, language runtime, application dependencies,
application code — that together form a complete, self-contained execution
environment. The kernel is shared with the host; everything above the kernel is
pinned in the image.

This is a genuinely radical deployment model. It says: "don't configure the
target machine, replace it." The target machine needs only a container runtime
(Docker, containerd, podman). Everything else is in the image.

```dockerfile
# Multi-stage build: compile in one stage, ship in another
FROM golang:1.22 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server .

FROM scratch
COPY --from=builder /app/server /server
ENTRYPOINT ["/server"]
```

### What Worked Exceptionally Well

1. **Multi-stage builds as a universal pattern.** The builder stage has the full
   toolchain (compiler, headers, package manager). The runtime stage has only the
   artifact. The final image is minimal — no compiler, no dev headers, no build
   tools. This pattern works identically across languages: a Go service, a Rust
   binary, a Java JAR with a minimal JRE, a Python app with only runtime
   dependencies.

2. **Distroless images as a security baseline.** Google's distroless images
   contain only the application and its runtime dependencies — no shell, no
   package manager, no `apt`, no `curl`, no `bash`. This means an attacker who
   compromises the application cannot `apt install` tools or spawn a shell. The
   attack surface is the application binary and the kernel interface.

3. **Layered caching for fast rebuilds.** Each `RUN`, `COPY`, and `ADD`
   instruction creates a layer. Docker caches layers by content hash. Change one
   line of application code: only the final `COPY` and `RUN` layers rebuild. The
   OS, runtime, and dependency layers come from cache. This makes CI rebuilds
   fast — 10-30 seconds after dependencies are installed, regardless of language.

4. **Registry + tag as a universal deployment interface.** `docker pull
   registry.example.com/app:v1.2.3` works the same for a Go binary, a Python
   app, a Node service, or a JVM application. The ops team doesn't need to know
   the language — they need to know the image tag. This is the container
   model's killer feature: language-agnostic deployment.

### What Failed or Caused Persistent Friction

1. **Image size sprawl.** A naive `FROM node:22` followed by `npm install` and
   `COPY . .` produces a 1.2 GB image. Multi-stage builds and distroless images
   fix this but require deliberate effort. The default — the path of least
   resistance — produces bloated images. Most Dockerfiles in the wild are not
   optimized.

2. **The "it works in Docker" trap.** Docker provides isolation from the host OS
   but not from Docker itself. Different Docker versions, different containerd
   versions, and different kernel versions can produce subtly different behavior.
   The Docker image is a deployable artifact, but it is not a perfectly
   hermetic artifact — the kernel is shared.

3. **BuildKit cache invalidation surprises.** `COPY . .` invalidates the cache
   for all subsequent layers every time any file changes. The `go mod download`
   pattern (copy `go.mod` and `go.sum` first, then download, then copy source)
   works around this but is a manual optimization that developers must learn.
   BuildKit's `--mount=type=cache` improves this but adds complexity.

4. **Mac/Windows performance tax.** Docker on macOS runs in a Linux VM (via
   hypervisor.framework or Virtualization.framework). File system operations —
   especially `npm install` with thousands of small files — are 5-20x slower
   than native. Docker's `virtiofs` (Docker Desktop 4.6+) improved this but
   does not eliminate the gap.

### Key Structural Insight for Nomi

Docker demonstrates a meta-principle: **the deployment artifact format should be
independent of the language.** Whether Nomi eventually compiles to static
binaries, WASM modules, or Python bytecode, the deployment interface should
support the same pattern: produce an artifact, reference it by content hash,
ship it to a runtime. Docker's registry + tag model is one answer. OCI
artifacts, WASM registries, and content-addressed stores are others. Nomi should
design its build output to be compatible with all of them.

---

## 5. Serverless / FaaS

### Core Deployment Philosophy

Serverless (Function-as-a-Service) changes the deployment unit from a
long-running process to a stateless function that runs on demand. The platform
(AWS Lambda, Cloudflare Workers, Google Cloud Functions, Vercel Functions)
manages everything above the function handler: load balancing, scaling, instance
lifecycle, OS patching. The developer provides code + configuration. The
platform provides everything else.

This is a radical inversion of deployment responsibility: instead of the
developer managing infrastructure, the platform manages infrastructure and the
developer manages code. The deployment artifact is a ZIP file or container image
containing a function handler.

### What Worked Exceptionally Well

1. **Cloudflare Workers (V8 isolates model).** Cloudflare Workers run JavaScript
   in V8 isolates — lightweight execution contexts within a single V8 process.
   Cold start time is under 5 ms (compared to 200 ms - 2 s for Lambda). The V8
   isolate model means thousands of "functions" can run on a single machine with
   near-zero overhead per isolate. This is the closest the industry has come to
   "deploy a function like you call a function."

2. **Lambda Layers for shared dependencies.** Lambda Layers let you publish a
   ZIP of shared dependencies (e.g., `numpy`, `pandas`) and attach it to
   multiple functions. This keeps function ZIPs small (just your code) while
   sharing the large dependency layer. It is a partial solution to the
   dependency-bloat problem in serverless.

3. **Provisioned concurrency (Lambda) for cold start elimination.** AWS lets you
   pre-warm a specified number of Lambda instances. You pay for the warm
   instances, but cold start latency drops to zero for traffic below the
   provisioned threshold. This acknowledges that cold starts are a fundamental
   limitation of the FaaS model and provides a pragmatic workaround.

4. **Vercel's framework-aware deployment.** Vercel reads the build output of
   Next.js, SvelteKit, Astro, etc., and automatically splits routes into
   serverless functions. A `/api/users` route becomes one function; `/api/posts`
   becomes another. The framework defines the split; Vercel deploys it. This
   eliminates the per-function configuration tax that AWS Lambda imposes.

### What Failed or Caused Persistent Friction

1. **Cold start variance by language.** Python cold starts are 200-500 ms. Node
   cold starts are 100-300 ms. Go cold starts are 50-150 ms. Java cold starts
   are 2-10 seconds (JVM class loading, JIT warmup). Ruby cold starts are
   500-1500 ms. The language choice directly determines whether your function is
   "serverless viable" for latency-sensitive workloads. This is not a
   serverless-problem — it is a language-design problem exposed by serverless.

2. **The 250 MB / 10 GB Lambda limits.** Lambda packages (ZIP) are limited to
   250 MB uncompressed (50 MB compressed). Container images can be up to 10 GB —
   but larger images mean longer cold starts (pulling the image from ECR). ML
   models, large dependencies, and bundled data quickly hit these limits.

3. **State is everywhere but serverless wants it nowhere.** Serverless functions
   are stateless by design. But real applications have state: database
   connections, session data, file uploads, caches. Connecting to a database from
   a serverless function means a new TCP connection on every cold start — or
   connection pooling via a proxy (RDS Proxy, etc.). The statelessness
   constraint pushes complexity into the persistence layer.

4. **The tooling tax of per-function configuration.** AWS Lambda requires each
   function to be configured separately: memory, timeout, environment variables,
   IAM role, VPC, layers. A service with 20 functions has 20 separate
   configurations. Infrastructure-as-code (Terraform, CDK, Pulumi) manages this
   but adds another layer of complexity.

### Key Structural Insight for Nomi

Serverless rewards language designs that minimize overhead. Fast startup, small
binary, low memory footprint — these are not just nice-to-have; they are
existential for serverless viability. Nomi should design for fast cold starts as
a first-class concern, even if Nomi's initial deployment target is traditional
servers. The serverless model is where deployment is heading, and languages that
cannot follow will be locked out.

---

## 6. Rust Deployment

### Core Deployment Philosophy

Rust's deployment philosophy is: **compile to a native binary, ship it, run
it.** Like Go, Rust produces self-contained executables with no runtime
dependency. Unlike Go, Rust does not include a garbage collector or scheduler in
the binary — the runtime cost is paid at compile time (borrow checker, monomorphization,
LLVM optimization). The resulting binary is a direct peer of C/C++ binaries: it
links against the system's libc (by default) or against musl for full static
linking.

```bash
# Standard release build
cargo build --release

# Fully static binary (musl target)
rustup target add x86_64-unknown-linux-musl
cargo build --release --target x86_64-unknown-linux-musl

# Smaller binary: strip + LTO + abort on panic
# (in Cargo.toml)
[profile.release]
strip = true
lto = true
panic = "abort"
```

### What Worked Exceptionally Well

1. **`cargo install` for CLI tool distribution.** `cargo install ripgrep`
   downloads the source, compiles it with optimizations, and installs the binary
   to `~/.cargo/bin`. No separate package manager, no Homebrew, no apt. The
   single command works on any platform with Rust installed. This is the closest
   the compiled-language world has come to `npm install -g`.

2. **Musl static binaries.** The `x86_64-unknown-linux-musl` target produces a
   fully static binary that runs on any Linux kernel 2.6+. No glibc version
   dependency. Copy to a `scratch` Docker image and it works. This is
   functionally equivalent to `CGO_ENABLED=0` Go binaries but with significantly
   smaller binary size (Rust's runtime is smaller than Go's).

3. **`cargo-deb` and `cargo-rpm` for system packages.** These tools
   automatically produce `.deb` and `.rpm` packages from a Cargo project. They
   place binaries in `/usr/bin`, config in `/etc`, systemd units in
   `/lib/systemd/system`. This bridges the gap between `cargo install` (for
   developers) and system package managers (for ops teams).

4. **Cross-compilation via `cross`.** The `cross` tool uses Docker to provide
   the correct cross-compilation toolchain for any target. `cross build --target
   aarch64-unknown-linux-gnu` "just works" — Docker provides the cross-linker,
   sysroot, and libraries. This is less seamless than Go's built-in
   cross-compilation but more flexible (supports any target LLVM supports).

### What Failed or Caused Persistent Friction

1. **Compile times.** `cargo build --release` for a mid-size project takes
   2-10 minutes on fast hardware. `cargo install ripgrep` compiles the entire
   dependency tree from source. This is acceptable for one-time installation but
   painful for CI/CD pipelines. Incremental compilation and `sccache` help but
   don't eliminate the fundamental slowness of LLVM optimization.

2. **The `openssl` dependency.** Many Rust crates depend on `openssl-sys`,
   which requires OpenSSL development headers on the build machine and links
   dynamically against the system's libssl. This breaks the "copy binary"
   deployment model unless you use `rustls` (pure-Rust TLS) or static-link
   OpenSSL (complex). The `openssl` → `rustls` migration is ongoing but
   incomplete as of 2026.

3. **Platform support gaps.** Rust supports many platforms via LLVM, but
   `std` (beyond `core` and `alloc`) requires OS support. Embedded targets
   (ARM Cortex-M, RISC-V) work with `#![no_std]` but lose `std::net`, `std::fs`,
   and `std::thread`. This is a clean technical distinction but means "Rust
   everywhere" is not uniformly `std` everywhere.

4. **`cargo install` compiles from source every time.** Unlike `npm install -g`
   or `pip install`, `cargo install` does not download pre-built binaries. It
   compiles. This means installation speed depends on the machine and the
   project's compile time. `cargo-binstall` (third-party) solves this by
   downloading pre-built binaries from GitHub Releases, but it is not part of the
   official toolchain.

### Key Structural Insight for Nomi

Rust demonstrates that a compiled language can have both a developer-friendly
distribution channel (`cargo install`) and a system-package distribution channel
(`cargo-deb`/`cargo-rpm`). Nomi should design for both: an easy path for
developers to install Nomi-built tools, and a clean path for ops teams to
package Nomi programs as system packages or containers.

---

## 7. Java / JVM Deployment

### Core Deployment Philosophy

Java's deployment philosophy has evolved through four distinct eras:

1. **"Install the JRE separately" (1995-2015).** Deploy a JAR, assume the
   target has the right JRE installed. This was the original model and the root
   of Java's classpath/runtime-version pain.
2. **Uber-JARs (2010-present).** Bundle all dependencies into a single
   executable JAR. The JRE is still separate, but at least there is only one
   artifact.
3. **jlink custom runtimes (Java 9+, 2017).** `jlink` produces a custom,
   minimal JRE containing only the modules the application uses. Ship the JRE +
   the application together.
4. **GraalVM Native Image (2019-present).** Ahead-of-time compilation to a
   standalone native binary. No JVM at runtime.

The trajectory is clear: from "the runtime is the platform's problem" to "the
runtime is bundled with the application" to "the runtime is compiled away."

### What Worked Exceptionally Well

1. **Uber-JARs as a universal artifact.** A Spring Boot "fat JAR" includes the
   application, all dependencies, and an embedded web server (Tomcat/Jetty). Run
   it with `java -jar app.jar` on any machine with a compatible JRE. This is
   the one-artifact deployable model applied to the JVM ecosystem.

2. **jlink minimal runtimes.** `jlink --add-modules java.base,java.sql,java.net.http
   --output myruntime` produces a JRE directory that is 30-50 MB instead of the
   200+ MB of a full JDK. This makes Java viable for container images: a custom
   JRE + a Spring Boot JAR can fit in a 100 MB container image.

3. **GraalVM Native Image for serverless.** A Quarkus or Micronaut application
   compiled with GraalVM Native Image starts in 10-50 ms (vs. 2-10 seconds for
   the JVM). This makes Java viable for serverless — the cold start problem that
   excluded Java from Lambda for years is solved (at the cost of build-time
   complexity and some runtime limitations).

4. **WAR files and servlet containers.** The WAR (Web Application Archive) model
   — deploy a standard-format archive to a standard-format container (Tomcat,
   Jetty, WildFly) — was the dominant Java deployment model for 15 years. It
   worked reliably: ops managed the containers, devs produced the WARs. The
   separation of responsibilities was clean, even if heavyweight by modern
   standards.

### What Failed or Caused Persistent Friction

1. **Classpath hell.** Before Maven/Gradle dependency management, Java
   deployment meant managing `CLASSPATH` — a colon-separated list of JAR file
   paths. Two dependencies requiring different versions of the same library
   caused `NoSuchMethodError` at runtime, often in production. Maven solved the
   build-time classpath; the runtime classpath remained a problem for 20 years.

2. **"Write once, debug everywhere."** The JVM's platform abstraction layer
   mostly worked, but edge cases — file encoding defaults, line separator
   differences, thread scheduling behavior, GC behavior — meant Java's "write
   once, run anywhere" was "write once, test everywhere."

3. **GraalVM Native Image compatibility gaps.** Not all Java code compiles with
   GraalVM Native Image. Reflection, dynamic class loading, and `MethodHandle`
   usage need explicit configuration (`reflect-config.json`, etc.). Libraries
   must be Native Image-aware. The "compile your Spring Boot app to a native
   binary" story works well for Quarkus and Micronaut (designed for it) but
   less well for legacy Spring applications.

4. **JVM version fragmentation in production.** Even with jlink-bundled JREs,
   production environments often have multiple JVMs installed. A server running
   Java 8, 11, 17, and 21 applications must have all four JREs available. The
   bundled-JRE model fixes this per-application but at the cost of disk space
   and memory (multiple JREs in memory = more RSS).

### Key Structural Insight for Nomi

Java's 30-year deployment evolution reveals a clear arc: **the runtime dependency
is a liability that the ecosystem progressively eliminates.** From "install the
JRE" to "bundle the JRE" to "compile away the JRE." Nomi should learn from this
arc and aim for the right endpoint from the start. If Nomi will have a runtime,
it should be bundlable. If it won't, even better.

---

## 8. Nix / NixOS for Deployment

### Core Deployment Philosophy

Nix's deployment philosophy is: **every build is a pure function from inputs to
outputs.** A Nix derivation specifies exact inputs (source code, dependencies,
build flags) and produces a content-addressed output in `/nix/store`. The build
runs in a sandbox with no network access and no access to files not explicitly
declared as inputs. This means: if two people build the same derivation on
different machines, they get bit-for-bit identical output.

```nix
# A Nix derivation for a Go program
{ lib, buildGoModule, fetchFromGitHub }:

buildGoModule rec {
  pname = "myapp";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "myorg";
    repo = "myapp";
    rev = "v${version}";
    sha256 = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
  };

  vendorHash = "sha256-BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=";
}
```

NixOS extends this to the entire operating system: your system configuration is
a Nix expression that evaluates to a complete, reproducible OS installation. The
same configuration on two machines produces the same set of packages, services,
and configurations.

### What Worked Exceptionally Well

1. **True build reproducibility.** A Nix derivation that succeeds on one machine
   will succeed on any other machine with the same architecture. If it produces a
   binary, the binary is bit-for-bit identical. This is not aspirational — it is
   enforced by the sandbox. Builds that accidentally depend on the build time,
   the machine's hostname, or the user's home directory fail (or produce
   different hashes, which Nix detects).

2. **Rollback as a first-class operation.** `nixos-rebuild switch` applies a new
   system configuration. If it breaks something, `nixos-rebuild switch
   --rollback` reverts to the previous configuration. Every configuration is a
   generation in the bootloader menu. Reboot into generation 42 if generation 43
   is broken. This makes system upgrades safe in a way that `apt upgrade` or
   `yum update` cannot match.

3. **`nixpkgs` as the universal package database.** `nixpkgs` contains 80,000+
   packages, all built from the same coherent dependency tree. When you install
   `python3Packages.numpy`, it uses the exact same BLAS/LAPACK libraries as
   `python3Packages.scipy` — because they are resolved from the same package set.
   This eliminates "numpy and scipy were compiled against different BLAS" bugs.

4. **Dev shells as reproducible development environments.** `nix develop` (or
   the older `nix-shell`) produces a shell with exactly the specified
   dependencies. A `flake.nix` in the repo root defines the dev environment.
   `nix develop` gives every developer the same Go version, the same linters,
   the same protobuf compiler, etc. "Works on my machine" becomes "works in the
   dev shell."

### What Failed or Caused Persistent Friction

1. **The learning curve is a cliff.** Nix's expression language is a lazy,
   purely functional DSL with its own syntax and semantics. Understanding how
   `callPackage`, `override`, `overrideAttrs`, and the fixed-point combinator
   work requires understanding Nix-the-language before you can use
   Nix-the-tool. This is the steepest learning curve of any build/deployment
   tool in common use.

2. **Build times are multiplicative.** Every dependency change triggers a
   rebuild of everything that depends on it. If `openssl` updates, everything
   that links against it rebuilds. Nix's binary cache (`cache.nixos.org`)
   mitigates this for `nixpkgs` packages, but for local derivations, you pay the
   full build cost. This makes the "everything is a Nix derivation" model
   expensive in developer time.

3. **macOS friction.** Nix works on macOS, but many `nixpkgs` packages are
   Linux-only, and the macOS sandbox has limitations (SIP prevents some system
   call interception). The Nix experience on macOS is second-class compared to
   NixOS (Linux). This is a problem for a tool that promises cross-platform
   reproducibility.

4. **The flakes split.** Nix flakes (2020) introduced a new CLI (`nix build`,
   `nix develop`, `nix run`) and a new manifest format (`flake.nix`). Pre-flake
   Nix (`nix-build`, `nix-shell`, `default.nix`) still works and is still widely
   used. The community is split. Documentation, tutorials, and examples are
   inconsistent about which style to use. This is a self-inflicted wound.

### Key Structural Insight for Nomi

Nix demonstrates the maximum extent of deployment reproducibility. The cost is a
steep learning curve and a custom expression language. Nomi should extract the
principle — content-addressed, sandboxed, deterministic builds — without
adopting Nix's full complexity. Lockfiles + content-addressed caches + build
sandboxing gets you 80% of Nix's reproducibility at 20% of the cost.

---

## 9. Wasm and Edge Deployment

### Core Deployment Philosophy

WebAssembly (Wasm) is a compilation target, not a deployment system per se, but
it enables a distinctive deployment model: **compile to a portable, sandboxed
binary format that runs at near-native speed in a minimal runtime.** The Wasm
runtime provides memory safety, capability-based security (no file system, no
network access unless explicitly granted via WASI), and OS-level process
isolation within a single process.

Edge deployment (Fastly Compute, Cloudflare Workers, Fermyon Spin) is where Wasm
deployment has found its natural home. The runtime is a Wasm engine (Wasmtime,
V8, Lucet/wasm-micro-runtime) running on edge servers. The deployable artifact
is a `.wasm` module — typically 100 KB - 5 MB for a real application.

```bash
# Compile Rust to WASM
rustup target add wasm32-wasi
cargo build --release --target wasm32-wasi
# Produces target/wasm32-wasi/release/app.wasm

# Compile Go to WASM (TinyGo is preferred over standard Go)
tinygo build -target=wasi -o app.wasm main.go
```

### What Worked Exceptionally Well

1. **Fastly Compute (Lucet/Wasmtime).** Fastly's edge platform runs Wasm modules
   compiled with Lucet (now Wasmtime). Startup time is in microseconds — the
   Wasm engine pre-compiles the module and instantiates it on demand. Cold starts
   that take seconds on Lambda take microseconds on Fastly. This is the
   deployment model closest to "run this function, right now, on the edge,
   without waiting."

2. **WASI as a capability system.** WASI (WebAssembly System Interface) provides
   file system, network, and random-number access only via explicit grant. A Wasm
   module cannot open `/etc/passwd` unless the runtime explicitly provides a
   preopened directory descriptor for `/etc`. This inverts the security model:
   instead of "block everything suspicious," it is "grant nothing by default."
   Every system interaction is an explicit capability grant.

3. **Language-agnostic bytecode.** Rust, C, C++, Go (via TinyGo), Zig, and
   Swift can all compile to Wasm. The `.wasm` file is the same format regardless
   of source language. An edge platform can run Rust-based Wasm modules and
   Go-based Wasm modules in the same runtime, with the same security model, with
   no per-language configuration.

4. **The component model for composition.** Wasm's component model (2024+) lets
   you compose Wasm modules that were compiled from different languages. A Rust
   module can import a Go module's interface; a JavaScript module can call into a
   C module. The component model defines a language-agnostic ABI (Canonical ABI)
   that modules use to communicate. This is "shared libraries done right" — the
   Wasm runtime enforces isolation between components.

### What Failed or Caused Persistent Friction

1. **The WASI preview churn.** WASI preview 1 (2019) provided a POSIX-like API.
   WASI preview 2 (2024) replaced it with a component-model-based API that is
   incompatible with preview 1. Toolchains built for preview 1 (older TinyGo,
   older `wasmtime`) do not work with preview 2 runtimes. This is a
   standardization-in-progress problem — WASI is not yet at the stability level
   of POSIX or libc.

2. **Garbage collection gap.** Wasm's GC proposal (2024+) adds native support
   for garbage-collected languages, but it is not yet universally available.
   Go's standard Wasm target (not TinyGo) requires shipping a Go runtime
   (scheduler + GC) compiled to Wasm — the Wasm module is 3-10 MB for a trivial
   program. This negates one of Wasm's core advantages (small artifact size).

3. **Debugging ergonomics.** Debugging a Wasm module on an edge platform is
   harder than debugging a local process. Stack traces may show Wasm bytecode
   offsets rather than source locations. DWARF debug info support in Wasm
   runtimes is incomplete. The debugging story is improving but is years behind
   native debugging.

4. **The toolchain fragmentation.** `wasm-pack` (Rust → Wasm for browser),
   `cargo-wasi` (Rust → WASI), `wasm-bindgen` (Rust ↔ JS interop), `wit-bindgen`
   (component model bindings), `javy` (JS → Wasm via QuickJS), `wasm-tools`
   (component model tooling) — the Wasm ecosystem has many tools with
   overlapping responsibilities and inconsistent defaults.

### Key Structural Insight for Nomi

Wasm is the most promising deployment target for a new language. It provides
sandboxing, portability, and near-native speed without requiring a
language-specific runtime on the target. Nomi should treat Wasm as a first-class
compilation target from day one. The component model's language-agnostic ABI is
also a strong vote for a language that has a clean, simple FFI: the simpler
Nomi's foreign interface, the easier it is to target WASI and the component
model.

---

## 10. Homebrew and Package Managers

### Core Deployment Philosophy

System package managers (Homebrew, apt, yum/dnf, pacman, Chocolatey) solve a
different deployment problem: **distributing developer tools to end-user
machines.** The user is a developer who wants to install `ripgrep` or `jq` or
`bat` on their laptop. The deployment artifact is a pre-compiled binary (or
sometimes a source build recipe). The distribution channel is a package
repository.

Homebrew in particular is the dominant tool-distribution channel for macOS
developers. A `brew install` formula is a Ruby script that specifies the source
URL, build instructions, and dependency formulas.

```ruby
# A Homebrew formula (Ruby DSL)
class Ripgrep < Formula
  desc "Search tool like grep and The Silver Searcher"
  homepage "https://github.com/BurntSushi/ripgrep"
  url "https://github.com/BurntSushi/ripgrep/archive/14.1.0.tar.gz"
  sha256 "33c0a15e6ff152afe4a3c0a2c5d8d4e3f5b8c1a7d9e0f2b6a8c4d1e3f5a7b9c"
  license "MIT"
  head "https://github.com/BurntSushi/ripgrep.git", branch: "master"

  depends_on "rust" => :build
  depends_on "pkg-config" => :build

  def install
    system "cargo", "install", "--root", prefix, "--path", "."
  end
end
```

### What Worked Exceptionally Well

1. **Bottles for instant installation.** A Homebrew "bottle" is a pre-compiled
   binary package. `brew install ripgrep` downloads the bottle — no compilation
   needed. This takes 5 seconds instead of 5 minutes. Bottles are built on
   Homebrew's CI infrastructure (macOS and Linux) for every supported OS version
   and architecture. The CI is the build farm; users get pre-built artifacts.

2. **The tap system for third-party distribution.** `brew tap
   myorg/tools` adds a third-party formula repository. `brew install
   myorg/tools/myapp` installs from that tap. This is a clean extension model:
   the core `homebrew/core` repository is curated, but anyone can publish
   formulas via a tap. No registration, no approval process. Just a Git repo
   with formula files.

3. **`brew services` for background daemons.** `brew services start postgresql`
   launches PostgreSQL as a background service (via launchd on macOS, systemd on
   Linux). This bridges the gap between "install a CLI tool" and "run a
   persistent service." It is simple enough to use during development without
   needing Docker or a full ops setup.

4. **Version management via `@` versions.** `brew install go@1.22` installs a
   specific Go version alongside the current one. `brew link go@1.22 --force`
   switches the active version. This is crude compared to `nvm` or `pyenv` but
   works for tools where the version coupling is simple.

### What Failed or Caused Persistent Friction

1. **Linux is second-class.** Homebrew on Linux (Linuxbrew) works but has
   persistent issues: many formulas assume macOS file paths, `brew services` on
   systemd was fragile for years, and bottles for niche Linux distributions are
   rarely available. The core developer experience is macOS-first.

2. **Formula maintenance burden.** Homebrew formulas require active maintenance:
   when upstream releases a new version, the formula's `url` and `sha256` must
   be updated. The `brew bump-formula-pr` automation helps but does not eliminate
   the maintenance cost. Less popular tools are often out of date in
   `homebrew/core`.

3. **Conflict with language-native toolchains.** `brew install python` installs
   a Python that is NOT the system Python and NOT managed by `pyenv`. Users who
   mix `brew`-installed Python with `pip install --user` end up with packages
   installed in unexpected locations. The Homebrew Python, the system Python, and
   the `pyenv` Python are three different things.

4. **Formula DSL limitations.** The formula Ruby DSL is expressive but has sharp
   edges. `depends_on :xcode` means "needs Xcode" but doesn't specify which
   version. `conflicts_with` declarations are frequently stale. Custom `install`
   methods are arbitrary Ruby that can fail in unanticipated ways.

### Key Structural Insight for Nomi

Homebrew demonstrates the value of a low-friction distribution channel for
developer tools. `brew install tool` is 10 seconds of setup that replaces 10
minutes of "clone the repo, read the README, install dependencies, compile, add
to PATH." Nomi should aim for both `nomi install tool` (language-native, like
`cargo install`) and Homebrew formula support (system-native). The best tools
offer both.

---

## 11. Cross-Language Synthesis

### Structural Invariants (patterns that appear across ALL successful deployment systems)

1. **Content-addressed artifacts.** Every system that achieves reproducibility
   does it through content addressing — not version numbers, not tags, but
   cryptographic hashes of the artifact or its inputs. Docker image digests, Nix
   store paths, Go module checksums (`go.sum`), npm integrity hashes, Homebrew
   bottle SHAs, Wasm module hashes. The pattern: **name things by what they
   contain, not what you call them.**

2. **Deterministic builds (build reproducibility).** A deployment system is only
   as trustworthy as the guarantee that the same inputs produce the same outputs.
   Nix enforces this via sandboxing. Go achieves it via hermetic compilation
   (`CGO_ENABLED=0`). Docker approximates it with layered caching. The invariant:
   **if you cannot reproduce a build, you cannot reason about what you
   deployed.**

3. **The separation of build environment from runtime environment.** Multi-stage
   Docker builds, Nix derivations with separate build inputs, `cargo build
   --release` with dev dependencies excluded — every system converges on
   installing the full toolchain for building and only the runtime for running.
   The invariant: **the build environment is a superset of the runtime
   environment; ship only the subset needed at runtime.**

4. **A lockfile or equivalent pinning mechanism.** `Cargo.lock`,
   `package-lock.json`, `go.sum`, `Pipfile.lock`, `poetry.lock`, `mix.lock`,
   `build.zig.zon`, Ruby's `Gemfile.lock` — every language with a package
   manager eventually adds a lockfile. The invariant: **version ranges are for
   development; exact hashes are for deployment.**

5. **An artifact registry as the central distribution surface.** Docker Hub,
   PyPI, npm, crates.io, Maven Central, proxy.golang.org, Homebrew/core. Every
   ecosystem develops a central (or federated) registry where deployable
   artifacts are published, discovered, and fetched. The invariant: **a globally
   addressable namespace for artifacts.**

6. **The "one command to deploy" commitment.** `docker push`, `npm publish`,
   `cargo publish`, `go install`, `brew install`, `nix run`. The pattern: **the
   deployment command should be a single invocation that handles fetching,
   building (if needed), installing, and verifying.** Multi-step deployment
   scripts are a symptom of an immature system.

7. **Platform selectors in artifact names.** Wheels encode platform in the
   filename. Container images encode platform in the manifest (multi-arch).
   Homebrew bottles encode OS and version. Go module zips are platform-independent
   but Go binary downloads encode GOOS/GOARCH. The invariant: **the artifact
   name encodes the target platform, so fetching the right one is deterministic.**

### Genuine Design Forks (where ecosystems made genuinely different tradeoffs)

1. **Self-contained binary vs. runtime-dependent deployables.** Go and Rust
   produce a single self-contained binary. Python, Node, Ruby, and Java produce
   artifacts that require a runtime on the target. This is the fundamental fork.
   Self-contained binaries are simpler to deploy but larger. Runtime-dependent
   deployables are smaller but require runtime management.

2. **Source distribution vs. binary distribution.** Nix and `cargo install`
   distribute source and build on the target. Homebrew bottles and PyPI wheels
   distribute pre-built binaries. The fork: source distribution guarantees
   platform compatibility (build for your exact system) at the cost of build
   time. Binary distribution eliminates build time at the cost of needing
   pre-built artifacts for every target platform.

3. **Curated package set vs. open marketplace.** Nixpkgs is a single, coherent
   package set where everything is tested together. PyPI and npm are open
   marketplaces where anyone can publish anything, and compatibility is not
   guaranteed across packages. The fork: curation gives reliability; openness
   gives velocity.

4. **System-level dependency management vs. language-level management.**
   Homebrew and apt manage dependencies at the system level (one version of
   `openssl` for everything). Cargo and npm manage dependencies at the project
   level (different projects can have different versions). The fork:
   system-level management avoids duplication but creates version conflicts.
   Project-level management avoids conflicts but duplicates dependencies.

5. **Declarative deployment (Nix, Docker Compose) vs. imperative deployment
   (bash scripts, Ansible).** Declarative systems specify the desired state and
   let the tool compute the transition. Imperative systems specify the sequence
   of steps to reach the state. The fork: declarative is more reliable (idempotent,
   reversible) but harder to debug. Imperative is more intuitive (run these
   commands in order) but brittle.

6. **Function-level deployment (serverless) vs. application-level deployment
   (containers).** Serverless deploys individual functions; containers deploy
   entire applications. The fork: function-level gives infinite granularity and
   auto-scaling but forces statelessness. Application-level gives full control
   over the runtime but requires managing the process yourself.

7. **Just-in-time compilation (JVM JIT) vs. ahead-of-time compilation (Go,
   Rust).** JIT compilation defers optimization to runtime, enabling profile-guided
   optimization but adding warm-up time. AOT compilation pays the optimization
   cost at build time, giving predictable performance immediately. The fork: JIT
   can produce faster peak performance; AOT gives predictable, immediate
   performance and simpler deployment.

### Static vs. Dynamic Deployment Spectrum

The deployment spectrum ranges from "the artifact IS the program" to "the
artifact describes how to reconstruct the program." Each point on the spectrum
involves different tradeoffs:

| Point on spectrum | Example | Artifact | Target requires | Deploy complexity |
|---|---|---|---|---|
| Fully static native binary | Go (CGO=0), Rust (musl) | Single ~5 MB binary | Kernel only | Trivial |
| Static binary + libc | Rust (gnu), Go (CGO=1) | Single ~5 MB binary | Kernel + libc | Low |
| JIT + bundled runtime | jlink JRE + JAR | JRE dir + JAR (~50 MB) | Kernel only | Medium |
| Compiled + bundled runtime | `deno compile` | Single ~50 MB binary | Kernel only | Low |
| Source + lockfile + container | Python + Docker | Container image | Container runtime | Medium |
| Source + lockfile (serverless) | Python on Lambda | ZIP + config | Serverless platform | High (config) |
| Source + lockfile (raw) | Python + `pip install` | Source + requirements.txt | Python + pip | High (drift) |
| Universal bytecode | Wasm module | Single `.wasm` file | Wasm runtime | Low |
| Declarative system config | NixOS configuration | `.nix` expression | NixOS | Very high (learning curve) |

The structural pattern: as you move left (more self-contained), deployment
simplicity increases but artifact size increases. As you move right (more
dynamic), artifact size decreases but deployment complexity increases. The
exception is Wasm, which is both small and self-contained — it achieves this by
having the runtime be the platform rather than the artifact.

### The "Single Binary" Question: When Does It Matter?

A single binary matters when:

- **CLI tools for end users.** A developer installing `ripgrep` wants `brew
  install ripgrep`, not "install Rust, then clone the repo, then `cargo build
  --release`, then add to PATH." Single binary = frictionless distribution.

- **Serverless cold start limited.** When you pay for every millisecond of
  startup, extracting a Python environment or loading a JVM is expensive. A
  single binary that starts in 1 ms (Rust) vs. 200 ms (Python) is the
  difference between viable and non-viable for latency-sensitive serverless.

- **Security-sensitive environments.** A distroless container with a single
  binary has no shell, no package manager, no `curl`, no `python` — nothing an
  attacker can use for lateral movement.

A single binary does NOT matter when:

- **The deployment target is a long-running server with a known runtime.**
  If your production servers all have Python 3.12 installed, shipping Python
  source + dependencies is fine. The runtime is already managed.

- **The application is large and dependency-heavy.** A 200 MB Python ML
  application is not going to fit in a single binary no matter what tool you
  use. Containers are the right answer here, and container images are large
  regardless.

- **The developers and deployers are the same team.** Internal tools, data
  pipelines, batch jobs — if the person deploying is the person who wrote the
  code, the deployment friction matters less because they already have the full
  toolchain.

### Cross-Compilation: How Should a Language Support Targeting Different Platforms?

The cross-compilation design space has three approaches, ranked by complexity:

1. **Compiler-internal (Go).** The compiler knows every target platform's ABI,
   linker script, and syscall convention. Cross-compilation is two environment
   variables. Cost: the compiler team must maintain platform support for every
   target. Benefit: zero user configuration.

2. **Toolchain-managed (Rust).** The user installs a target (`rustup target add`)
   and optionally a cross-linker. `cross` uses Docker to provide the full
   cross-toolchain. Cost: one `rustup` command + Docker. Benefit: supports any
   target LLVM supports.

3. **External toolchain (C/C++).** The user installs a complete cross-compilation
   toolchain (cross-gcc, cross-binutils, target sysroot). Cost: significant
   setup. Benefit: maximal flexibility, production-hardened.

For Nomi: approach 1 is the aspirational target. Approach 2 is the realistic
near-term target (name a target, get a binary). Approach 3 is the fallback.

### Reproducible Builds: Deterministic Compilation, Lockfiles, Content-Addressed Artifacts

A reproducible build means: the same source code + the same build environment +
the same build command = the same binary, every time, everywhere. The components
are:

1. **Deterministic compilation.** The compiler must not embed timestamps, random
   values, build-machine hostnames, or non-deterministic map iteration order.
   Go's compiler guarantees this since Go 1.10. Rust's `-C
   codegen-units=1` and `SOURCE_DATE_EPOCH` enable it.

2. **Lockfiles.** Exact, content-addressed records of every dependency. Go's
   `go.sum`, Rust's `Cargo.lock`, npm's `package-lock.json`. Without a lockfile,
   `npm install` resolves version ranges, and two runs can download different
   packages.

3. **Build sandboxing.** The build must not access the network, must not read
   files outside declared inputs, and must not depend on ambient state (env
   vars, time, hostname). Nix enforces this strictly. Bazel enforces this
   strictly. Docker approximates it.

4. **Content-addressed storage.** Artifacts are stored by their content hash
   (SHA-256), not by their name + version. Nix: `/nix/store/<hash>-<name>`.
   Docker: `image@sha256:...`. npm: `integrity` field with SRI hashes.

For Nomi: deterministic compilation should be a design requirement, not an
afterthought. Lockfile format should be specified before the package manager
is implemented. Content-addressed artifact storage should be the default.

### Version Management: Multiple Language Versions, Runtime Version Pinning

Version management is the problem of having multiple versions of a language
runtime installed and selecting the right one per-project. The approaches:

- **Shim-based (pyenv, rbenv, nodenv, goenv).** A `python` shim intercepts the
  command, reads `.python-version` in the current directory, and invokes the
  correct Python. Simple but slow (every invocation reads a file) and fragile
  (shell integration needed).

- **Path-based (nvm, asdf, mise-en-place).** Modifies `PATH` to include the
  selected version's `bin/` directory. Fast (no per-invocation overhead) but
  requires shell hooks for auto-switching.

- **Container-based (Docker, Dev Containers).** The language version is
  specified in the `Dockerfile` or `devcontainer.json`. No version manager
  needed — the container IS the environment. Heavyweight but reliable.

- **Locked-in-artifact (Go binaries, `deno compile`, GraalVM Native Image).**
  The language version is compiled into the artifact. No version manager needed
  on the target machine. The ultimate solution — but only works for compiled
  languages.

For Nomi: the long-term approach should be "locked-in-artifact" — the Nomi
compiler version is embedded in the binary. The near-term Python-hosted
approach should support `.nomi-version` files (like `.python-version`) and
integrate with `mise` or `asdf`.

### CI/CD Integration: How Deployment Integrates with Continuous Delivery

The deployment step in a CI/CD pipeline follows a universal pattern, regardless
of language:

1. **Restore the build environment** (install language toolchain, restore
   dependency cache).
2. **Build** (compile, bundle, package — produce the deployable artifact).
3. **Test the artifact** (smoke tests against the built artifact, not the source).
4. **Store the artifact** (push to registry: Docker Hub, PyPI, npm, S3, etc.).
5. **Deploy** (update the running environment to use the new artifact).
6. **Verify** (health checks against the deployed service).

Each language's deployment toolchain maps onto this pattern differently. The
key insight: **the artifact should be built once and promoted through
environments.** The artifact that ran in CI staging tests should be the exact
same bytes that run in production. This is the "build once" principle, and it
is violated by any deployment model that recompiles or re-resolves dependencies
at deploy time.

### Anti-Patterns: Deployment Mistakes That Consistently Hurt Ecosystems

1. **Building at deploy time.** If `pip install -r requirements.txt` runs on the
   production server, you are building at deploy time. The production server
   needs network access, a C compiler, and resolves version ranges at the
   moment of deployment. This is the root cause of "it passed CI but fails in
   prod."

2. **Mutable tags.** `docker pull myapp:latest` is a deploy-time lottery. The
   `latest` tag means different things at different times. Always deploy by
   digest (`myapp@sha256:...`) or immutable version tag.

3. **Shell scripts as deployment mechanism.** "SSH into the server and run
   `deploy.sh`" is the most common deployment anti-pattern. It is not
   reproducible, not auditable, not idempotent, and not rollback-able.

4. **No artifact promotion.** Building the artifact separately in dev, staging,
   and production environments (with different build flags, env vars, or
   dependency versions) means you never test what you deploy.

5. **Platform-gated tooling.** "Deployment only works on Linux — sorry, macOS
   users" — any tool that requires a specific host platform for builds is a
   barrier. Cross-compilation and containerized builds solve this.

6. **Version range resolution at deploy time.** `pip install "requests>=2.28"`
   in production means the production environment might install `requests 2.31`
   today and `requests 2.32` tomorrow. Lockfiles exist to prevent this.

7. **Runtime environment managed by convention rather than specification.**
   "We all know production uses Python 3.11" — until someone deploys a service
   that needs 3.12 and the production environment gets updated silently.

---

## 12. Nomi Adopt / Refuse / Adapt Table

The table below gives concrete recommendations for Nomi's deployment posture.
"Near-term" means while Nomi is Python-hosted. "Long-term" means when Nomi has
a standalone toolchain. "Adopt" means take as-is. "Refuse" means reject and
don't imitate. "Adapt" means take the idea but reshape it for Nomi's context.

| # | Pattern | Decision | Rationale & Nomi Action |
|---|---|---|---|
| 1 | **Content-addressed artifacts** | Adopt (long-term) | Every Nomi build artifact should be named by SHA-256 hash. The `nomi build` output should be content-addressable: `target/<hash>/` not `target/release/`. Docker images, Wasm modules, and native binaries all follow this pattern. |
| 2 | **Lockfile as a required build input** | Adopt (both) | Nomi should have a `nomi.lock` file (like `Cargo.lock`, `go.sum`) that records exact dependency hashes. Near-term: generate one from `requirements.txt` hashes. Long-term: integrate with the package resolver. |
| 3 | **Multi-stage build separation** | Adopt (long-term) | The Nomi compiler toolchain should be separate from the Nomi runtime. `nomi build` should produce an artifact that does not need the compiler. Docker's multi-stage pattern is the deployment model to target. |
| 4 | **Cross-compilation as a built-in** | Adopt (long-term) | Like Go's `GOOS`/`GOARCH`, Nomi should support `nomi build --target wasm32-wasi` and `nomi build --target x86_64-linux` with zero toolchain setup. This is a hard requirement for Wasm/edge deployment. |
| 5 | **Deterministic builds by default** | Adopt (long-term) | No timestamps, no hostname, no non-deterministic iteration order in the compiler. The same source + same toolchain = same binary. Go's `-trimpath` and Rust's `SOURCE_DATE_EPOCH` are the models. |
| 6 | **Single-binary deployment for CLI tools** | Adopt (long-term) | `nomi compile --standalone` should produce a self-contained executable. Near-term: via PyInstaller/Nuitka. Long-term: native compilation to LLVM/MLIR → native binary. |
| 7 | **Wasm as a first-class compilation target** | Adopt (long-term) | Every Nomi program should be compilable to a `.wasm` module targeting WASI preview 2. This is table-stakes for edge/serverless deployment. The component model should be a design input for Nomi's FFI/ABI. |
| 8 | **Homebrew / system package distribution** | Adopt (both) | The Nomi toolchain itself should be installable via `brew install nomi`. Provide bottles for macOS and Linux. This is the lowest-friction way for developers to install Nomi. |
| 9 | **Docker as the universal deployment vehicle** | Adapt (both) | Near-term: Nomi programs deploy like Python programs (Dockerfile with `pip install nomi` + source). Long-term: Nomi programs deploy with a multi-stage Dockerfile (build stage with `nomi build`, runtime stage with `FROM scratch` + binary). |
| 10 | **Dynamic runtime dependency** | Refuse (long-term) | Java's "install the JRE" model is the anti-pattern. If Nomi needs a runtime, it should be bundlable, minimal, and versioned with the compiler. Better: Nomi should not need a runtime on the target. |
| 11 | **Serverless cold start as a design constraint** | Adopt (long-term) | Nomi programs should start in under 20 ms. This means: no JIT warmup, no class loading, no dependency extraction at startup. The Nomi runtime (if any) should be minimal and instant-on. |
| 12 | **Building at deploy time** | Refuse (both) | Never resolve dependencies, compile, or link on the production target. The artifact should be the artifact. Near-term: Docker image as the artifact. Long-term: native binary or Wasm module. |
| 13 | **Mutable version tags** | Refuse (both) | `nomi install mypkg@latest` should be a development convenience that expands to a specific version. Deployment should always use exact digests. Docker's `latest` tag is the cautionary tale. |
| 14 | **Shell scripts for deployment** | Refuse (both) | No `deploy.sh`, no `ssh production "git pull && restart"`. Nomi should provide `nomi deploy` that integrates with standard CI/CD patterns (push to registry, then promote). |
| 15 | **Nix-style sandboxed builds** | Adapt (both) | Near-term: use Docker or `pip` hash-checking. Long-term: aim for deterministic, sandboxed builds. But do NOT adopt Nix's custom expression language — use Nomi's own language for build configuration. |
| 16 | **Language-native install command** | Adopt (long-term) | `nomi install <package>` should work like `cargo install` or `go install`. Download, compile (or fetch pre-built binary), install to `~/.nomi/bin`. This is the primary distribution channel for Nomi CLI tools. |
| 17 | **Declarative build configuration** | Adopt (both) | `nomi.toml` (near-term: `pyproject.toml`) should declaratively specify build targets, dependencies, and deployment configuration. No imperative build scripts. Rust's `Cargo.toml` and Go's `go.mod` are the models. |
| 18 | **Runtime version pinning in the project file** | Adopt (both) | `nomi.toml` should declare the Nomi version range (like `requires-python`). Near-term: `.nomi-version` file. Long-term: compiled into the artifact, with `nomi run` checking compatibility at invocation time. |
| 19 | **Artifact promotion across environments** | Adopt (long-term) | `nomi promote <artifact-hash> --from staging --to production`. The artifact built in CI should be immutable and promoted through environments. The "build once" principle should be enforced by the toolchain. |
| 20 | **Bottle/package registry integration** | Adopt (long-term) | When Nomi can produce native binaries, provide a `nomi publish` command that pushes to a Nomi package registry AND to Homebrew/apt/choco as appropriate. Distribution is multi-channel by default, not an afterthought. |

---

## 13. Sources

- [Go: Compile and install the application](https://go.dev/doc/tutorial/compile-install)
- [Go: Static linking and CGO](https://www.arp242.net/static-go.html)
- [Go: Module mirror and checksum database](https://go.dev/blog/module-mirror-launch)
- [Rust: Cross-compilation](https://rust-lang.github.io/rustup/cross-compilation.html)
- [Rust: `cross` tool](https://github.com/cross-rs/cross)
- [Rust: Musl static binaries](https://doc.rust-lang.org/edition-guide/rust-2018/platform-and-target-support/musl-support-for-fully-static-binaries.html)
- [Python: Packaging overview (PyPA)](https://packaging.python.org/en/latest/overview/)
- [Python: manylinux wheels (PEP 600)](https://peps.python.org/pep-0600/)
- [Python: PyInstaller](https://pyinstaller.org/)
- [Python: Nuitka](https://nuitka.net/)
- [Python: shiv](https://github.com/linkedin/shiv)
- [npm: package-lock.json specification](https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json)
- [Deno: `deno compile`](https://docs.deno.com/runtime/reference/cli/compile/)
- [Bun: `bun build --compile`](https://bun.sh/docs/bundler/executables)
- [Docker: Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Distroless container images](https://github.com/GoogleContainerTools/distroless)
- [AWS Lambda: Deployment package limits](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)
- [Cloudflare Workers: How Workers works](https://developers.cloudflare.com/workers/reference/how-workers-works/)
- [Java: jlink](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jlink.html)
- [GraalVM Native Image](https://www.graalvm.org/latest/reference-manual/native-image/)
- [Spring Boot: Container images](https://docs.spring.io/spring-boot/docs/current/reference/html/native-image.html)
- [Nix: How Nix works](https://nixos.org/guides/how-nix-works.html)
- [NixOS: Declarative system configuration](https://nixos.org/manual/nixos/stable/)
- [Nix Flakes](https://nixos.wiki/wiki/Flakes)
- [WebAssembly: Core specification](https://webassembly.github.io/spec/core/)
- [WASI: Preview 2](https://github.com/WebAssembly/wasi-cli)
- [Was component model](https://component-model.bytecodealliance.org/)
- [Fastly Compute: Wasm on the edge](https://www.fastly.com/documentation/guides/compute/)
- [Fermyon Spin](https://developer.fermyon.com/spin/v2/index)
- [Homebrew: Formula cookbook](https://docs.brew.sh/Formula-Cookbook)
- [Homebrew: Bottles](https://docs.brew.sh/Bottles)
- [TinyGo: WASI support](https://tinygo.org/docs/guides/webassembly/)
- [Reproducible Builds project](https://reproducible-builds.org/)
