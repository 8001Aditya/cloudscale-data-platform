# ADR 0002: Use Azure Event Hubs through its Kafka-compatible endpoint

## Status

Accepted

## Context

The platform needs managed streaming ingestion while remaining demonstrably compatible with common Kafka clients and patterns. Operating a Kafka cluster would add cost and operational scope that do not serve the first project phases.

## Decision

Use Azure Event Hubs Standard with its Kafka-compatible endpoint for Azure integration. Use a Kafka-compatible local broker in later local-development phases.

## Consequences

This preserves Kafka producer and consumer skills while eliminating Kafka broker management in Azure. Features that require a full Kafka ecosystem will be assessed explicitly instead of assumed available.
