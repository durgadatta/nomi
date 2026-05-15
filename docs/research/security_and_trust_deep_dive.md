# Security and Trust: A Deep Dive

## Status

Raw research notes. This document surveys how programming languages and their
ecosystems handle security, trust, and capability boundaries. It covers
supply-chain integrity, secret management, sandboxing, capability-based
security, cryptographic hygiene, memory safety, information flow control,
authentication design, and redaction. The analysis is organised as ten
system-level deep dives followed by a cross-language synthesis and a Nomi
Adopt/Refuse/Adapt table.

Companion docs: `data_boundary_systems_deep_dive.md` (data boundary), 
`diagnostics_and_explanations_comparative.md` (explain/error reporting),
`packaging_and_project_structure_deep_dive.md` (dependency management).

## Purpose

Security in a programming language is not a feature bolted on after design.
It is the set of structural properties that make it hard to write insecure
programs and easy to write secure ones. This document asks three questions
for every system studied:

1. What is the core security philosophy?
2. What worked exceptionally well, and what failed?
3. What is the key structural insight for Nomi?

The goal is not to produce a security checklist. It is to identify the
invariants that all trustworthy systems share, the genuine design forks
where reasonable systems disagree, and the concrete decisions Nomi should
make at the language level — not deferred to a linter, a CI step, or a
third-party tool.

---

## 1. Nix: The Reproducibility-and-Integrity Maximalist

### 1.1 Core Security Philosophy

Nix is built on a single radical idea: **if you know the exact inputs, you
can reproduce the exact outputs, and you can verify that nothing was
tampered with.** This is not a security add-on; it is the organizing
principle of the entire system. Every package, every configuration, every
build artifact lives at a path derived from a cryptographic hash of its
inputs. The store path `/nix/store/<hash>-<name>` encodes integrity into
the filesystem layout itself.

The mechanism is the **fixed-output derivation**. A derivation is a
specification of a build: source inputs, build command, environment
variables, and dependencies. The derivation is hashed to produce the store
path. If anything changes — a source file, a compiler flag, a dependency
version — the hash changes, and the output lands at a different path. This
means you can have multiple versions of the same package coexisting
without conflict, but it also means that if you can verify the hash, you
can verify the entire transitive build graph.

Input-addressed builds take this further. Rather than trusting that a
builder produced the right output, input-addressed builds derive the
output hash from the inputs alone, then verify that the build actually
produces that output. This is the gold standard: you do not trust the
builder; you trust the hash function.

### 1.2 The Nix Sandbox

Nix builds run in a sandbox by default on Linux (via user namespaces and
mount namespaces) and optionally on macOS (via sandbox-exec). The sandbox:

- Restricts network access (no internet during builds).
- Restricts filesystem access to explicitly declared inputs.
- Runs builds as an unprivileged build user (`nixbld`).
- Prevents writes outside the designated output directory.

The sandbox is not a security boundary against a malicious builder — a
determined attacker with arbitrary code execution in a build can
potentially escape. It is a **reproducibility boundary**: it catches
accidental dependencies on undeclared inputs (a file in `/usr/lib`, a
network fetch, a system configuration). The sandbox makes "it works on my
machine" into a build failure.

### 1.3 Binary Cache Trust

Nix's binary cache (`cache.nixos.org`) serves pre-built store paths. The
cache signs store path metadata with a private key; the client verifies
the signature. This is a **TOFU (Trust On First Use) model**: the first
time you substitute a path from the cache, you trust the cache's public
key embedded in your Nix configuration. Subsequent fetches verify that
signature.

The `narHash` (Nix ARchive hash) is the integrity anchor. Every store
path has a `narHash` that covers the full contents of the store object.
When the binary cache serves a `.nar` file, the client computes its hash
and checks it against the expected `narHash` from the derivation. If they
differ, the substitution is rejected.

The limitation: you are trusting the cache operator to serve binaries
that correspond to the claimed sources. Nix cannot verify that the binary
was actually built from those sources without a **trusted build** —
either you build it yourself, or you trust a third party that attests to
the build result. This is where Nix's model meets SIGSTORE/sigstore (see
Section 4).

### 1.4 Nix Flakes and Integrity

Nix flakes lock inputs with a `flake.lock` that records exact Git
revisions and `narHash` values. When you evaluate a flake, Nix verifies
that the fetched sources match the recorded hashes. This is essentially
a content-addressed import system: the lock file is a Merkle tree of the
entire dependency graph, and any tampering with any input is detected as
a hash mismatch.

Flakes also introduce **pure evaluation**: by default, flake evaluation
does not read files outside the flake's source tree and does not access
environment variables. This prevents "works on my machine" evaluation
leaks and makes the evaluation itself reproducible.

### 1.5 What Nix Can and Cannot Guarantee

**Can guarantee:**
- Integrity: if the hash matches, the bytes are what you expect.
- Reproducibility of the dependency graph: every machine evaluating the
  same `flake.lock` gets the same sources.
- Build isolation from undeclared inputs (via sandbox).

**Cannot guarantee:**
- That the source code is not malicious (Nix hashes code, not intent).
- That a binary from the cache corresponds to the claimed source (without
  trusted-build attestations).
- That the build process itself is free of supply-chain attacks (e.g., a
  compromised compiler in the bootstrap chain — the Thompson attack).

### 1.6 Key Structural Insight for Nomi

Nix's core insight is that **content addressing is the foundation of
trust**. When a dependency is named by its hash, integrity is not a
separate verification step — it is the naming convention. Nomi should
adopt content-addressed imports for remote dependencies: an import
statement that includes a hash is self-verifying. The SHA-256 of a module
source becomes its identity. This is already the Dhall model (which Nomi
follows for data boundary imports), and it should extend to code imports.

The second insight is that **sandboxing is a reproducibility tool before
it is a security tool**. Nomi's `where` clause and `data` constraint
system already create local reasoning boundaries. The next layer — build
or evaluation sandboxing — should be designed to catch accidental
dependency on undeclared context, mirroring Nix's "no network during
build" principle.

---

## 2. Capability-Based Security

### 2.1 Core Security Philosophy

Capability-based security (or "ocap" for object-capability) starts from a
different place than most security models. The principle of least
authority (POLA) is the organizing idea: **a computation should have
access only to the resources it needs, and no more.** In a capability
system, you do not ask "is this user allowed to open this file?" You ask
"does this computation possess a capability that grants file access?"

A capability is an unforgeable reference. In a pure ocap system, there is
no global namespace for resources — no filesystem root, no process table,
no `/etc/passwd`. A program starts with a set of initial capabilities
(its arguments, its environment), and it can only access what those
capabilities grant. It cannot manufacture new capabilities out of thin
air; capabilities must be handed to it explicitly.

This is the opposite of the ACL (Access Control List) model. In ACL
systems, the ambient authority is the default: a program runs as a user,
and the user's permissions determine what the program can do. The program
can access anything the user can access. In a capability system, the
program can access nothing except what it is explicitly given.

### 2.2 The E Language and Object-Capability Model

The E language (Mark S. Miller, late 1990s) is the canonical programming
language embodiment of capability security. E combines:

- **Unforgeable object references** — you cannot fabricate a reference to
  an object you have not been given.
- **No static mutable state** — all mutable state is encapsulated in
  objects reachable only through capabilities.
- **Event-loop concurrency** — vat-based, with each vat having its own
  set of capabilities. Vats communicate through asynchronous messages.
- **The "rights amplification" pattern** — two capabilities can be
  combined to produce a capability that neither alone would grant.

In E, a file is not opened by calling `open("/path/to/file")` with a
string path. A file is opened by calling `fileCap.open()` where
`fileCap` is a capability handed to the program at startup. There is no
global filesystem namespace to traverse.

### 2.3 Capability Patterns

Three patterns from the ocap literature are particularly important for
language design:

**Sealer/Unsealer.** A sealer creates a pair of related capabilities: a
sealer that can "seal" a value into an opaque box, and an unsealer that
can extract it. The unsealer is a capability — if you do not have it, you
cannot open the box. This pattern is used for:
- Branding (making values that only trusted code can inspect).
- Encapsulation (hiding implementation details behind a capability
  boundary).
- Rights management (a sealed value acts as a token that grants authority
  to whoever holds the matching unsealer).

**Membrane.** A membrane wraps a set of capabilities to filter or
transform messages passing through. Think of it as a proxy that
interposes on every capability invocation. Membranes enable:
- Revocation (wrap a capability in a revocable membrane; revoke the
  membrane later).
- Auditing (log every access to a capability).
- Attenuation (restrict the arguments or results of capability
  invocations — for example, wrap a file-write capability so it can only
  write to a specific directory).

**Powerbox.** When a program needs a capability it does not have, it asks
the user through a powerbox — a UI pattern where the user selects a
resource, and the powerbox grants a capability for that specific resource
only. Sandstorm uses this pattern: an app requests "access to a file,"
the user picks the file, and the app receives a capability for that file
— not for the whole filesystem.

### 2.4 Modern Capability Systems

