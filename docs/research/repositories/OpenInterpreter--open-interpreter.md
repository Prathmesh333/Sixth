# Open Interpreter

Repository: [OpenInterpreter/open-interpreter](https://github.com/OpenInterpreter/open-interpreter)  
Category: Execution harness  
Inspected commit: `ac1fcc8fe57aba51fcc3c79afd57a0883237fe87`  
Upstream commit timestamp: 2026-10-11T00:37:07Z  
License text inspected: Apache-2.0

## Problem and implementation

Runs a coding-oriented agent harness and exposes programmatic and interactive execution surfaces.

The current tree contains codex-rs and a Rust core, not the older Python interpreter architecture. The streaming-web-chat guide separates a browser from a server-side process bridge, correlates turn events and keeps provider configuration out of frontend JavaScript.

## Published direction

The portability document states a direction toward shared protocols, readable user data and migration paths. The README explicitly points to a community fork for the original Python project.

## Application to Sixth

Borrow the thin client/server boundary, correlated execution events and portable skill definitions. Sixth should expose a documented task stream and exportable memory.

Do not embed a general shell agent in the consumer MVP. Its current focus and permissions surface exceed the planned browser/calendar tools.

## Repository structure

Selected directories in the pinned tree:

```text
codex-rs/
codex-cli/
docs/
docs-site/
```

[Browse the pinned tree](https://github.com/OpenInterpreter/open-interpreter/tree/ac1fcc8fe57aba51fcc3c79afd57a0883237fe87). This is a selected map, not the complete repository.

## Evidence inspected

- [docs/portability.md](https://github.com/OpenInterpreter/open-interpreter/blob/ac1fcc8fe57aba51fcc3c79afd57a0883237fe87/docs/portability.md)
- [docs/streaming-web-chat.md](https://github.com/OpenInterpreter/open-interpreter/blob/ac1fcc8fe57aba51fcc3c79afd57a0883237fe87/docs/streaming-web-chat.md)
- [codex-rs/core/src/lib.rs](https://github.com/OpenInterpreter/open-interpreter/blob/ac1fcc8fe57aba51fcc3c79afd57a0883237fe87/codex-rs/core/src/lib.rs)
- [README.md](https://github.com/OpenInterpreter/open-interpreter/blob/ac1fcc8fe57aba51fcc3c79afd57a0883237fe87/README.md)
- [LICENSE](https://github.com/OpenInterpreter/open-interpreter/blob/ac1fcc8fe57aba51fcc3c79afd57a0883237fe87/LICENSE)

Review scope: repository tree, README, license text, and selected implementation/architecture sections. Large files were inspected selectively. No repository was installed, executed, benchmarked, or audited end to end. Sixth recommendations above are our design choices.
