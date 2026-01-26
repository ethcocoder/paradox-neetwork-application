# Internet & Domain Architecture

## Zero-Rated + Normal Internet Coexistence

---

## 1. Purpose of This Document

This document explains **how the Paradox Network Application (PNA)** can operate under a **zero-rated domain provided by Ethio Telecom**, while still being able to safely and legally access the wider internet for non-core functionality.

The goal is to clearly separate **free national traffic** from **normal internet traffic**, without breaking app functionality or violating telecom policies.

---

## 2. Core Concept: Dual Traffic Lanes

PNA operates using **two strictly separated network lanes**:

| Lane | Description | Cost Model |
|----|------------|-----------|
| **Lane A** | Core Paradox Communication | Zero-rated (Free) |
| **Lane B** | External / Non-core Internet | Normal billing |

Ethio Telecom only zero-rates **Lane A**.

---

## 3. Zero-Rated Domain (Lane A)

### 3.1 Definition

The zero-rated domain is the **only domain** approved by Ethio Telecom for free access.

Examples:
- `core.pna.et`
- `ptp.pna.et`

All critical communication traffic flows exclusively through this domain.

---

### 3.2 Traffic Allowed on Zero-Rated Domain

Only the following traffic types are permitted:

- Latent message payloads
- Semantic vectors
- Temporal deltas
- Control signals
- Subscription validation
- Emergency & priority messages

❌ No raw media streaming
❌ No third-party content
❌ No tunneling or proxy traffic

---

### 3.3 Telecom Enforcement

Ethio Telecom applies:

- Domain whitelisting
- IP range filtering
- Deep Packet Inspection (DPI)

Rule example:

> If destination domain ∈ PNA Zero-Rated List → Data cost = 0

All other traffic is billed normally.

---

## 4. Normal Internet Access (Lane B)

### 4.1 Purpose

Lane B handles all **non-critical** or **optional** features, including:

- App updates
- External APIs
- Analytics (opt-in)
- Optional integrations

---

### 4.2 Behavior Without Data

If the user has **no data balance**:

- Lane B becomes unavailable
- App does NOT crash
- Core communication continues via Lane A

This guarantees service continuity in rural and low-connectivity environments.

---

## 5. Application-Level Routing Logic

The application enforces strict routing rules:

- Core communication → Zero-Rated Domain only
- External services → Normal internet only

No fallback or redirection from Lane B into Lane A is allowed.

This prevents abuse and ensures telecom compliance.

---

## 6. Security & Abuse Prevention

To maintain zero-rating approval, PNA enforces:

- Domain-bound request signing
- Payload size limits
- Rate limiting per sender
- Latent payload validation
- Anomaly detection

Any violation automatically blocks traffic at the application level.

---

## 7. Why This Model Is Telecom-Safe

This architecture ensures:

- Predictable bandwidth usage
- No VPN or proxy behavior
- No third-party data leakage
- Full inspectability by Ethio Telecom

The system behaves as a **single-purpose national service**, not a general internet gateway.

---

## 8. Failure Modes & Graceful Degradation

| Scenario | App Behavior |
|--------|-------------|
| No mobile data | Core app works normally |
| Network congestion | Latent traffic prioritized |
| External API down | Non-critical features disabled |
| Partial connectivity | Messages queue & reconstruct later |

---

## 9. Regulatory Alignment

This design aligns with:

- Zero-rating policies
- National ICT regulations
- Emergency communication standards

It minimizes regulatory risk while maximizing public access.

---

## 10. Summary

PNA safely operates with:

- One zero-rated domain for essential communication
- Full optional access to the global internet
- Strict separation of concerns
- Strong abuse prevention

This approach enables **free national access without compromising system integrity or telecom trust**.

---

**End of internet.md**