**Sandstorm** (Kenton Varda, 2015-2017) was a web app platform built on
capability security. Each app ran in an isolated grain with no network
access, no filesystem access, and no ambient authority. Apps communicated
through capability-based RPC (Cap'n Proto). The user's browser mediated
all external interactions. Sandstorm demonstrated that ocap security is
practical for real applications — and that the UX challenge (powerbox,
sharing, revocation) is harder than the technical challenge.

**Capsicum** (FreeBSD/Google, since FreeBSD 9) is a capability mode for
file descriptors. Once a process enters capability mode, it cannot access
the global filesystem namespace at all. It can only use file descriptors
it already holds. `openat()` with a directory file descriptor replaces
`open()` with a path string. This is a pragmatic retrofit of capability
principles onto a Unix kernel — and it works. Chrome on FreeBSD uses
Capsicum to sandbox renderer processes.

**Fuchsia** (Google's microkernel OS) is built on capability principles
from the ground up. Every kernel object handle is a capability. Processes
start with no handles and receive them through explicit transfer. The
component framework (CMX) uses capability routing to declare what each
component needs. Fuchsia is the most ambitious attempt to build a
capability operating system for general-purpose use.

### 2.5 What Worked and What Failed

**Worked:**
- The sealer/unsealer pattern is genuinely useful in library design —
  it appears in Python (`secrets.compare_digest` as a primitive), in
  JavaScript (hardened closures in SES), and in capability-safe subsets
  of languages.
- The principle "no ambient authority" is a powerful design constraint
  even when not fully realized. Every time a system says "pass the
  database handle explicitly rather than reaching for a global," it is
  applying POLA.
- Capsicum showed that capability principles can be retrofitted onto
  existing kernels without a full rewrite.

**Failed:**
- The E language did not achieve mainstream adoption. The ocap community
  remains small. The problem is partly network effects (no one uses an
  ocap OS, so no one writes ocap programs, so there is no demand for an
  ocap OS) and partly a mismatch with developer expectations (programmers
  expect to be able to do `open("/etc/passwd")` and get a file handle).
- Sandstorm's company (Sandstorm.io) failed commercially. The platform
  was technically coherent but the market for self-hosted capability-secure
  web apps was too small.
- Full ocap purity requires language-level enforcement. You cannot bolt
  capabilities onto a language that has static mutable state, global
  variables, and unrestricted reflection. Most mainstream languages cannot
  be made ocap-safe without an impractical subset.

### 2.6 Key Structural Insight for Nomi

Nomi does not need to be a pure ocap language. But it should adopt three
capability patterns as **library-level conventions with language support**:

1. **No global ambient authority for IO.** File handles, network sockets,
   and environment variables should be explicitly passed to functions that
   use them. Nomi's `data` and config boundary already separates
   environment ingestion from business logic; this should extend to all
   IO capabilities.

2. **Sealer/unsealer as a standard library pattern.** A `Capability`
   module should provide sealer/unsealer as a primitive, not a pattern
   users must implement themselves. This is useful for secure token
   handling, API key wrapping, and privilege separation within a program.

3. **Capability scopes (future layer).** The Nomi docs already reference
   "capability scopes" as a future concern. These should follow the
   powerbox model: a block of code declares what capabilities it needs,
   and the caller provides them. This is the block-call pattern Nomi
   already has, with capability requirements as a parameter policy.

---

## 3. Secrets Management

### 3.1 Core Security Philosophy

Secrets management is the problem of storing, distributing, and using
values that should not be widely visible: API keys, database passwords,
TLS private keys, auth tokens. The core tension: secrets must be
available to programs that need them, but every place they are stored or
transmitted expands the attack surface.

There are two fundamentally different approaches:

**Secret stores** (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault)
centralize secrets, audit access, rotate values, and serve them to
applications on demand. The application does not store the secret; it
fetches it at runtime. This is the right model for production
infrastructure but is heavyweight for development and small projects.

**Encrypted-at-rest** (SOPS, sealed secrets, `sops-nix`) keep secrets in
version control but encrypted. Only authorized keys can decrypt them. The
secret is closer to the code that uses it, which improves developer
ergonomics at the cost of a broader attack surface (anyone with access to
the repo has the ciphertext; anyone with the decryption key has the
plaintext).

### 3.2 Vault (HashiCorp)

HashiCorp Vault is the standard-bearer for centralized secret management.
Its design principles are instructive:

- **Dynamic secrets:** rather than storing a database password, Vault
  generates a temporary credential on demand and revokes it after a TTL.
  The application never sees a long-lived secret.
- **Audit logging:** every secret access is logged. You know who accessed
  what and when.
- **Leasing and renewal:** secrets are leased with a TTL. Applications
  must renew their lease. If an application crashes or is terminated, the
  secret is automatically revoked when the lease expires.
- **Encryption as a service:** Vault can perform cryptographic operations
  (encrypt, decrypt, sign, verify) without exposing key material to the
  caller.

The Vault model is powerful but operationally complex. It requires
running a Vault cluster, managing unseal keys, configuring auth backends,
and instrumenting applications to fetch and renew secrets. For Nomi's
design scope (a language, not an infrastructure platform), the important
lesson is the **lease/revocation model** — secrets should have a bounded
lifetime, and the language should make it easy to express "this value
expires after time T."

### 3.3 SOPS and Sealed Secrets

Mozilla SOPS (Secrets OPerationS) takes a different approach. Secrets
are stored as encrypted files in version control. SOPS encrypts the
values but preserves the structure (YAML, JSON, .env, binary). Only the
values are encrypted; the keys remain in plaintext so you can see what
secrets exist and how they are structured.

`sops-nix` integrates SOPS with NixOS, decrypting secrets at system
activation time and placing them in protected files readable only by the
services that need them.

The key insight of SOPS is that **structure is not secret**. The fact
that a config has a `database_password` field is not sensitive; the
password value is. Encrypting the entire file obscures structure;
encrypting values only preserves readability while protecting the secret.

### 3.4 Environment Variables and the "Secret in Config" Problem

The most common (and worst) approach to secrets management is storing
secrets in environment variables and config files. The problems:

- **Accidental logging:** `console.log(process.env)` or `print(os.environ)`
  dumps every secret into logs.
- **Child process inheritance:** environment variables are inherited by
  all child processes by default. A process you spawn for image
  conversion can see your database password.
- **Inspectability:** `/proc/<pid>/environ` is world-readable (on many
  systems). Any user on the same machine can read your secrets.
- **No access control:** environment variables have no notion of which
  code should or should not have access. Every line of code in the
  process can read every environment variable.

Despite these problems, environment variables are ubiquitous because
they are supported by every language, every orchestration platform
(Kubernetes secrets are injected as env vars or files), and every CI
system.

### 3.5 Language Standard Library Approaches

**Python's `secrets` module** (Python 3.6+) provides cryptographically
secure random number generation. It does NOT handle secret storage,
retrieval, or lifecycle. It is a building block, not a solution.

**Ruby's `SecureRandom`** is similar — secure random generation, no
secret lifecycle management.

**Rust** has no stdlib secrets module. Individual crates handle secret
management, with varying quality. The `secrecy` crate provides
wrapping types that prevent accidental logging and comparison.

**Go's `crypto/`** packages provide secure random generation but no
secret lifecycle primitives.

The pattern across all languages: standard libraries provide secure
randomness (necessary but insufficient) and leave everything else to
third-party libraries or infrastructure.

### 3.6 Key Structural Insight for Nomi

Nomi should provide a `Secret[T]` wrapper type in the standard library
with three critical behaviors:

1. **Redacted display by default.** `print(api_key)` outputs
   `Secret("***")`, never the plaintext. The only way to extract the
   value is through an explicit boundary like `api_key.reveal()` or an
   IO function that is typed to accept `Secret[T]`.

2. **Non-inheritance by child processes.** When spawning a subprocess,
   `Secret` values should not be passed to the child's environment
   unless explicitly authorized. The default should be: secrets are
   not inherited.

3. **Constant-time comparison.** `Secret[str]` equality should use
   constant-time comparison to prevent timing attacks on token validation.

This is already sketched in Nomi's research notes (see
`everyday_fallback_simplification_ideas.md` §23), and it maps to the
existing `data` boundary concept: a `Secret[T]` is a `data` type whose
display policy is redacted.

---

## 4. Supply-Chain Security

### 4.1 Core Security Philosophy

Software supply-chain security is the problem of ensuring that the
dependencies you use are the ones you think you are using, and that they
have not been tampered with. The threat model includes:

- **Typosquatting:** publishing a package with a similar name to a
  popular package, hoping someone installs it by mistake.
- **Dependency confusion:** publishing a package with the same name as a
  private internal package, hoping the resolver picks the public one.
- **Account takeover:** compromising a maintainer's account and publishing
  a malicious version.
- **Malicious maintainer:** a maintainer intentionally publishing
  backdoored code.
- **Build system compromise:** compromising the build infrastructure
  rather than the source code.

### 4.2 npm: The Left-Pad and Event-Stream Incidents

The npm ecosystem has been shaped by two defining incidents:

**Left-pad (2016).** A developer unpublished 11-line package that padded
strings. Thousands of projects — including Babel and React — broke
because their dependency trees transitively depended on it. The
structural problem: npm allowed unpublishing packages that others
depended on. The fix: npm changed its unpublish policy (you can no longer
unpublish a package if others depend on it, except in limited
circumstances). The deeper lesson: **immutability of published packages
is a security property.** If a version can disappear, supply-chain
integrity is impossible.

**Event-stream (2018).** A malicious maintainer was given publish access
to the `event-stream` package. They published a version that included a
dependency (`flatmap-stream`) containing obfuscated code that stole
Bitcoin wallets. The attack targeted a specific wallet (`copay-dash`)
and was discovered because the malicious code used a deprecated
`crypto.createDecipher` which triggered a deprecation warning. The lesson:
**trust in maintainers is not transitive.** The trust model of "I trust
the package, so I trust anyone the maintainer gives access to" is broken.

### 4.3 PyPI: Typosquatting and Package Name Confusion

PyPI (Python Package Index) sees a steady stream of typosquatting
attacks. Attackers publish packages with names like `requsts` (missing
`e`), `djanjo` (transposed letters), or `python-dateutil` (hyphen vs
underscore confusion). The attacks range from information-gathering (phone
home with hostname and username) to full remote access trojans.

PyPI's response has included:
- Name similarity checks during package registration.
- Mandatory two-factor authentication for maintainers.
- API tokens with scoped permissions instead of username/password
  authentication.
- Trusted publishing (OIDC-based, no long-lived tokens).
- The PyPI Security Key initiative (hardware-backed 2FA for critical
  packages).

The structural problem: PyPI has no mechanism for namespace ownership.
Anyone can register any name that is not already taken. Compare this to
Go, where the import path includes the domain name (`github.com/user/pkg`)
— namespace ownership is delegated to the domain name system.

### 4.4 Go's Sum Database and Transparency Model

Go's approach to supply-chain security is the most architecturally
coherent of any major language ecosystem. Two key components:

**The checksum database (sum.golang.org).** When `go get` fetches a
module, it requests the module's `go.sum` entry from the checksum
database. The database is a transparency log (a Merkle tree) that records
every module version and its SHA-256 hash. The key properties:

- **Append-only:** once a hash is recorded, it cannot be changed or
  removed. This prevents targeted attacks where a malicious version is
  served to a specific victim and then removed.
- **Verifiable:** the database publishes a signed tree head. Anyone can
  verify that a record is in the log and that the log has not been forked.
- **Auditable:** anyone can monitor the log for unexpected entries (e.g.,
  a new version of a package that was supposedly unmaintained).

**The module proxy (proxy.golang.org).** The proxy caches module source
code. Combined with the sum database, a user's `go.sum` file becomes a
cryptographic record of every module version used in the build, with
hashes verifiable against the transparency log.

The Go model does not prevent malicious code from being published. It
prevents a malicious version from being **served selectively** or
**retroactively altered** — which converts supply-chain attacks from
targeted (hard to detect) to broad (easy to detect, because everyone sees
the same version).

### 4.5 Sigstore and Cosign

Sigstore is a Linux Foundation project that provides free, short-lived
code signing certificates bound to OIDC identities. The key components:

- **Fulcio** (certificate authority): issues short-lived (10-minute)
  signing certificates based on OIDC identity (Google, GitHub, Microsoft).
- **Rekor** (transparency log): records every signature in an append-only
  log, providing non-repudiation and auditability.
- **Cosign** (CLI): signs and verifies container images and other
  artifacts using Fulcio-issued certificates.

The sigstore model is significant because it eliminates the hardest part
of code signing: key management. Instead of maintaining long-lived signing
keys, developers authenticate with their existing identity (Google account,
GitHub account) and receive a short-lived certificate. The transparency
log provides the long-term record.

This maps directly to the SLSA (Supply-chain Levels for Software
Artifacts) framework, which defines four levels of supply-chain integrity:

- **SLSA 1:** Build is documented (provenance exists).
- **SLSA 2:** Build service is versioned and generates authenticated
  provenance.
- **SLSA 3:** Source and build platforms meet cryptographic standards
  (isolated, parameterless, hermetic).
- **SLSA 4:** Two-person review, hermetic builds, reproducible, all
  dependencies tracked.

### 4.6 What Language-Level Features Affect Supply-Chain Security?

Several language design decisions directly affect supply-chain risk:

**Import path naming.** Go's domain-name imports (`import
"example.com/user/project"`) prevent dependency confusion and
typosquatting by anchoring packages to domain ownership. NPM's bare-name
imports (`import "left-pad"`) create a global namespace with no ownership
model.

**Version resolution algorithm.** Go's **Minimal Version Selection
(MVS)** picks the oldest version that satisfies all constraints — this is
deterministic and minimizes the attack surface from dependency updates.
Rust's Cargo resolver picks the maximum semver-compatible version —
deterministic for a given lockfile, but `cargo update` can pull in
surprising changes. NPM's resolver has historically been the most brittle
(with `package-lock.json` now providing determinism).

**Macro and metaprogramming surface.** Rust's proc macros can execute
arbitrary code at compile time. A malicious proc macro can read files,
exfiltrate environment variables, or inject code into the compiled binary.
The `cargo careful` project tracks this risk. Languages that restrict
macro power (Go has no macros; Zig's comptime is sandboxed) reduce the
supply-chain attack surface.

**Unused dependency pruning.** Go refuses to compile if you import a
package but do not use it. Rust warns on unused dependencies. NPM does
not enforce usage — you can `npm install` a thousand packages, use none
of them, and your lockfile will still track them. Unused dependencies are
a security risk because they expand the attack surface without providing
any value.

### 4.7 Key Structural Insight for Nomi

Nomi should build on the data-boundary import model already established
(Dhall-style content-addressed imports) and extend it to code:

1. **Content-addressed imports for all external dependencies.** An import
   of the form `import "module" sha256:deadbeef...` is self-verifying.
   The hash is the identity. This is optionally enforced: local imports
   do not require hashes, remote imports do.

2. **Lockfile as a Merkle tree.** A `nomi.lock` records the hash of every
   dependency, transitively. Verification is a single hash comparison at
   the root.

3. **No bare-name imports from a global namespace.** Import paths include
   a domain component (Go-style) or are local relative paths. There is no
   `nomi install left-pad`.

4. **Unused dependencies are a compile error.** Nomi should refuse to
   build if an imported module is not used. This is a security feature
   as much as a hygiene feature.

5. **Macro sandboxing (future).** When Nomi grows metaprogramming, macros
   should not have ambient authority. They should receive explicit
   capabilities (the AST node they process, a diagnostic emitter) and
   nothing else.

---

## 5. Sandboxing and Isolation

### 5.1 Core Security Philosophy

Sandboxing is the practice of restricting what a program can do: what
files it can read, what network hosts it can connect to, what environment
variables it can access, what system calls it can make. There is a
spectrum from "no restrictions" (C programs with full ambient authority)
to "pure capability" (E programs with no ambient authority at all).

The key design question is not "should we sandbox?" but **"where on the
spectrum does the sandbox go, and who decides what capabilities a program
gets?"**

### 5.2 Deno's Permission Model

Deno (Ryan Dahl's successor to Node.js) takes the clearest position in
the language-runtime design space: **no ambient authority by default.**
A Deno program that tries to read a file, open a network connection, or
access environment variables will be denied — unless the user explicitly
grants that permission at launch time.

```
deno run --allow-net --allow-read=/tmp app.ts
```

Deno's permission flags are:
- `--allow-read[=<path>]` — filesystem read access, optionally scoped.
- `--allow-write[=<path>]` — filesystem write access, optionally scoped.
- `--allow-net[=<host:port>]` — network access, optionally scoped.
- `--allow-env[=<var>]` — environment variable access, optionally scoped.
- `--allow-run[=<command>]` — subprocess execution, optionally scoped.
- `--allow-ffi[=<path>]` — foreign function interface (dynamic library
  loading).
- `--allow-all` / `-A` — all permissions (opt-out of sandbox).

The design is pragmatic. A program can request permissions at runtime
via `Deno.permissions.request()`, allowing for progressive permission
escalation. The permission state is inspectable via
`Deno.permissions.query()`.

Deno's model has two important limitations:

1. **Permissions are strings, not capabilities.** `--allow-net` is a
   coarse permission. You cannot say "this module can access the database
   but not the internet" — the permission applies to the entire process.
   This is a limitation of the Unix process model, not Deno's design.
   Fine-grained capability separation requires separate processes or
   V8 isolates (which Deno's `Deno.createWorker` supports).

2. **Permissions are at the process boundary, not the module boundary.**
   If your program imports a library, that library inherits the
   permissions of the main program. There is no way to say "this library
   can read files but this other library cannot." This is the
   **confused deputy problem**: a library you trust with one operation
   can perform other operations using your authority.

### 5.3 WebAssembly's Sandbox Model

WebAssembly takes a different approach: the sandbox is **the only
execution model.** A Wasm module has no access to the host system at all.
It can only:
- Perform computation on its own linear memory.
- Call functions explicitly provided by the host (imports).
- Return results to the host (exports).

Wasm's sandbox properties are:
- **Memory isolation:** each module has its own linear memory. One module
  cannot read another module's memory.
- **Control-flow integrity:** the Wasm call stack is separate from the
  host call stack. A Wasm function cannot jump to arbitrary host code.
- **No ambient authority:** a Wasm module cannot perform any IO unless
  the host provides functions for it.

WASI (WebAssembly System Interface) extends Wasm with a capability-based
system interface. A WASI module receives file descriptors (capabilities)
from the host and can only operate on those. It cannot open files by path
name — it must receive a pre-opened directory descriptor.

The Wasm/WASI model is the closest existing system to pure ocap
principles in a mainstream runtime. The key design decision: **the
sandbox is not a feature you opt into; it is the only mode of execution.**
You cannot write a Wasm program that reads `/etc/passwd` — the concept
does not exist in the Wasm abstract machine.

### 5.4 Java SecurityManager (Deprecated)

Java's SecurityManager was an attempt at in-process sandboxing. Any code
calling a sensitive operation (file IO, network, class loading) triggered
a `checkPermission` call. A security policy file determined which code
sources had which permissions. The full machinery:

- `java.lang.SecurityManager` — the gatekeeper.
- `java.security.AccessController.doPrivileged()` — a block of code that
  asserts its authority, circumventing the caller's permission checks.
- `.java.policy` files — grant statements mapping code sources to
  permissions.

Java's SecurityManager was deprecated for removal in Java 17 (JEP 411).
Why it failed:

- **Complexity:** writing correct security policies was extremely
  difficult. The interaction between `doPrivileged` blocks, thread
  context, and stack inspection created unpredictable behavior.
- **Performance:** checking permissions on every file open, socket
  connect, and class load added measurable overhead.
- **Inadequate granularity:** permissions were broad (SocketPermission,
  FilePermission) and hard to compose.
- **False sense of security:** developers assumed the SecurityManager
  protected them, but the attack surface (serialization, JNI, reflection,
  unsafe) was far larger than the SecurityManager ever covered.
- **Developer friction:** libraries did not work under a SecurityManager
  unless specifically tested. Running the JDK itself with a
  SecurityManager was unsupported.

The lesson: **in-process sandboxing with broad permission checks is
brittle.** The sandbox boundary should be at the process/isolate level
(Deno, Wasm) or at the OS level (seccomp, Capsicum), not in-library
within a single process.

### 5.5 OS-Level Sandboxing

**seccomp** (Linux) allows a process to restrict its future system calls
to a safe subset. Once seccomp mode is enabled, any disallowed system
call kills the process. Chrome uses seccomp to sandbox renderer processes:
a renderer can `read`, `write`, `mmap` (within limits), and a few others,
but cannot `open`, `socket`, or `exec`.

**pledge** (OpenBSD) works at a higher level: a program declares what
"promises" it needs (stdio, rpath, wpath, cpath, dns, inet, etc.), and
the kernel enforces that. After the initial setup, the program can drop
privileges by calling `pledge` with a reduced set. Unlike seccomp,
`pledge` is ergonomic — it operates on semantic categories rather than
individual syscall numbers.

**AppArmor** (Linux) uses path-based profiles to restrict file access.
A profile lists which paths a program can read, write, and execute.
AppArmor is more flexible than seccomp (path-level granularity) but more
complex to configure.

The pattern across all OS-level sandboxing: **the sandbox is a one-way
door.** A process starts with broader permissions, then drops them. It
cannot regain permissions without exec'ing a new process or receiving an
explicit capability from a trusted source.

### 5.6 Key Structural Insight for Nomi

Nomi's immediate sandbox model should follow two principles:

1. **Capability scopes (future) are more important than runtime
   sandboxing (now).** The language-level capability model — explicit
   IO handles, no global filesystem, no ambient network — provides
   security at design time. Runtime sandboxing (seccomp, pledge) is an
   operational concern best handled by the host platform, not the
   language runtime.

2. **The sandbox boundary should be at the module level, not the process
   level.** Deno's limitation (permissions apply to the entire process)
   is a genuine design constraint. Nomi should design its module system
   so that a module can be imported with attenuated capabilities — e.g.,
   `import "user_service.nomi" with { db: read_only_db_cap }`. This is
   the powerbox pattern applied to module imports.

---

## 6. Memory Safety and Type Safety

### 6.1 Core Security Philosophy

Memory safety is the property that a program cannot access memory it
should not: no buffer overflows, no use-after-free, no double-free, no
null-pointer dereferences (in safe code). Type safety is the property
that a value of type T cannot be treated as a value of type U (unless
the language explicitly allows it through a checked conversion).

These are not theoretical concerns. Microsoft's Security Response Center
(MSRC) has repeatedly stated that **approximately 70% of all CVEs in
Microsoft products are memory safety issues.** Google's Project Zero
found a similar ratio in Chrome and Android. The majority of remote code
execution vulnerabilities in the history of computing trace back to
memory unsafety.

### 6.2 Rust's Ownership System as a Security Property

Rust's ownership system is the most significant language-level advance in
memory safety in decades. The core rules:

- **Each value has exactly one owner** (a binding or a container).
- **References must not outlive their referent** (the borrow checker
  enforces this statically).
- **At any given time, you can have either one mutable reference or any
  number of immutable references, but not both** (preventing data races).

These rules eliminate use-after-free, double-free, buffer overflows, null
pointer dereferences, and data races — in safe Rust. The `unsafe` keyword
creates an explicit boundary: code inside an `unsafe` block can perform
operations that Rust cannot verify, but the expectation is that the safe
API wrapping that `unsafe` code preserves the safety invariants.

The key insight is that **Rust made memory safety a compile-time property
without garbage collection.** C and C++ have no memory safety. Java, Go,
and C# have memory safety via garbage collection, which prevents
use-after-free and double-free but not data races (Go: "don't communicate
by sharing memory; share memory by communicating"). Rust provides the
safety of GC languages with the runtime performance of C.

### 6.3 The Microsoft 70% Finding and Its Implications

Microsoft's finding that 70% of CVEs are memory safety bugs is not an
observation about Microsoft's code quality. It is a structural fact about
memory-unsafe languages. When Microsoft rewrote parts of Windows in Rust
(DWriteCore, Win32k GDI region code, some Azure components), the
memory-safety CVEs in those components dropped to zero.

Google's Android team reports a similar finding: memory safety
vulnerabilities in new Rust code are close to zero. The Android team's
conclusion:

> "As the amount of new memory-unsafe code entering Android has decreased,
> the number of memory safety vulnerabilities has also decreased. The
> correlation is strong: from 2019 to 2022, memory safety vulnerabilities
> dropped from 76% of Android's total vulnerabilities to 35%."

The transition to Rust reduced Android's memory safety vulnerabilities
while also reducing overall vulnerability density (because new code was
increasingly written in Rust rather than C/C++).

### 6.4 Type Confusion, Use-After-Free, and Buffer Overflows

These are the three categories that dominate CVE databases:

**Buffer overflows** occur when a program writes beyond the allocated
bounds of a buffer. In C, `strcpy(dst, src)` has no bounds check. In
Rust, `dst.copy_from_slice(src)` will panic (or be a compile error) if
`src` is larger than `dst`. Buffer overflows are impossible in safe Rust,
impossible in Java/C#/Go/Python (array bounds are checked at runtime),
and possible in C/C++.

**Use-after-free** occurs when a program uses a pointer after the memory
it points to has been freed. In Rust, the borrow checker prevents this
statically. In GC languages, the GC ensures that memory is not freed
while it is reachable — use-after-free is impossible (though logical
use-after-release — using a closed database handle — is still possible).

**Type confusion** occurs when a program treats a value of one type as
another type. In C, casting `void*` to `struct Foo*` with no runtime
check is routine. In C++, `reinterpret_cast` is the explicit "I know
what I'm doing" version. In Java, generics are erased at runtime —
`ArrayList<String>` and `ArrayList<Integer>` are the same runtime type,
which creates type confusion vulnerabilities at the JVM boundary. In
Rust, `unsafe` transmutes can cause type confusion, but safe Rust
prevents it statically.

### 6.5 What Language-Level Guarantees Matter?

Not every language can or should be Rust. The key question: what is the
minimum memory-safety baseline for a new language in 2026?

**Non-negotiable:**
- Array bounds checking (panic or Result, not silent corruption).
- No uninitialized memory access (zero-initialize or compile error).
- No double-free (GC or ownership tracking).
- Integer overflow detection (panic or saturating, not silent wraparound
  in debug mode).

**Pragmatic but important:**
- Data race freedom. Even GC languages should provide some mechanism
  (Go's race detector, Java's `synchronized`, or a borrow checker).
- Null safety via the type system (Option/Optional/Maybe types).
- Exhaustive pattern matching on discriminated unions (prevents "I forgot
  to handle that case" logic errors).

**Deferred until proven necessary:**
- Full borrow checking (Rust-level). In a language with a GC or with a
  simpler memory model, borrow checking may not be necessary. But the
  language should not preclude adding it later for unboxed types.

### 6.6 Key Structural Insight for Nomi

Nomi is a higher-level language than Rust and should not attempt to
compete on zero-cost memory safety. But it should adopt five structural
guarantees:

1. **No undefined behavior in the safe language.** Array out-of-bounds
   panics with a diagnostic. Integer overflow is detected. Null is
   replaced by `Option[T]`/`None` at the type level.

2. **Data race freedom for `data` values.** Nomi's `data` types should
   be immutably shareable between concurrent contexts (threads, async
   tasks, block-call bodies). Mutation requires explicit opt-in
   (`mut`-like annotation on fields or container types).

3. **Type safety at the boundary.** `Data.decode` returns `Result[T, E]`,
   never `any`/`dynamic`. The type checker should enforce that all
   decoded values are validated before use.

4. **No `unsafe` escape hatch (initially).** Rust's `unsafe` is necessary
   for systems programming. Nomi is not a systems language. There should
   be no way to subvert the type system. FFI (when added) should be a
   capability-bound operation, not an `unsafe` block that can appear
   anywhere.

5. **Integer types with explicit semantics.** Nomi's integer types should
   specify overflow behavior (panic, saturating, or wrapping) rather than
   leaving it undefined or platform-dependent.

---

## 7. Information Flow Control

### 7.1 Core Security Philosophy

Information flow control (IFC) is the idea that the language or runtime
should track how information moves through a program and enforce a
security policy. The classic formulation is **noninterference**: high-
sensitivity data should not influence low-sensitivity outputs. If a
program reads a secret value, no observable low-sensitivity output should
depend on that secret value.

This is a stronger property than access control. Access control says "this
user can or cannot read this file." IFC says "if this user reads a secret
file, the output they produce must not contain any information derived
from that secret." It prevents the user from exfiltrating data, not just
from reading it.

### 7.2 JIF, LIO, and the IFC Research Line

**JIF** (Java + Information Flow, Andrew Myers et al., Cornell) extends
Java with security types. Variables are labeled with a security level
(e.g., `{Alice: Bob}` meaning Alice can read but Bob cannot). The type
checker ensures that information does not flow from high-security
variables to low-security outputs. If the checker cannot prove
noninterference, it rejects the program.

JIF demonstrated that IFC is practical for a realistic programming
language — but it required programmers to annotate every variable with a
security label. The annotation burden was the primary barrier to adoption.

**LIO** (Haskell, Stefan Heule et al., Stanford) embeds IFC as a
library using Haskell's type system. A computation runs in the `LIO`
monad, which tracks a current label and a current clearance. The label
represents the sensitivity of data the computation has seen; the
clearance represents the maximum sensitivity the computation is allowed
to see. Reading sensitive data raises the label; writing to a channel
checks that the label is below the channel's sensitivity.

LIO showed that IFC could be embedded in an existing language as a
library — but it required programmers to write in monadic style, which is
a heavy adoption cost for non-Haskell programmers.

**URFlow** (David Darais et al.) applied IFC to JavaScript using a
combination of static analysis and runtime checks. It was practical for
securing browser extensions but never achieved mainstream adoption.

### 7.3 Taint Tracking vs. Full IFC

Taint tracking is a simpler version of IFC: data from untrusted sources
(forms, network input, file reads) is marked as "tainted." The runtime or
static analyzer ensures that tainted data does not flow into sensitive
sinks (SQL queries, shell commands, HTML output) without explicit
sanitization.

**Perl's taint pragma** (`#!/usr/bin/perl -T`) is the original taint
tracking implementation. In taint mode, any data from outside the program
(environment variables, file reads, command-line arguments) is tainted.
Using tainted data in a "dangerous" operation (file open, system call,
eval) is a runtime error. The only way to untaint data is to extract it
with a regex capture group — which forces the programmer to explicitly
validate the data format.

**Pysa** (Python Static Analyzer, Meta/Facebook) applies taint analysis
to Python. Sources (places where data enters the program) and sinks
(places where data could cause harm) are annotated, and Pysa tracks
potential taint flows. Pysa is practical (it runs on Meta's Python
codebase) but limited (it is a static analysis tool, not a language
feature; it has false positives and false negatives).

**Ruby's `Safe` levels** (`$SAFE`) were an attempt at taint tracking but
were deprecated in Ruby 2.7 and removed in 3.0. The mechanism was
complex, interacted badly with metaprogramming, and was circumvented by
Ruby's dynamic nature.

### 7.4 Why Hasn't IFC Achieved Mainstream Adoption?

Five structural reasons:

1. **Annotation burden.** Full IFC requires security annotations on
   variables, function parameters, and return types. This is a
   significant annotation cost that most programmers are unwilling to pay
   without a clear, immediate benefit.

2. **The "label creep" problem.** In a program that processes both
   sensitive and non-sensitive data, the label of any value that touches
   sensitive data rises. Over time, most values in the program become
   high-sensitivity, and the IFC system prevents them from being used in
   low-sensitivity contexts — even when the usage is safe.

3. **Declassification.** Real programs need to release information
   derived from sensitive data — a hash of a password, a count of
   sensitive records, a "password strength" meter that reads the
   password. IFC systems need a declassification mechanism, and designing
   a safe declassification primitive is an open research problem.

4. **Implicit flows.** Information can leak through control flow: `if
   secret then x = 1 else x = 0` — x now contains 1 bit of the secret.
   Tracking implicit flows requires the IFC system to understand program
   structure deeply, which complicates the analysis and increases false
   positives.

5. **Performance.** Runtime IFC (tracking labels dynamically) adds
   overhead to every operation. Static IFC (type-checking labels) adds
   complexity to the type system. Neither is free.

### 7.5 What Fragments of IFC Are Practical?

Rather than full IFC, several narrower approaches have proven practical:

**Taint mode for specific domains.** SQL injection prevention does not
need full IFC. It needs "this string came from user input, so it must be
parameterized before entering a SQL query." Domain-specific taint
tracking is practical — it is what prepared statements, parameterized
queries, and template auto-escaping already do.

**Capability scopes as IFC-lite.** Instead of tracking information flow,
restrict what code can do with information it has. A function that has
access to a database but not to the network cannot leak database contents
over the network. This is capability security applied at the function
level, and it is practical without annotations.

**Secret-erasure types.** A type like `Secret[T]` that cannot be
serialized, logged, or printed is a crude form of IFC: it prevents
information from flowing from the secret value to observably low-
sensitivity channels (logs, stdout, error messages). This is practical,
cheap, and addresses the most common information-leak vector.

### 7.6 Key Structural Insight for Nomi

Nomi should not implement full information flow control. The annotation
burden and label-creep problem are too severe for a language targeting
everyday programming. Instead, Nomi should implement three practical
fragments:

1. **`Secret[T]` as a redaction boundary.** Values of type `Secret[T]`
   cannot be printed, logged, or serialized without explicit unwrap. This
   is enforced by the type system (the formatter does not accept
   `Secret[T]`) and by the `explain` system (which redacts secrets in
   diagnostic output).

2. **Capability scopes as coarse IFC.** A block of code that has access
   to `db: Database` but not `net: Network` cannot leak data from the
   database to the network. This is not true IFC (it does not prevent
   the block from encoding database data into a return value that the
   caller then sends over the network), but it prevents the most direct
   exfiltration path.

3. **Taint checking for specific boundaries.** Nomi's `Data.decode`
   boundary is a natural place for taint. A value decoded from external
   data should carry a provenance marker (`Tainted[User]` or
   `Validated[User]`) that is consumed by sinks like SQL query builders
   and shell command constructors. The type system ensures that
   unvalidated external data does not flow into sensitive sinks.

---

## 8. Cryptographic Hygiene

### 8.1 Core Security Philosophy

Cryptographic hygiene is the principle that a standard library should
make correct cryptographic usage the path of least resistance. The
canonical statement is from Daniel J. Bernstein (djb), the creator of
NaCl:

> "The number one rule of crypto is: don't write your own crypto. Use
> existing constructions built by people who understand the problem."

But the deeper problem is: even when programmers use a crypto library,
they use it wrong. They choose the wrong algorithm, generate nonces
incorrectly, compare hashes with `==` (revealing timing information),
or store keys in plaintext. Cryptographic hygiene is about designing an
API where the obvious thing to do is the secure thing.

### 8.2 NaCl / libsodium: The "No Footguns" Design

NaCl (Networking and Cryptography library, pronounced "salt") was
designed by djb, Tanja Lange, and Peter Schwabe to be the library where
"the obvious way to do something is the correct way."

Key design decisions that made libsodium successful:

**Curve25519 by default.** NaCl chose Curve25519 (Bernstein's curve) for
elliptic-curve Diffie-Hellman key exchange. At the time, the dominant
choice was NIST P-256, which has implementation complexity and
theoretical concerns about curve parameters. Curve25519 was designed to
be "the Montgomery curve with the fastest constant-time implementation"
— correctness and performance in one decision.

**Combined constructions, not composable primitives.** A traditional
crypto library exposes AES, SHA-256, HMAC, RSA, and ECDSA as separate
primitives. The programmer is expected to combine them correctly:
encrypt-then-MAC, generate a random IV, use a proper nonce, verify before
decrypting. NaCl exposes `crypto_box` (public-key authenticated
encryption), `crypto_secretbox` (secret-key authenticated encryption),
and `crypto_sign` (digital signatures). Each does one thing, correctly,
with no choices for the programmer.

**No error-prone parameters.** `crypto_box` takes a message, a nonce, the
recipient's public key, and the sender's secret key. There are no
algorithm parameters, no mode selection, no padding options. The
implementation chooses the right algorithm, generates the right key
material, and handles nonce generation and management.

**Constant-time by default.** Libsodium's comparison functions
(`sodium_memcmp`, `crypto_verify_16`, `crypto_verify_32`) are guaranteed
constant-time. The library prevents timing side-channel attacks at the
implementation level rather than expecting the programmer to know about
them.

The result: libsodium is the gold standard for crypto library design.
It has had no critical security vulnerabilities in its core constructions
since its initial release.

### 8.3 Google Tink: High-Level Crypto for Application Developers

Google Tink takes the NaCl philosophy further. It provides a multi-
language (Java, C++, Go, Python, JavaScript) crypto library organized
around "primitives" and "key management":

**Primitives** are high-level operations: `Aead` (Authenticated
Encryption with Associated Data), `Mac`, `DeterministicAead`,
`StreamingAead`, `HybridEncrypt`/`HybridDecrypt`, `PublicKeySign`/
`PublicKeyVerify`.

**Keysets** are collections of keys with metadata (key ID, algorithm,
status — enabled, disabled, or destroyed). Tink separates key management
from cryptographic operations. A `KeysetHandle` holds a reference to a
keyset; cryptographic operations use the handle, not raw key bytes.

**Key rotation** is built in. A keyset can have multiple keys; the
primary key is used for new operations, while old keys remain available
for decryption/verification. Rotation is as simple as adding a new key
and promoting it to primary.

Tink's design principles are worth understanding for any new language's
crypto API:

1. **AEAD by default.** Tink's `Aead` interface is the primary
   encryption API. You cannot accidentally use unauthenticated encryption
   (like AES-CBC without a MAC). The API simply does not expose it.

2. **Safe key generation.** Keys are generated with `KeysetHandle`,
   which handles randomness, serialization, and storage. You never hold
   raw key bytes unless you explicitly choose to.

3. **No legacy algorithms.** Tink supports AES-GCM, AES-EAX,
   ChaCha20-Poly1305, and XChaCha20-Poly1305. It does not support RC4,
   DES, MD5, SHA-1, or ECB mode — algorithms known to be broken or weak.
   There is no API to access them.

4. **Cross-language compatibility.** A key generated in Java can be
   used in Go, Python, or C++. The key format is standardized.

### 8.4 What Crypto Primitives Should a Standard Library Provide?

A language standard library faces a different constraint from a
dedicated crypto library. The stdlib must be stable for the language's
lifetime, which means it cannot include algorithms that might be broken
ten years from now. The minimum set:

**Must provide:**
- Secure random number generation (`crypto.random_bytes(n)`).
- Constant-time comparison (`crypto.compare(a, b)`).
- SHA-256 and SHA-512 (hash functions for fingerprints, not password
  hashing).
- HMAC-SHA256 (message authentication).
- AEAD encryption (AES-256-GCM or ChaCha20-Poly1305).
- Key derivation (HKDF).

**Should provide (or standardize a blessed third-party library):**
- Password hashing (Argon2id).
- Public-key authenticated encryption (X25519 + ChaCha20-Poly1305, like
  NaCl's `crypto_box`).
- Ed25519 digital signatures.
- TLS client (for secure communication — not rolling TLS from primitives).

**Should NOT provide:**
- Raw block ciphers (AES-ECB, AES-CBC without MAC). These are footguns.
- RSA encryption (superseded by ECC; legacy only).
- Any algorithm that has been broken or deprecated (DES, RC4, MD5, SHA-1).
- "Flexible" APIs that let programmers choose modes, padding, and IV
  generation. The correct mode is the only mode.

### 8.5 Key Structural Insight for Nomi

Nomi's crypto posture should follow the NaCl/Tink philosophy: **provide
secure constructions, not composable primitives.** The API surface:

```
crypto.random(n: int) -> bytes
crypto.hash(data: bytes) -> Hash
crypto.compare(a: bytes, b: bytes) -> bool  # constant-time
crypto.secret_box.encrypt(msg: bytes, key: Secret[Key]) -> bytes
crypto.secret_box.decrypt(ciphertext: bytes, key: Secret[Key]) -> Result[bytes, CryptoError]
crypto.hkdf.derive(secret: Secret[bytes], salt: bytes, info: str, length: int) -> Secret[bytes]
crypto.password.hash(password: str) -> Hash  # Argon2id
crypto.password.verify(password: str, hash: Hash) -> bool
```

Key integrity property: **all keys are `Secret[T]`.** The type system
prevents a key from being accidentally logged, printed, or serialized.
This is not just crypto hygiene; it is the `Secret[T]` type's primary
use case.

No `crypto.aes_encrypt(mode="CBC", key=..., iv=...)` API. No choices
that the programmer can get wrong. If a mode becomes broken in the
future, the library changes the underlying implementation behind the
same high-level API.

---

## 9. Authentication and Identity

### 9.1 Core Security Philosophy

Authentication is the hardest problem in web application security to get
right. The stakes are high (account takeover, data breach) and the
surface area is large (password storage, session management, token
validation, OAuth flows, multi-factor auth). The philosophy that has
emerged over the last decade: **do not build authentication yourself.**
The complexity and risk are too high for a single development team.

The landscape has bifurcated:

- **Identity providers** (Auth0, Clerk, Firebase Auth, Supabase Auth,
  WorkOS) handle authentication as a service. You integrate their SDK
  and they handle sign-up, sign-in, MFA, password reset, social login,
  and session management. The cost is vendor dependence and ongoing
  subscription fees.

- **Self-hosted auth** (Keycloak, Ory, Authentik, Zitadel) are open-
  source identity servers you run yourself. They provide the same
  features as identity providers but require operational expertise to
  host and maintain.

### 9.2 OAuth2, OIDC, JWT, and WebAuthn

These are the four protocols and formats that dominate modern
authentication:

**OAuth2** (RFC 6749) is an authorization framework, not an
authentication protocol. It defines how a user can grant a third-party
application access to their resources without sharing their credentials.
The Authorization Code Grant (with PKCE) is the only flow that should
be used for new applications. The Implicit Grant is deprecated. The
Resource Owner Password Credentials grant should never have existed.

**OpenID Connect (OIDC)** is an authentication layer on top of OAuth2.
It adds an ID token (a JWT) that contains claims about the authenticated
user (subject, email, name, picture). OIDC is what most people mean when
they say "OAuth login" (Sign in with Google, Sign in with GitHub).

**JWT** (JSON Web Token, RFC 7519) is a format for signed claims.
Critically, JWT is a format, not a protocol. The security of a JWT-based
system depends on correct validation: check the signature, check the
issuer, check the audience, check the expiration, check the not-before
time, and never accept `alg: "none"` (the "none algorithm" attack).
JWT libraries have had a long history of vulnerabilities because they
default to lenient validation.

**WebAuthn** (W3C Web Authentication API) is the standard for passwordless
authentication using hardware authenticators (security keys, platform
authenticators like Touch ID and Windows Hello). WebAuthn uses public-key
cryptography: the authenticator generates a key pair for each relying
party, and the private key never leaves the authenticator. This prevents
phishing (the credential is bound to the origin) and credential stuffing
(there are no passwords to reuse).

### 9.3 Clerk / Auth0 vs. Rolling Your Own

The Clerk and Auth0 model: you include a script tag or SDK call, and
authentication is handled. The <SignIn /> component is pre-built, the
session management is pre-built, the MFA flows are pre-built, and the
social login providers are pre-configured. The tradeoffs:

**Advantages:**
- Security updates are the provider's responsibility.
- The attack surface is outsourced to a team whose full-time job is auth
  security.
- Compliance (SOC2, GDPR, CCPA) is partially offloaded.

**Disadvantages:**
- Vendor lock-in: migrating from Clerk to Auth0 means re-implementing
  user provisioning.
- Latency: every auth check is an API call to the provider.
- Customization limits: the provider's UI and flow may not match your
  application's needs.
- Cost at scale: per-monthly-active-user pricing becomes expensive for
  high-volume applications.

The middle ground is **self-hosted identity** (Keycloak, Ory, Zitadel).
These give you control over your user data and avoid per-user pricing,
at the cost of operational complexity and maintenance burden.

### 9.4 Session Management Patterns

Regardless of whether you use an identity provider or self-host, session
management follows two dominant patterns:

**Server-side sessions (traditional web apps).** The server creates a
session, stores it in a database or cache, and sends the session ID as
a cookie (`HttpOnly`, `Secure`, `SameSite=Lax`). The server looks up the
session on each request. This is secure (the cookie is opaque, the
server controls session lifetime) but requires server-side state.

**Token-based sessions (SPAs, mobile apps, APIs).** The client receives
an access token (JWT or opaque token) after authentication and sends it
in the `Authorization: Bearer <token>` header. The server validates the
token on each request. JWTs are self-contained (the server does not need
to look up session state), which improves scalability at the cost of
revocation complexity (you cannot invalidate a JWT before it expires
without a token blacklist).

The critical security properties for session management:

- **HttpOnly cookies for web apps** — prevent JavaScript from reading the
  session token (XSS protection).
- **Secure cookies** — prevent transmission over unencrypted HTTP.
- **SameSite cookies** — prevent CSRF by restricting when cookies are
  sent cross-site.
- **Token binding or DPoP** — bind tokens to a specific client to
  prevent token replay.

### 9.5 How Should a Language or Framework Guide Developers?

A language standard library cannot and should not try to implement
OAuth2. But a language's web framework should make secure auth the
default, not an opt-in configuration. The framework should:

1. **Provide a `Session` abstraction** that uses HttpOnly, Secure,
   SameSite cookies by default. The default should be secure.

2. **Provide a `User` / `Identity` type** that represents an
   authenticated principal. Functions that require authentication should
   accept this type, not a raw token string.

3. **Make CSRF protection automatic.** The framework should generate and
   validate CSRF tokens for all state-changing requests. Opt-out, not
   opt-in.

4. **Provide password hashing as a standard library primitive**
   (Argon2id), with a simple two-function API: `hash_password` and
   `verify_password`.

5. **Never provide an "encrypt password" function.** Passwords are
   hashed, not encrypted. The only operation on a stored password is
   verification. An "encrypt password" API implies reversibility, which
   is a design error.

### 9.6 Key Structural Insight for Nomi

Nomi's web framework (when built) should adopt the Clerk/Auth0 model in
spirit: provide a pre-built, secure auth path that works out of the box,
with escape hatches for customization. The language standard library
should provide the cryptographic primitives (Argon2id, secure random,
constant-time comparison). The `Secret[T]` type should carry session
tokens and API keys. The `explain` system should never expose
authentication-related values.

---

## 10. Redaction and Data Safety

### 10.1 Core Security Philosophy

Redaction is the practice of preventing sensitive data from appearing in
logs, error messages, debug output, and diagnostic traces. The philosophy
is: **sensitive values should be visible-but-safe.** They should be
visible enough that the programmer knows they exist (a log line that says
`authenticating with API key ***` is useful; a log line that silently
swallows the fact that an API key exists is not), but not so visible that
they can be exfiltrated through log aggregation, error reporting, or
debugging tools.

### 10.2 Python's `__repr__` and the PII Problem

Python's `__repr__` is the single biggest source of inadvertent PII
disclosure in Python applications. The default `__repr__` (for objects
without a custom `__repr__`) outputs the object's memory address. But
when developers add a custom `__repr__`, they often include all fields:

```python
class User:
    def __repr__(self):
        return f"User(name={self.name}, email={self.email}, ssn={self.ssn})"
```

This `__repr__` ends up in log messages, Sentry error reports, and debug
traces. The SSN is now in the log aggregation system, the error tracker,
and possibly the developer's terminal scrollback. The GDPR implications:
a user's personal data has been processed and stored in systems that were
never designed because the developer did not think of `__repr__` as a
data-processing operation.

The structural problem is that `__repr__` is a single method with
conflicting requirements:
- It should be useful for debugging (show all the information).
- It should be safe for logging (show no sensitive information).
- It should be unambiguous (a User object should look like a User
  object).

Python's solution: there is no solution. Each application reinvents
redaction in its logging configuration, with variable quality.

### 10.3 Structured Logging with Redaction

Structured logging (logging key-value pairs rather than formatted
strings) enables systematic redaction. In a structured log:

```json
{"event": "user_login", "user_id": 42, "api_key": "***REDACTED***"}
```

The redaction can happen at the logging framework level, independently
of the application code. The framework knows that fields named `api_key`,
`password`, `token`, `secret`, and `credential` should be redacted.

The problem is that this relies on convention (field naming) rather than
type information. If a developer names their field `key` instead of
`api_key`, the redaction fails. If a developer puts a password in the
`username` field (bizarre but possible), the redaction fails.

### 10.4 GDPR and Data Privacy Implications

The General Data Protection Regulation (GDPR) and similar regulations
(CCPA, LGPD, PIPEDA) create legal obligations around personal data.
Critically for language design:

- **Data minimization:** Collect only the data you need. A language that
  makes it easy to add fields to a type also makes it easy to collect
  unnecessary PII.
- **Purpose limitation:** Use data only for the purpose for which it was
  collected. Debug logging that captures a user's email address for the
  purpose of "seeing what happened" is processing personal data outside
  the stated purpose.
- **Right to erasure:** Users can request that their data be deleted.
  If personal data is scattered across log files, error reports, and
  debug traces, erasure is practically impossible.

The structural implication: a language should make it **easy to keep
PII out of diagnostic systems** and **hard to accidentally include it.**

### 10.5 How Should a Language Make Sensitive Data Visible-but-Safe?

The key design pattern: **the type system distinguishes sensitive values
from non-sensitive values, and the display/format/log systems respect
that distinction.**

**`Secret[T]` as a type constructor.** A value of type `Secret[str]` is
a string that cannot be printed, logged, or serialized by default. The
only way to extract the value is through an explicit `reveal()` call,
which should be auditable.

**`PII[T]` as a type constructor (or annotation).** A value of type
`PII[str]` carries a note that it contains personal data. The display
system shows the type and a tag (`PII("email@example.com" as [email])`)
but the logging system can be configured to redact PII values.

**Redacted `__format__` / `explain`.** Nomi's `explain` system is the
natural place for redaction. When `explain` encounters a `Secret[T]` or
`PII[T]` value, it shows the type and metadata, not the raw value. The
programmer can request raw display with `explain --unsafe` (a deliberate
escalation).

**Field-level annotations.** Nomi's `data` declarations already support
annotations (`@strict`, `@lax`, `@default`). Add `@secret` and `@pii`:

```
data DatabaseConfig:
    host: str
    port: int
    @secret password: str
    @pii connection_user: str
```

With these annotations, `DatabaseConfig`'s display shows `password:
Secret("***")` automatically. No custom `__repr__` needed.

### 10.6 Key Structural Insight for Nomi

Nomi's existing `data` boundary concept is the right foundation for
redaction. The missing piece is the `@secret` and `@pii` annotations that
tell the display and diagnostic systems to handle these fields safely.
The `Secret[T]` wrapper type enforces redaction at the type level: you
cannot accidentally print a secret because the print function does not
accept `Secret[T]`.

The `explain` normal form is the right place for sensitive-value
handling. `explain config` shows the structure of a config object but
redacts secret values. `explain --unsafe config` shows everything. This
is an intentional escalation that can be audited.

---

## Cross-Language Synthesis

### 11.1 Structural Invariants — What All Trustworthy Systems Share

These seven patterns appear in every system that has achieved a
meaningful level of security and trust, regardless of architecture:

**1. Content addressing is the foundation of integrity.** Nix, Git, Go's
sum database, Docker image digests, Sigstore/Rekor — they all use
cryptographic hashes as the identity of artifacts. When you check the
hash, you do not need to trust the distribution channel. Any system that
relies on names without hashes (npm package names, PyPI project names,
Docker `:latest` tags) eventually has an integrity incident.

**2. The sandbox is a one-way door.** seccomp, pledge, Capsicum, Deno
permissions, Nix build sandbox — they all start with broader permissions
and drop them irreversibly. A program cannot regain permissions it has
given up. This is a monotonicity property that makes reasoning about
security tractable.

**3. Explicit is more secure than implicit.** Nix's explicit dependency
declaration makes undeclared inputs a build failure. Deno's explicit
permissions make ambient authority impossible. Capability systems'
explicit capability passing makes it impossible to accidentally access
a resource. Every security system converges on making authority explicit
and visible.

**4. Transparency logs convert targeted attacks into public attacks.**
Go's sum database, Rekor, Certificate Transparency — the pattern is:
publish a Merkle tree of all operations. An attacker can no longer serve
malicious content to a specific victim without also publishing it to a
globally visible log. The log makes targeted attacks detectable.

**5. Defaults determine security posture.** NaCl's default of AEAD
encryption means you cannot accidentally use unauthenticated encryption.
Nix's default of sandboxed builds means you cannot accidentally depend
on undeclared inputs. A language that makes secure defaults the path of
least resistance will have fewer security incidents than one that
requires explicit opt-in to security.

**6. Separation of identity and authority.** OIDC separates identity
(who you are) from authorization (what you can do). Capability systems
separate the ability to name a resource from the ability to access it.
Go's import paths separate naming (the domain) from content (the hash).
When identity and authority are conflated, confused-deputy attacks and
privilege-escalation vulnerabilities follow.

**7. Immutability after publication.** npm's left-pad incident showed
that mutable package registries break supply-chain trust. Go's sum
database is append-only. Nix derivations, once built, cannot be changed.
Immutability is not just a convenience property; it is a security
property.

### 11.2 Genuine Design Forks — Where Systems Made Genuinely Different Tradeoffs

**1. Centralized trust (Go sum DB) vs. decentralized trust (Git signing).**
Go's model trusts a single transparency log operated by Google. Git's
model trusts individual developers' GPG keys. Go's model has a single
point of failure (if Google's sum DB is compromised, every Go user is
affected). Git's model has a diffuse trust surface (every developer's
key is a potential attack vector). Neither is obviously superior; they
optimize for different threats.

**2. Process-level sandboxing (Deno) vs. isolate-level sandboxing (Wasm).**
Deno permissions apply to the entire process. Wasm sandboxing applies
per-module. Deno's model is simpler to understand and implement. Wasm's
model is finer-grained and more secure. The tradeoff is granularity vs.
simplicity.

**3. In-language IFC (JIF) vs. library-level IFC (LIO) vs. no IFC.**
JIF required language changes. LIO used the type system of an existing
language (Haskell). Neither achieved mainstream adoption. The tradeoff:
security precision vs. adoption cost.

**4. Secret stores (Vault) vs. encrypted-at-rest (SOPS).** Vault
provides dynamic secrets, leasing, and audit logging but requires
operational infrastructure. SOPS encrypts secrets in version control
with minimal infrastructure but provides static secrets with no TTL.
The tradeoff is operational complexity vs. secret lifecycle management.

**5. Memory safety via ownership (Rust) vs. memory safety via GC (Go,
Java).** Rust provides zero-cost memory safety with a substantial
learning curve. GC languages provide memory safety with runtime overhead
and a simpler programming model. The tradeoff is performance vs.
ergonomics. For Nomi (a higher-level language), the GC path is the right
one.

**6. Capability security (Fuchsia) vs. permission security (Android).**
Fuchsia's kernel is capability-based from the ground up. Android's
permission model is ACL-based with runtime permission prompts. Fuchsia's
model is architecturally purer. Android's model is more familiar to
developers and users. The tradeoff is architectural coherence vs. user
experience.

**7. Built-in auth (Clerk/Auth0 model) vs. library auth (Passport.js,
Devise).** Identity providers handle auth as a service. Library-based
auth gives developers full control. The tradeoff is operational
simplicity vs. control and cost.

### 11.3 The "Least Authority" Design Space for Nomi

The principle of least authority (POLA) can be applied at multiple
levels of the language. For Nomi, the design space is:

**Level 1 — Values (now).** `Secret[T]` is a value-level POLA mechanism.
A `Secret[str]` cannot be printed, logged, or serialized. The authority
to access the plaintext is bound to explicit unwrap operations.

**Level 2 — Data boundaries (now).** `Data.decode` is a boundary-level
POLA mechanism. External data enters the program through a validated
boundary. After decoding, the data carries provenance
(`source="config/prod.nomi"`) and constraint evidence. Code that
operates on decoded data knows its origin and validity.

**Level 3 — Module capabilities (design-needed).** Module imports could
carry capability restrictions: `import "db.nomi" with { access:
read_only }`. The imported module receives only the capabilities the
caller grants.

**Level 4 — Process capabilities (future).** The Nomi runtime could
support capability-based process spawn: `spawn("worker.nomi",
capabilities: { net: dns_only, fs: read_only("/data") })`. Child
processes start with no ambient authority.

**Level 5 — System capabilities (OS-level, deferred).** The host OS
applies seccomp/pledge/Capsicum restrictions to the Nomi runtime. This
is an operational concern, not a language concern, but the language
should make it easy to declare what capabilities a program needs.

### 11.4 Config Secrets — How Nomi's `data`/Config Boundary Should Handle Sensitive Values

Nomi's `data` declarations already define the config boundary. The
security extension: `@secret` and `@pii` field annotations that
integrate with the display and diagnostic systems.

```
data AppConfig:
    @secret api_key: str
    @secret database_url: str  # contains embedded credentials
    @pii admin_email: str
    port: int  = 8080
    log_level: str = "info"

config = Data.decode(env("APP_CONFIG"), AppConfig.decoder)
```

The behavior:

- `print(config)` shows `AppConfig(api_key=Secret("***"),
  database_url=Secret("***"), admin_email=PII("a...@example.com"),
  port=8080, log_level="info")`.
- `config.explain()` shows field names and types but never raw values for
  `@secret` and `@pii` fields.
- `config.api_key.reveal()` returns the plaintext — this call can be
  audited, logged, and restricted.
- Configs are serialized to disk with secrets encrypted (using the host's
   key management, or with a local key for development).

The `@secret` annotation should also prevent the field from appearing in
error messages. If `Data.decode` fails on a `@secret` field, the error
message says "field 'api_key' failed constraint: required" — it does not
say "field 'api_key' with value 'sk-live-abc123' failed constraint:
min_length." The value is never included in the error.

### 11.5 Dependency Trust — What a New Language Should Do From Day One

Nomi can make supply-chain security a first-class property because it
does not have a legacy ecosystem. The day-one posture:

1. **Content-addressed imports.** Every remote import is optionally
   pinned by hash: `import "pkg" sha256:deadbeef...`. The lockfile is a
   Merkle tree. Verification is automatic.

2. **Domain-name import paths.** Import paths include a domain and a
   path within that domain. There is no global package namespace.

3. **Unused imports are a compile error.** A dependency that is imported
   but not used is caught at compile time. This reduces the attack
   surface and prevents dependency creep.

4. **No build scripts during dependency fetch.** Fetching a dependency
   should not execute any code from that dependency. In npm, `npm
   install` runs `postinstall` scripts — a downloaded package can run
   arbitrary code before you have even looked at it. In Rust, build.rs
   can run arbitrary code. In Nomi, fetching a dependency should be a
   pure operation: download, verify hash, cache. No execution.

5. **Capability-restricted dependency evaluation.** When a dependency is
   evaluated (compiled/loaded), it should receive only the capabilities
   needed for compilation: access to its own source tree, access to the
   types and signatures of its declared dependencies, and access to a
   diagnostic sink. No network, no filesystem beyond its source tree, no
   environment variables. This mirrors Nix's sandboxed build model.

### 11.6 Redaction as a Language Primitive

Redaction should not be a logging configuration concern or a framework
feature. It should be a language-level property of values. The mechanism:

**`Secret[T]` as a type.** Values wrapped in `Secret[T]` are opaque to
the display, format, and diagnostic systems. Extraction requires an
auditable boundary operation.

**`@secret` on data fields.** A field annotated `@secret` is
automatically wrapped in `Secret[T]` by the `data` constructor. The
programmer does not need to manually wrap and unwrap; the type system
handles it.

**`explain` respects `@secret`.** The `explain` normal form shows
structure without revealing secret values. `explain --unsafe` is an
explicit escalation.

**Redaction in error messages.** Error messages that include values from
`@secret` or `@pii` fields redact those values. The error says what
failed, not what the secret was.

**Redaction in log streams.** The log system (when built) should
integrate with the same annotation system. A `log.info("config loaded",
config)` call should not log secret values.

### 11.7 Capabilities vs. Permissions — String Permissions vs. Unforgeable References

The choice between capabilities (unforgeable references) and permissions
(string-based access control) is not a binary one. Both have a place in
Nomi:

**String permissions are appropriate for:**
- Runtime flags (Deno's `--allow-net`): the user at the command line
  grants permissions by name. Names are comprehensible to humans.
- Feature flags and runtime configuration: a feature name is a string.
- Static analysis exemptions: a linter suppression is a string comment.

**Capabilities are appropriate for:**
- IO handles: a function that writes to a file receives a `FileHandle`,
  not a path string and a "write permission."
- Database connections: a function that queries a database receives a
  `DatabaseConnection`, not a connection string and "read permission."
- Inter-module communication: a module that provides a service exports a
  capability object; modules that consume the service import it.

The rule of thumb: **strings for human-to-program communication;
capabilities for program-to-program communication.** When a human grants
a permission at the command line, the permission is a string. When one
part of the program grants access to another part of the program, the
grant is a capability reference.

Nomi's existing `data` and constraint system already leans toward
capabilities: `Data.decode(raw, Decoder)` receives a `Decoder` value,
not a schema name string. This pattern should extend to all IO and
resource handles.

### 11.8 Anti-Patterns — Security Mistakes That Consistently Hurt Ecosystems

**1. The "trust the registry" anti-pattern.** Ecosystems that assume the
package registry is trustworthy (no typosquatting, no malicious packages,
no account takeover) eventually have a supply-chain incident. The fix:
content-addressed imports that do not trust the registry.

**2. The "plaintext in logs" anti-pattern.** Every language and framework
that does not distinguish sensitive values from non-sensitive values in
its logging and display systems ends up with secrets in logs. The fix:
`Secret[T]` and `@secret` at the language level.

**3. The "flexible crypto API" anti-pattern.** Libraries that expose raw
crypto primitives with algorithm and mode parameters produce predictable
vulnerabilities (ECB mode, CBC without MAC, static IV, key-as-IV, nonce
reuse). The fix: high-level constructions with no parameter choices.

**4. The "dev is prod" anti-pattern.** Development tools that run without
restrictions (network, filesystem, environment) and then deploy with
different restrictions create a gap where security issues are invisible
in development. The fix: development-mode restrictions that mirror
production restrictions (Deno's permission flags work the same in dev
and prod).

**5. The "roll your own auth" anti-pattern.** Every web framework that
provides a "build anything" session primitive without a secure default
implementation creates a stream of authentication vulnerabilities. The
fix: pre-built, secure auth with escape hatches.

**6. The "debug mode reveals everything" anti-pattern.** Debug views that
dump all object state (Laravel's debug bar, Django Debug Toolbar,
Flask debug mode) are security vulnerabilities in production. The fix:
`@secret` and `@pii` annotations that debug tools respect.

**7. The "version ranges are safe" anti-pattern.** Dependency resolvers
that automatically upgrade within semver ranges (npm's caret ranges,
Cargo's default resolver) create supply-chain risk: a new version of a
transitive dependency can introduce compromised code, and the lockfile
update may be invisible to code review. The fix: Go's MVS (Minimal
Version Selection) — upgrades only happen when explicitly requested.

**8. The "global namespace for packages" anti-pattern.** Registries that
use bare names (PyPI, npm, RubyGems) create typosquatting and dependency
confusion vulnerabilities. The fix: domain-name import paths that
delegate namespace ownership to domain ownership.

---

## Nomi Adopt / Refuse / Adapt Table

| # | Idea | Source | Action | How it maps to Nomi |
|---|------|--------|--------|---------------------|
| 1 | Content-addressed imports with hash verification | Nix, Dhall, Go sum DB | **Adopt** | `import "pkg.nomi" sha256:...` for remote dependencies. Hash is optional for local imports, required for remote. Lockfile is a Merkle tree. |
| 2 | `Secret[T]` type with redacted display by default | Python `secrets`, Rust `secrecy` | **Adopt** | `Secret[T]` wraps sensitive values. `print`, `log`, `explain` show `Secret("***")`. Explicit `reveal()` to extract. |
| 3 | `@secret` and `@pii` field annotations on `data` types | Inferred from GDPR needs, structured logging | **Adopt** | `data DbConfig { host: str; @secret password: str }`. Auto-redacted in display, diagnostics, error messages. |
| 4 | High-level crypto constructions only (no raw primitives) | NaCl/libsodium, Google Tink | **Adopt** | `crypto.secret_box.encrypt(...)`, `crypto.password.hash(...)`. No AES mode/parameter selection API. |
| 5 | AEAD by default for all symmetric encryption | Tink, libsodium | **Adopt** | `crypto.secret_box` is authenticated encryption. No unauthenticated encryption API exists. |
| 6 | Constant-time comparison as the default for sensitive data | libsodium | **Adopt** | `Secret[T]` equality uses constant-time comparison. `crypto.compare(a, b)` for raw bytes. |
| 7 | Domain-name import paths (no bare-name global namespace) | Go, Deno | **Adopt** | `import "example.com/user/pkg"` rather than `import "pkg"`. Domain ownership anchors the namespace. |
| 8 | Unused imports are a compile error | Go | **Adopt** | Importing a module without using it is a compile error. This is both a hygiene and security property. |
| 9 | No build scripts / no code execution during dependency fetch | Nix (fetch vs build separation) | **Adopt** | Fetching a dependency downloads and verifies the hash only. No scripts run. No code from the dependency executes at fetch time. |
| 10 | Lockfile as Merkle tree with transitive hash verification | Go `go.sum`, Nix `flake.lock` | **Adopt** | `nomi.lock` records the hash of every dependency transitively. A single root hash verifies the entire tree. |
| 11 | Argon2id password hashing in standard library | OWASP recommendation | **Adopt** | `crypto.password.hash(password)` and `crypto.password.verify(password, hash)`. No parameter selection. |
| 12 | Secure random generation in standard library | Every credible language | **Adopt** | `crypto.random(n: int) -> bytes`. Backed by OS CSPRNG. No fallback to non-crypto RNG. |
| 13 | `PII[T]` type constructor for personal data | GDPR requirements | **Adopt** | `PII[str]` carries a provenance tag. Display system shows `PII("...@example.com")` with configurable redaction. |
| 14 | `explain` respects `@secret` and `@pii` annotations | Nomi's existing explain normal form | **Adopt** | `explain value` shows structure with redacted sensitive fields. `explain --unsafe value` is an explicit escalation. |
| 15 | Capability-restricted module evaluation (no ambient authority) | Deno, Nix sandbox, Wasm | **Adapt** | Adapt Deno's permission model to Nomi's module system. Modules receive explicit capabilities (their source tree, their declared dependency signatures, a diagnostic sink). No network or filesystem access by default during compilation. |
| 16 | Transparency log for package publication | Go sum DB, Rekor | **Adapt** | A Nomi package registry (when built) should publish to an append-only transparency log. Adapt the Go sum DB model to Nomi's content-addressed import system. |
| 17 | Dynamic secrets with TTL | HashiCorp Vault | **Adapt** | Adapt Vault's leasing model to Nomi's `Secret[T]` type: `Secret[T]` carries an optional TTL. After expiry, `reveal()` returns an error. This is a library feature, not infrastructure. |
| 18 | sealer/unsealer as a standard library pattern | E language, ocap literature | **Adapt** | Provide `Capability.sealer()` that returns `(seal, unseal)` functions. Adapt the ocap pattern to Nomi's function/closure vocabulary. Used for secure token wrapping and privilege separation. |
| 19 | Full information flow control (IFC) with security type lattice | JIF, LIO | **Refuse** | The annotation burden and label-creep problem are too severe for a language targeting everyday programming. Nomi's `Secret[T]`, capability scopes, and decode taint provide practical fragments without full IFC. |
| 20 | In-process SecurityManager / permission stack walks | Java SecurityManager (deprecated) | **Refuse** | Java's stack-walking permission model was complex, slow, and gave a false sense of security. Nomi's security boundaries are at the data boundary (decode), the type boundary (Secret[T]), and the capability boundary (module imports), not in-process permission checks. |
| 21 | Flexible crypto API with algorithm/mode selection | OpenSSL, traditional crypto libraries | **Refuse** | Do not expose AES mode selection, IV generation, nonce management, or algorithm parameters. The API provides constructions, not primitives. |
| 22 | Bare-name package registry with centralized namespace | npm, PyPI, RubyGems | **Refuse** | A global namespace with bare names creates typosquatting and dependency confusion. Nomi uses domain-name import paths. |
| 23 | `__repr__` / `toString` that dumps all fields by default | Python, Java | **Refuse** | Default display of data values must respect `@secret` and `@pii` annotations. No method that accidentally prints secrets because the programmer forgot to override it. |
| 24 | Version-range-based dependency resolution (default upgrade) | npm caret ranges, Cargo semver | **Refuse** | Nomi should adopt Go's MVS or a similar approach: dependencies only upgrade when explicitly requested. Automatic upgrades within semver ranges are a supply-chain risk. |
| 25 | Macro system with arbitrary compile-time code execution | Rust proc macros | **Refuse** (for now) | Macros should be syntactic transformations, not arbitrary code execution. If full compile-time computation is added later, it should be sandboxed (Wasm-based compile-time evaluation, like Zig's comptime). |
| 26 | Password encryption API (as opposed to hashing) | Legacy systems | **Refuse** | Passwords are hashed with Argon2id, never encrypted. There is no "encrypt password" function in the standard library. Encryption implies reversibility, which is a design error for passwords. |

---

## Sources

### Language and ecosystem documentation

- Nix manual (store, derivations, sandbox): https://nixos.org/manual/nix/stable/
- Nix flakes specification: https://nixos.wiki/wiki/Flakes
- Go modules and checksum database: https://go.dev/doc/modules/checksums
- Deno permissions documentation: https://docs.deno.com/runtime/fundamentals/security/
- WebAssembly specification (sandbox model): https://webassembly.org/
- WASI overview: https://wasi.dev/
- Rust ownership and borrowing: https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html
- Rust unsafe code guidelines: https://rust-lang.github.io/unsafe-code-guidelines/
- Java SecurityManager (JEP 411 — deprecated for removal): https://openjdk.org/jeps/411
- Python secrets module: https://docs.python.org/3/library/secrets.html
- Ruby SecureRandom: https://docs.ruby-lang.org/en/master/SecureRandom.html

### Capability security

- Mark S. Miller, "Robust Composition: Towards a Unified Approach to Access Control and Concurrency Control" (PhD dissertation, 2006): https://erights.org/talks/thesis/
- Mark S. Miller, Chip Morningstar, Bill Frantz, "Capability-based Financial Instruments" (2000)
- Kenton Varda, Sandstorm: https://sandstorm.io/
- FreeBSD Capsicum: https://man.freebsd.org/cgi/man.cgi?capsicum(4)
- Fuchsia capability model: https://fuchsia.dev/fuchsia-src/concepts/components/v2/capabilities
- David Wagner and Dean Tribble, "A Security Analysis of the Combex Capability System" (2002)
- Jonathan Rees, "A Security Kernel Based on the Lambda Calculus" (PhD dissertation, MIT, 1995)

### Supply-chain security

- SLSA framework: https://slsa.dev/
- Sigstore: https://www.sigstore.dev/
- Alex Birsan, "Dependency Confusion" (2021): https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610
- "event-stream incident" postmortem: https://blog.npmjs.org/post/180565383195/details-about-the-event-stream-incident
- left-pad incident summary: https://arstechnica.com/information-technology/2016/03/rage-quit-coder-unpublished-17-lines-of-javascript-and-broke-the-internet/
- Microsoft MSRC, "We Need a Safer Systems Programming Language" (2019): https://msrc.microsoft.com/blog/2019/07/we-need-a-safer-systems-programming-language/
- Google Project Zero vulnerability statistics: https://googleprojectzero.blogspot.com/
- Android memory safety transition: https://security.googleblog.com/2022/12/memory-safe-languages-in-android-13.html

### Cryptographic design

- NaCl / libsodium: https://doc.libsodium.org/
- Daniel J. Bernstein, Tanja Lange, Peter Schwabe, "The Security Impact of a New Cryptographic Library" (NaCl, 2011)
- Google Tink: https://developers.google.com/tink
- Thai Duong, "Tink: A Cryptographic Library in a Hundred Languages" (2018)
- OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

### Information flow control

- Andrew Myers, "JFlow: Practical Mostly-Static Information Flow Control" (1999)
- Stefan Heule et al., "LIO: A Library for Information Flow Control in Haskell" (2013)
- David Darais et al., "URFlow: A Flow-Sensitive Security-Typed Web Framework" (2017)
- Andrei Sabelfeld and Andrew Myers, "Language-Based Information-Flow Security" (2003)
- Perl taint mode: https://perldoc.perl.org/perlsec

### Authentication

- OAuth2 specification: https://datatracker.ietf.org/doc/html/rfc6749
- OAuth2 Security Best Current Practice: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics
- JWT specification: https://datatracker.ietf.org/doc/html/rfc7519
- WebAuthn specification: https://www.w3.org/TR/webauthn-3/
- Clerk documentation: https://clerk.com/docs
- Auth0 documentation: https://auth0.com/docs

### Redaction and GDPR

- GDPR full text: https://gdpr-info.eu/
- "GDPR and Logging" (various):
- Hacker News / OWASP discussions on PII in logs:
  https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

### Nomi internal references

- [../convenience/data_and_types.md](../convenience/data_and_types.md) — Nomi's data boundary vocabulary
- [../convenience/absence_and_result.md](../convenience/absence_and_result.md) — `Result[T, E]` and error handling
- [../convenience/scope_context.md](../convenience/scope_context.md) — capability scopes and implicit parameters
- [../convenience/review_and_roadmap.md](../convenience/review_and_roadmap.md) — secrets, redaction, and capability scopes on the roadmap
- [../convenience/syntax_synthesis_matrix.md](../convenience/syntax_synthesis_matrix.md) — config wants redaction
- [../language/language_design_dimensions.md](../language/language_design_dimensions.md) — axes of variation
- [../language/language_foundation.md](../language/language_foundation.md) — canonical design foundation
- [convenience/design_lessons_and_integration.md](./design_lessons_and_integration.md) — systemic cruft patterns (the second-mini-language anti-pattern applies to config/secret DSLs)
- [research/everyday_fallback_simplification_ideas.md](./everyday_fallback_simplification_ideas.md) §23 — early secret-value design sketches
- [research/data_boundary_systems_deep_dive.md](./data_boundary_systems_deep_dive.md) — data boundary architecture (decode, validation, constraints)
- [research/packaging_and_project_structure_deep_dive.md](./packaging_and_project_structure_deep_dive.md) — dependency management and project structure
