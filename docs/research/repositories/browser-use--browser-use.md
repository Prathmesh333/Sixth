# Browser Use

Repository: [browser-use/browser-use](https://github.com/browser-use/browser-use)  
Category: Browser execution  
Inspected commit: `ccd22fef47a1a36e0c4596fef5db73a5117b9d06`  
Upstream commit timestamp: 2026-10-16T09:55:38Z  
License text inspected: MIT

## Problem and implementation

Provides a model-driven browser agent and tool interfaces for inspecting and interacting with web pages.

browser_use/agent/service.py hosts the agent loop; browser_use/mcp/server.py provides an MCP surface. Agent state and action results carry observations and run history. The tree separates agent logic from browser handling and integrations.

## Published direction

The README documents hosted, CLI and Python-library paths. These are alternative access modes; no standalone dated roadmap was verified.

## Application to Sixth

Adopt the Python library behind Sixth's BrowserExecutor interface after a pinned-version spike. Send a narrow task and relevant constraints, then verify returned page or cart state independently.

Browser execution does not supply Sixth's durable personal memory or safe retry semantics. Keep tenancy, approvals, credentials and the action ledger outside the browser agent.

## Repository structure

Selected directories in the pinned tree:

```text
browser_use/agent/
browser_use/browser/
browser_use/mcp/
examples/
tests/
```

[Browse the pinned tree](https://github.com/browser-use/browser-use/tree/ccd22fef47a1a36e0c4596fef5db73a5117b9d06). This is a selected map, not the complete repository.

## Evidence inspected

- [browser_use/agent/service.py](https://github.com/browser-use/browser-use/blob/ccd22fef47a1a36e0c4596fef5db73a5117b9d06/browser_use/agent/service.py)
- [browser_use/mcp/server.py](https://github.com/browser-use/browser-use/blob/ccd22fef47a1a36e0c4596fef5db73a5117b9d06/browser_use/mcp/server.py)
- [README.md](https://github.com/browser-use/browser-use/blob/ccd22fef47a1a36e0c4596fef5db73a5117b9d06/README.md)
- [LICENSE](https://github.com/browser-use/browser-use/blob/ccd22fef47a1a36e0c4596fef5db73a5117b9d06/LICENSE)

Review scope: repository tree, README, license text, and selected implementation/architecture sections. Large files were inspected selectively. No repository was installed, executed, benchmarked, or audited end to end. Sixth recommendations above are our design choices.
