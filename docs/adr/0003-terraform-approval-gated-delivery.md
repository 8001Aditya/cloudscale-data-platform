# ADR 0003: Use Terraform with approval-gated delivery

## Status

Accepted

## Context

Infrastructure must be reproducible, reviewable, and safe for a portfolio environment with controlled cloud spend.

## Decision

Define Azure infrastructure in Terraform modules. Continuous integration validates formatting and plans; resource creation or changes require an explicit manual approval through a protected GitHub environment.

## Consequences

Infrastructure changes are reviewable and repeatable. Initial setup requires an approved remote-state design and OIDC federation, which will be implemented before any deployment workflow.
