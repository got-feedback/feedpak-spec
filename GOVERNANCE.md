# Governance

This document describes how the feedpak specification is maintained and how new versions are
decided and cut. It is intentionally lightweight; the goal is a stable, predictable format,
not bureaucracy.

## Roles

- **Maintainers** — the people with merge rights on this repository. They review proposals,
  steward releases, and are responsible for keeping the spec, schemas, examples, and validator
  consistent with one another.
- **Contributors** — anyone who opens an issue or pull request. No special status is required
  to propose a change.

## How decisions are made

Changes are proposed and discussed in the open as **feedpak Enhancement Proposals (FEPs)** —
see [CONTRIBUTING.md](CONTRIBUTING.md). The working model is **rough consensus**:

- A proposal is accepted when it has a clear on-disk design, no unresolved objections from
  maintainers, and the corresponding spec + schema + example + changelog changes are ready.
- Editorial changes (typos, clarifications that do not change conformance) may be merged by a
  maintainer without a FEP.
- When consensus cannot be reached, maintainers make the final call, and the reasoning is
  recorded in the issue or PR.

## Compatibility is the prime directive

The format exists so that independently written tools can exchange songs. Every decision is
weighed against that. In practice:

- **Prefer additive change.** New capability should arrive as a new *optional* manifest key or
  side-file that older readers can ignore (a MINOR bump). This is how every extension has
  shipped so far and should remain the default.
- **Deprecate, don't break.** When a field must change, the preferred path is: add the new
  field, mark the old one deprecated in the spec, and keep reading it for at least one MINOR
  release before any MAJOR release removes it. This mirrors the spec's own guidance
  ([§9.4](spec/feedpak-v1.md#94-stay-backward-compatible)) and is binding process here.
- **MAJOR bumps are rare and deliberate.** A backward-incompatible change requires a new spec
  document (`spec/feedpak-v2.md`) and an explicit migration note, not an in-place edit.

## Cutting a release

A maintainer cuts a specification release by:

1. Ensuring the spec, `schemas/`, `examples/`, and `tools/validate.py` are mutually consistent
   and CI is green.
2. Moving the `[Unreleased]` entries in [CHANGELOG.md](CHANGELOG.md) under a new version
   heading with the date.
3. Updating the version/date in the spec header and the README badge table.
4. Tagging the commit (`vMAJOR.MINOR.PATCH`) so the published version is immutably frozen, and
   creating a matching GitHub release.

Version numbers follow the policy in [spec §4.2](spec/feedpak-v1.md#42-compatibility-policy).

## Relationship to implementations

This repository defines the format only. Applications that read or write feedpak (including
those in the wider feedback project) are separate efforts and track this spec as a dependency;
they do not drive it. A change is not part of the format until it lands here.
