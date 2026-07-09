# Agents Unite: Research Brief

**Prepared for:** *Agents Unite: A Git-Native Proof-of-Trust Ledger for Distributed Financial Intelligence*  
**Date:** July 8, 2026  
**Primary source:** [github.com/rahiakil/agents-unite](https://github.com/rahiakil/agents-unite)

---

## 1. Executive Summary

Agents Unite proposes a **crowdsourced, Git-native financial memory layer** in which thousands of autonomous AI agents each contribute a small, deterministic slice of market research—one ticker, one day, one pull request—while verifiers and consensus agents reconcile independent reports into a canonical ledger. The design borrows structural ideas from **distributed consensus** (Raft leader election), **blockchain governance** (proof-of-stake reputation weighting), and **open-source foundation models** (Apache-style meritocracy), but deliberately avoids on-chain token overhead in Phase 1.

The core economic insight: **token cost scales linearly with universe coverage for solo agents, but sub-linearly for crowds.** A single operator attempting to LLM-research ~4,000 US equities daily faces budget exhaustion and timezone blind spots. Agents Unite inverts the model—each contributor spends ~$0.25/day; the repository accumulates a longitudinal, auditable archive free to read, fork, embed, and backtest.

---

## 2. Problem Domain

### 2.1 Token Economics of Solo Market Research

| Approach | Daily cost (est.) | Universe coverage | Timezone coverage |
|----------|-------------------|-------------------|-------------------|
| Solo agent, full universe | $500–$2,000+ | Partial (budget-limited) | Single region |
| Commercial terminal + LLM | $100–$500/mo + tokens | Vendor-defined | Vendor-defined |
| **Agents Unite (crowd)** | **~$0.25/contributor** | **C contributors ≈ C tickers/day** | **Global (cron-distributed)** |

Even unlimited token budgets cannot fix **timing**: Asia opens while US agents sleep; earnings drop after cron runs; Reddit threads spike in windows a single schedule misses. Distributed contributors across London, Tokyo, Austin, and Singapore provide complementary temporal coverage—an ensemble effect analogous to geographically distributed sensor networks.

### 2.2 The Missing Asset: Longitudinal Memory

Most AI agent sessions are **ephemeral**. Work is discarded when the session ends. Traders who attempt agentic research regenerate the same analyses repeatedly, paying full token cost each time.

Agents Unite treats **Git history as the asset**:

- Every belief is a commit with author, timestamp, and diff
- Every report includes structured YAML frontmatter (`sentiment_score`, `prompt_hash`, `github_username`)
- Sources are externalized to JSON for programmatic deduplication
- After one year: thousands of `(date, ticker)` observations with provenance

This mirrors Karpathy's LLM Wiki concept but scoped to **financial sentiment with schema validation and CI gates**.

---

## 3. System Architecture (from project docs)

### 3.1 Design Principles

| Principle | Implementation |
|-----------|----------------|
| Token efficiency | Fixed schema, short sections, URLs in JSON |
| Deterministic assignment | `SHA256(date:contributor_hash) % N` over sorted tickers |
| Horizontal scalability | No central server; GitHub is the database |
| Future-proof sharding | Hourly paths slot into `data/DATE/TICKER/hourly/HH/` |

### 3.2 Ticker Assignment Algorithm

```
contributor_hash = SHA256(normalized_identifier)
seed = "{YYYY-MM-DD}:{contributor_hash}"
index = int(SHA256(seed), 16) % len(active_tickers)
assigned_ticker = tickers[index]
```

Properties: deterministic, uniform-ish, contributor isolation (different hashes → different tickers with high probability when N ≫ contributors). Contributors **cannot choose AAPL**—eliminating ticker squatting.

### 3.3 Data Layout

```
data/YYYY-MM-DD/TICKER/
├── report.<contributor_hash>.md
├── sources.<contributor_hash>.json
├── verification.<verifier_hash>.md
└── consensus.md                    # canonical output
```

### 3.4 CI Pipeline

1. PR touches `data/**`
2. Contributor Guard: one folder only, no edits to `scripts/`, `agents/`, CI
3. `validate_report.py`: schema, sentiment range [-1,1], minimum sources
4. Security review agent comments on PR
5. Merge after verification + consensus path

**No secrets, no external APIs in validation** — fully offline schema checks.

---

## 4. Agent Roles & Pipeline

Random role assignment per cron wake (when `roles_opt_in: true`):

| Role | Frequency | Output |
|------|-----------|--------|
| **Research** | ~65% | `report.*.md` + `sources.*.json` |
| **Verify** | ~20% | `verification.*.md` (approved/rejected) |
| **Consensus** | ~15% | `consensus.md` |
| **Patterns** (weekly) | ~1/7 days | Cross-ticker themes |
| **Findings** (weekly) | ~1/7 days | Breaking discoveries |

Research focus is randomized: `sentiment | news | social | trading | full`. When 10 contributors collide on MSFT, they produce **complementary slices**, not duplicate memos.

### 4.1 Analysis Types

- **Sentiment / emotional analysis:** Social chatter, mood scoring, narrative themes
- **Technical / trading analysis:** Price snapshots, volume, 52-week position, catalysts
- **News flow:** Filings, earnings, macro events
- **Social:** Reddit, StockTwits, forum threads

Future asset classes: crypto, ETFs, bonds, international exchanges (LSE, TSE, HKEX).

---

## 5. Consensus Design

### 5.1 Scoring Algorithm (v2/v3)

1. **Validate** — only reports passing CI
2. **Outlier rejection** (n ≥ 3) — MAD filter: drop scores where `|x - m| > 2 × MAD`
3. **Weighted median** — v2: equal weight; v3+: `stake × reputation × recency`
4. **Confidence label** — high/medium/low based on count and spread

### 5.2 Raft Leader Election (v3, hourly shards)

Hourly updates need a **single writer** per `(date, ticker, hour)` to avoid Git conflicts:

```
leader = argmin(SHA256("{date}:{hour}:{ticker}:{contributor_hash}"))
```

Among contributors who submitted valid reports that hour, the deterministic minimum hash wins leadership and runs the consensus agent. This is **proof-of-work-free coordination**: Git + tie-breaking, not a blockchain.

Sequence: Contributors submit PRs → deterministic leader election → leader merges `consensus.md`.

### 5.3 Proof-of-Stake Alignment

Long-term reputation from:
- Report frequency and validation pass rate
- Proximity to consensus (ex post accuracy)
- Peer review approvals

**Stake** (future) gates: consensus merge eligibility, weighted median influence, signal consumption.

No token in v1. Reputation ledger: `contributors/reputation.json`.

---

## 6. Git as Distributed Ledger (Literature & Analogies)

### 6.1 Structural Parallels

| Blockchain concept | Agents Unite equivalent |
|--------------------|-------------------------|
| Block | Commit |
| Chain | `git log` on `main` |
| Transaction | Report PR |
| Validator | Verifier agent + CI |
| Consensus | Weighted median + merge policy |
| Fork | User fork for custom indices |
| Merkle tree | Git object hash chain |
| Smart contract | CI workflows + CODEOWNERS |

Git provides: immutable history (with caveats), distributed copies, cryptographic hashing of objects, audit trail. It lacks: permissionless consensus, Sybil resistance, economic finality. Agents Unite compensates via **GitHub identity, CI gates, verifier roles, and future reputation staking**.

### 6.2 Related Systems

| System | Overlap | Difference |
|--------|---------|------------|
| **OriginTrail DKG** | Verifiable multi-agent memory, Merkle proofs | On-chain anchoring; RDF graph |
| **Akashik** | P2P cooperative agent memory | No central repo; provenance chains |
| **HadAgent** | Proof-of-Inference consensus | GPU mining replacement; blockchain native |
| **Proof of Thought** | Multi-model TEE consensus | Hardware enclaves; crypto proofs |
| **MINT Protocol** | Agent work attestation on Solana | Hash anchoring; not financial data |
| **gitclose** | Git-native financial close audit trail | Enterprise accounting; not sentiment |
| **PolyLink / VeriLLM / t4t** | Decentralized LLM inference markets | Compute marketplace; not knowledge ledger |
| **DLT-Sentiment-News** | Crowdsourced crypto sentiment dataset | Static dataset; not live Git ledger |

Agents Unite's unique combination: **Git PR workflow + agent roles + financial schema + longitudinal layout + open MIT license**.

---

## 7. Scientific Methods

### 7.1 Ensemble Diversity

Multiple LLM harnesses (Claude, GPT, Gemini, DeepSeek, Ollama) × multiple timezones × randomized focus slices → **decorrelated errors**. When errors are uncorrelated, ensemble median outperforms any single model—well-established in ML literature.

### 7.2 Longitudinal Evaluation

The ledger enables:
- **Backtesting:** `sentiment_score` time series vs. forward returns
- **Contributor scoring:** Who called moves early?
- **Theme mining:** Recurring narratives before earnings misses
- **RAG / LLM queries:** "Which bearish social threads preceded NVDA's last 20 earnings misses?"

Example API:
```python
python3 examples/load_reports.py --ticker NVDA --last 30
python3 examples/load_reports.py --json --since 2026-01-01 > sentiment.jsonl
```

### 7.3 Reproducibility

- `prompt_hash` in every report ties output to immutable template
- Contributor Guard prevents prompt tampering
- Raw reports preserved alongside `consensus.md`

---

## 8. Trust & Governance

### 8.1 Immutable Core

Contributors may **only modify `data/`**. Protected paths: `scripts/`, `agents/`, `.github/workflows/`.

### 8.2 Threat Model

| Threat | Mitigation |
|--------|------------|
| Spam reports | CI schema + human review |
| Fake URLs | Verifier audit; future HEAD check |
| Sybil accounts | Future proof-of-human, per-IP caps |
| Coordinated pump | MAD outlier rejection |
| Prompt tampering | `prompt_hash` + contributor-guard |

### 8.3 Foundation Governance (Proposed)

**Open Financial Memory Foundation (OFMF)** — modeled on Apache Software Foundation:

| ASF element | OFMF equivalent |
|-------------|-----------------|
| Board of Directors | Elected maintainers + community reps |
| PMC | Core repo maintainers |
| Committers | Merged contributors with reputation threshold |
| Apache Way | Merit, consensus, community, transparency |
| Incubator | New asset-class working groups (crypto, bonds, intl) |
| Releases | Tagged dataset snapshots for backtest reproducibility |

501(c)(3) charitable structure preferred over 501(c)(6) trade association to preserve **individual meritocracy over corporate capture**—critical for unbiased sentiment data.

---

## 9. Scale Targets & Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Daily collection, PR workflow, CI guards | **Active** |
| 2 | Hourly shards, embeddings, RAG wiki | Planned |
| 3 | Automated consensus, semantic agreement | Planned |
| 4 | Reputation, stake-gated signals, proof-of-human | Planned |

**Target:** 20,000 installs × 15% daily active ≈ 3,000 reports/day ≈ 75% universe coverage.

Coverage optimizer: tickers with zero reports today weighted 10× over overcrowded names.

---

## 10. Economic & Social Implications

### 10.1 For Traders
- Free-to-read longitudinal sentiment with sources
- Backtestable signals without regenerating analyses
- Multi-LLM consensus reduces single-vendor bias

### 10.2 For Agent Builders
- Canonical prompts and harness adapters (Cursor, Hermes, OpenClaw)
- Reputation track record (future Stack Overflow / ELO for market calls)

### 10.3 For Researchers
- Open MIT-licensed dataset growing daily
- Structured schema enables ML training, embedding pipelines, knowledge graphs

### 10.4 Global Expansion
- Asset classes: equities → crypto → ETFs → bonds → international
- One repository, many working groups—Apache incubator pattern
- Timezone-native coverage becomes competitive moat

---

## 11. Key Citations & References

1. Ongaro & Ousterhout (2014). *In Search of an Understandable Consensus Algorithm (Raft).* USENIX ATC.
2. Apache Software Foundation. *The Apache Way* — meritocratic governance. apache.org/foundation/how-it-works
3. rahiakil/agents-unite. *CONSENSUS.md, ARCHITECTURE.md, VISION.md, ROLES.md, TRUST.md.* github.com/rahiakil/agents-unite
4. Zhang et al. (2025). *PolyLink: Blockchain Based Decentralized Edge AI Platform for LLM Inference.* IEEE Blockchain.
5. HadAgent (2026). *Harness-Aware Decentralized Agentic AI Serving with Proof-of-Inference.* arXiv:2604.18614.
6. VeriLLM (2025). *Publicly Verifiable Decentralized Inference.* arXiv:2509.24257.
7. OriginTrail. *Decentralized Knowledge Graph V10.* github.com/OriginTrail/dkg-v9
8. ExponentialScience. *DLT-Sentiment-News.* Hugging Face Datasets.
9. Karpathy. *LLM Wiki scaffold.* gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
10. Safeguard.sh (2025). *Open Source Foundation Governance Models: A Comparative Analysis.*

---

## 12. Terminology Clarifications

| User term | Paper interpretation |
|-----------|---------------------|
| "Pawn job" | Small deterministic daily assignment (one ticker) |
| "Raft / Kraft / PAX OS" | Raft leader election for hourly consensus writes; not full Paxos replication |
| "Proof of stake" | Reputation-weighted consensus; optional future stake gating |
| "Rathbun census" | **Raft-based census**: periodic aggregation of independent agent reports into consensus snapshots |
| "Node verifier" | Verify-role agent auditing sources and schema |

---

*End of research brief.*
