# ADR 0001: Adopt a medallion architecture with Delta Lake

## Status

Accepted

## Context

The platform needs a clear, explainable model for retaining raw events, performing incremental transformation, recovering from failures, and presenting stable analytics tables.

## Decision

Store source-faithful data in ADLS Gen2 and process data through Delta Bronze, Silver, and Gold layers with Azure Databricks and PySpark.

## Consequences

The design supports ACID writes, schema evolution, time travel, incremental processing, and separate data contracts per layer. It also requires deliberate table maintenance, checkpoint management, and data-retention policies.
