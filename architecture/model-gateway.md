# Provider-independent Model Gateway

Status: **SPECIFIED interface; no adapters or credentials implemented**.

Every node accesses models through this interface, including local inference.
Future adapters may support GitHub Copilot, OpenAI, Anthropic, open-source
models, local inference servers, or other compatible providers. No provider is
required, selected, or granted organizational authority.

## Request contract

Request ID, organization/agent/task/runtime/node IDs, current assignment/fencing
context, pinned configuration, capability requirements, model-selection policy,
input/artifact references with privacy classification, permitted tool set,
budget reservation, deadline, idempotency key, retry policy, and tracing context.
Provider/model IDs are routing metadata, never agent/CEO identity.

The gateway authenticates the workload, verifies permission, current scoped
assignment, privacy/residency constraints, budget and route authorization, then
selects an eligible provider/model by capability, cost, latency, availability and
policy. A failover may not broaden data access, tool permissions, token ceilings,
budget, or external scope. No eligible route means a reported blocked/failed
operation, not an unauthorized fallback.

## Response and accounting contract

Return structured status, output/artifact references, selected provider/model
and revision when available, finish reason, request/trace IDs, latency, usage,
cost and uncertainty, retry/error classification, and safe provenance.
Provider output is untrusted data, never approval or policy.

Usage contains known token counts or explicit `unknown/not_reported`; never
invent counts. Cost records currency, estimate/actual status, price source,
unknown values, and reservation settlement. Unknown accounting blocks further
spending when allowance cannot be guaranteed; it is not silently zero.

Rate-limit enforcement, bounded exponential backoff with jitter, deadlines,
request deduplication and circuit breaking belong in adapters/gateway policy.
Retry only classified safe failures and reconcile ambiguous responses with
provider request IDs. Model calls may themselves incur duplicate cost; do not
promise exactly-once billing.

## Credentials and portability

Each runtime uses an explicitly authorized workload credential profile stored
in a secret manager/OS credential store, with rotation, expiry, scope and
revocation. Git/prompt/config stores contain opaque profile references only.
Do not pass personal browser sessions or tokens to agents.

A personal GitHub Copilot login on Local does not authenticate Cloud and may
not permit unattended use. Validate each provider's supported API, licensing,
terms, and workload authentication before implementing an adapter. No particular
Copilot automation API is assumed to exist.

Tool actions remain behind the separate governed execution/effect gate; a model
response requesting a tool is not permission to invoke it. Logs redact prompts,
personal data, credentials and provider secrets. Export configuration and
provenance in provider-neutral formats for replacement and handover.
