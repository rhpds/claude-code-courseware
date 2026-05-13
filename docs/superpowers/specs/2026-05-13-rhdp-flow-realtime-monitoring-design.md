# RHDP-Flow Real-Time Monitoring and Deeper OCP Visibility

**Date:** 2026-05-13
**Status:** Draft
**Approach:** B — Watcher Agent + MCP Tools
**Builds on:** 2026-05-08-rhdp-flow-full-integration-design.md

## Context

The RHDP-Flow tool suite currently has three MCP servers (rhdp-ops-mcp with 9 tools, rhdp-intake-mcp with 4 tools, rhdp-flow-mcp with 20 tools) plus companion skills and agents. During Summit 2026 operations (71 live workshops, 74 resource pools, 6 MultiWorkshop groups, 1,235 catalog items), ops needs proactive alerting rather than manual polling. Several Kubernetes CRD types with valuable operational data are not yet surfaced by any tool.

## Goals

1. **Real-time monitoring** — a background watcher agent that detects state changes and surfaces alerts in the Claude session without manual polling.
2. **Deeper OCP visibility** — new MCP tools that expose CatalogItems, ResourcePools, MultiWorkshops, and ServiceAccesses.
3. **Event-scale operations** — MultiWorkshop-aware extend/scale, pool health dashboards, and summary views.

## Non-Goals

- Team-wide Slack alerting (Approach C — can be layered later).
- Persistent watcher service surviving session restarts.
- Cross-tool unification of the three MCP servers.

## Architecture

```
OCP Cluster (K8s API)
    |
    | workshops, workshopprovisions, workshopuserassignments,
    | resourceclaims, resourcepools, multiworkshops,
    | catalogitems, serviceaccesses
    |
    v
rhdp-ops-mcp (FastMCP server)
    |
    | ops_snapshot, ops_pool_health, ops_catalog_items,
    | ops_resource_pools, ops_multiworkshop, ops_service_accesses,
    | ops_watch_config + existing 9 tools
    |
    v
ops-watcher (background agent via ScheduleWakeup)
    |
    | compare snapshots, detect transitions,
    | deduplicate, escalate
    |
    v
Claude Code session (alerts surface in conversation)
```

The MCP server is the "eyes" — it provides raw state from OCP via new and existing tools. The watcher agent is the "brain" — it decides what's worth alerting on and formats output. Clean separation: data retrieval in the MCP layer, alert logic in the agent layer.

## New MCP Tools

### State Snapshot Tools (for the watcher)

#### `ops_snapshot(namespace: str = "", stage: str = "")`

Returns a compact, diffable representation of all workshops with:
- Workshop name, namespace, display_name, stage
- Provision phase (Provisioning, Ready, Failed, Deleting)
- Stop time, destroy time (ISO 8601)
- Seat count (assigned/capacity)
- White-glove flag
- MultiWorkshop membership (if any)

Filters by namespace or stage when provided. Designed for periodic comparison — the watcher calls this every tick and diffs consecutive results.

Returns: `list[SnapshotRow]` as JSON.

#### `ops_pool_health(pool_name: str = "")`

Returns ResourcePool status from `poolboy.gpte.redhat.com/v1`:
- Pool name
- minAvailable (configured minimum)
- available, ready, unready counts (from `status.resourceHandleCount`)
- lifespan config (default, maximum, unclaimed TTL)
- Health flag: `healthy` when `available >= minAvailable`, `degraded` when below

When `pool_name` is provided, returns detail for one pool. Otherwise returns all pools.

Returns: `list[PoolHealthRow]` as JSON.

#### `ops_watch_config(thresholds: str = "")`

Get or set alert thresholds for the current session. Thresholds are passed to the watcher agent via its loop prompt and carried between ticks. The MCP tool provides a consistent interface for reading/writing them, but the agent is the authority — it interprets thresholds when classifying events.

Default thresholds:
- Deadline: critical < 1h, warning < 4h, info < 24h
- Seats: warning at 80%, critical at 100%
- Pools: alert when `available < minAvailable`

Input format: `"deadlines=1h,4h,24h seats=80,100 pools=auto"`

Returns: current threshold configuration as JSON.

### Deeper Visibility Tools

#### `ops_catalog_items(stage: str = "", search: str = "")`

Lists CatalogItems from `babylon.gpte.redhat.com/v1`:
- Name, display name, stage (dev/event/prod)
- Category (from annotations)
- Age
- Namespace

Filters by stage and/or substring search. Answers "what can we deploy?" without the catalog UI.

Returns: `list[CatalogItemRow]` as JSON.

#### `ops_resource_pools(pool_name: str = "")`

Detailed pool inventory from `poolboy.gpte.redhat.com/v1`:
- Pool name, namespace
- minAvailable, maxUnready
- Lifespan config (default, maximum, relativeMaximum, unclaimed)
- Resource handle counts (available, ready, unready)
- Resource provider references
- deleteUnhealthyResourceHandles flag

More detailed than `ops_pool_health` — this is for investigation, not monitoring.

Returns: `list[ResourcePoolDetail]` as JSON.

#### `ops_multiworkshop(namespace: str, name: str)`

Returns a MultiWorkshop resource and all its linked assets:
- MultiWorkshop display name, description, purpose
- Start date, end date, number of seats
- Assets list: each asset's display name, catalog key, workshop name, namespace, workshop ID
- Per-asset workshop status (by looking up each linked workshop)

This enables MultiWorkshop-aware operations.

Returns: `MultiWorkshopDetail` as JSON.

#### `ops_service_accesses(namespace: str, workshop_name: str = "")`

Lists active ServiceAccess resources:
- User identity
- Workshop reference
- Access state
- Created timestamp

Shows who is actually connected to a workshop right now, beyond seat assignment counts.

Returns: `list[ServiceAccessRow]` as JSON.

## Watcher Agent

### Lifecycle

Implemented as a `/ops watch` skill command that spawns a background loop:

| Command | Behavior |
|---------|----------|
| `/ops watch` | Start watcher with default thresholds |
| `/ops watch stop` | Stop the running watcher |
| `/ops watch status` | Current state, last check time, alert counts |
| `/ops watch config` | Show current thresholds |
| `/ops watch config deadlines 1h,4h,24h` | Set deadline thresholds |
| `/ops watch config seats 80,100` | Set seat occupancy thresholds |
| `/ops watch config pools auto` | Alert when available < minAvailable |

### Tick Behavior (every ~90-120s)

Each tick:
1. Call `ops_snapshot()` — get current workshop/provision/seat state.
2. Call `ops_pool_health()` — get current pool availability.
3. Compare against previous snapshot (held in the loop's prompt context).
4. Classify changes into four event types.
5. Deduplicate — each unique event ID (workshop + event type + severity) reported once.
6. If alerts exist, surface as formatted message. If no alerts, stay silent.

### Event Types

#### Provision State Changes
- Trigger: workshop provision phase changed between ticks.
- Severity: CRITICAL for `-> Failed`, INFO for `-> Ready`, WARNING for `-> Deleting` (unexpected).
- Event ID: `provision:{namespace}/{name}:{new_phase}`

#### Pool Health Changes
- Trigger: pool's available count dropped below minAvailable, or pool exhausted (available = 0).
- Severity: CRITICAL for exhausted (available = 0), WARNING for degraded (available < minAvailable).
- Event ID: `pool:{pool_name}:{severity}`

#### Deadline Proximity
- Trigger: workshop's stop or destroy time crossed a threshold boundary since last tick.
- Severity: CRITICAL for < 1h or overdue, WARNING for < 4h, INFO for < 24h.
- Deduplicate by threshold — once a workshop enters the 4h window, don't re-alert until it enters the 1h window.
- Event ID: `deadline:{namespace}/{name}:{threshold}`

#### Seat Occupancy Spikes
- Trigger: workshop seat assignment percentage crossed a threshold (80%, 100%).
- Severity: WARNING for >= 80%, CRITICAL for >= 100%.
- Event ID: `seats:{namespace}/{name}:{threshold}`

### Alert Format

```
[WATCHER] 2 alerts at 14:32 UTC

CRITICAL  Provision failed: summit-2026.lb2862-ai-app-dev-cluster.event-w9d8g
          Namespace: summit-2026 | Phase: Failed | Was: Provisioning (3m ago)

WARNING   Pool low: summit-2026.lb2860-private-maas-aws-cluster.event
          Available: 1/4 (minAvailable: 4) | Ready: 1
```

### Escalation

If a CRITICAL alert goes unacknowledged for 2 consecutive ticks (~3-4 minutes), re-surface with `[REPEAT]` prefix. WARNING and INFO alerts do not escalate.

### ScheduleWakeup Configuration

- `delaySeconds: 90` — stays within the 5-minute prompt cache window (avoids cache miss cost). Checks ~40 times per hour.
- Loop prompt carries the previous snapshot as a compact hash/diff-base so the agent can detect changes without external state persistence.

## Event-Scale `/ops` Skill Extensions

### New commands added to the ops skill:

| Command | MCP Tool | What it does |
|---------|----------|-------------|
| `/ops summary` | `ops_summary` | Dashboard: totals, attention count, seat fill, pool health, provision failures |
| `/ops pools` | `ops_resource_pools` | Pool health overview — all pools with availability |
| `/ops pools <name>` | `ops_resource_pools(pool_name)` | Detailed pool info with handle breakdown |
| `/ops catalog` | `ops_catalog_items` | Available catalog items |
| `/ops catalog <search>` | `ops_catalog_items(search)` | Search catalog items |
| `/ops group <ns> <name>` | `ops_multiworkshop` | Show MultiWorkshop and all linked assets |
| `/ops extend <ns> <name> <n>d --group` | `ops_extend_stop` + `ops_multiworkshop` | Extend all assets in a MultiWorkshop group |
| `/ops scale <ns> <name> <n> --group` | `ops_scale_workshop` + `ops_multiworkshop` | Scale all assets in a MultiWorkshop group |

### MultiWorkshop-Aware Operations

When `/ops extend` or `/ops scale` targets a workshop that belongs to a MultiWorkshop group (detected via `ops_multiworkshop` lookup), the tool warns:

```
This workshop is part of MultiWorkshop "automation-voasv" with 3 assets:
  - Ansible Automation Platform Roadshow 01 - Introspection
  - Ansible Automation Platform Roadshow 02 - Standardization
  - Ansible Automation Platform Roadshow 03 - Operational Efficiency

Apply to all 3 assets? (use --group flag to apply to all)
```

Without `--group`, operates on the single workshop only.

## Models (new dataclasses in models.py)

```python
@dataclass
class SnapshotRow:
    name: str
    namespace: str
    display_name: str
    stage: str
    provision_phase: str          # Provisioning, Ready, Failed, Deleting
    stop_time: str | None         # ISO 8601
    destroy_time: str | None      # ISO 8601
    seats_assigned: int
    seats_capacity: int
    white_glove: bool
    multiworkshop_name: str | None

@dataclass
class PoolHealthRow:
    name: str
    min_available: int
    available: int
    ready: int
    unready: int
    health: str                   # healthy, degraded, exhausted

@dataclass
class CatalogItemRow:
    name: str
    display_name: str
    stage: str
    category: str
    namespace: str
    age_days: int

@dataclass
class ResourcePoolDetail:
    name: str
    namespace: str
    min_available: int
    max_unready: int
    lifespan_default: str
    lifespan_maximum: str
    lifespan_unclaimed: str
    available: int
    ready: int
    unready: int
    delete_unhealthy: bool
    provider_names: list[str]

@dataclass
class MultiWorkshopDetail:
    name: str
    namespace: str
    display_name: str
    description: str
    purpose: str
    start_date: str
    end_date: str
    number_seats: int
    assets: list[MultiWorkshopAsset]

@dataclass
class MultiWorkshopAsset:
    display_name: str
    catalog_key: str
    workshop_name: str
    namespace: str
    workshop_id: str
    status: str | None            # from linked workshop lookup

@dataclass
class ServiceAccessRow:
    user: str
    workshop_ref: str
    state: str
    created: str
```

## Implementation Order

1. **New models** — add dataclasses to `rhdp_ops/models.py`
2. **K8s client methods** — add CatalogItem, ResourcePool, MultiWorkshop, ServiceAccess queries to `k8s_client.py`
3. **Snapshot tool** — `ops_snapshot` in `mcp_server.py`
4. **Pool health tool** — `ops_pool_health` in `mcp_server.py`
5. **Visibility tools** — `ops_catalog_items`, `ops_resource_pools`, `ops_multiworkshop`, `ops_service_accesses`
6. **Watch config tool** — `ops_watch_config` with in-memory threshold storage
7. **Watcher agent** — background agent definition in `.claude/agents/ops-watcher.md`
8. **Skill updates** — extend `/ops` skill with watch, summary, pools, catalog, group commands
9. **Tests** — unit tests for all new k8s_client methods and model serialization
10. **Courseware** — update Module 24 or create new Module 28 for the watcher workflow

## Scope Boundary

This design stays within Claude Code's existing architecture. No new services, containers, or Slack integration. The watcher dies with the session — acceptable because event ops are session-scoped. If team-wide alerting is needed later, Approach C can be layered on top without changing these tools.

## Cluster Requirements

- `oc login` with token that has read access to workshops, workshopprovisions, workshopuserassignments, resourceclaims, resourcepools, multiworkshops, catalogitems, serviceaccesses across relevant namespaces.
- Write access for extend/scale/lock operations (existing requirement).
- Python `kubernetes` client library (already a dependency of rhdp-ops-mcp).
