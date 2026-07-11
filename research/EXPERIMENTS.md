# Pending Experiments (Agents Unite Paper)

Actionable checklist for numbers the paper describes but does not yet measure.
Status reflects the architecture paper as of July 2026.

## Already cited (external; do not re-claim as AU results)

| Result | Source | Use in paper |
|--------|--------|--------------|
| SciFact 81.5% → 98.2% (+20.5%) federated tree-sharing | Folklore BEIR bench | Analogy for shared-ledger reuse |
| NFCorpus 77.3% → 97.6% (+26.2%) | Folklore | Same |
| FiQA 66.0% → 94.5% (+43.3%) | Folklore | Same (finance-relevant corpus) |
| LLM / terminal / alt-data list prices | OpenAI, Tiingo, Polygon, NeuGroup, Neudata | Cost tables |

## Pending for Agents Unite (must run on AU data)

### 1. Sentiment factor backtest (highest priority)

**Claim to support:** Crowd `sentiment_score` / `consensus_score` has predictive content.

**Inputs**
- Merged reports under `data/YYYY-MM-DD/TICKER/` for ≥60 trading days (ideally ≥1 year)
- Price series: Tiingo Power or Polygon (see paper Table `tab:market-data`)

**Procedure**
1. `python examples/load_reports.py --json --since YYYY-MM-DD > sentiment.jsonl`
2. Align scores to US close (or UTC midnight); document choice
3. Compute forward returns for h ∈ {1, 5, 20}
4. Quintile sorts + Spearman IC; bootstrap CIs
5. Optional: split by modality (sentiment/news/social/trading) and by `prompt_hash`

**Outputs for paper:** Table of IC / quintile spreads; figure optional.

**Blockers:** Need enough calendar depth in the live Agents Unite repo.

---

### 2. Federation-style reuse on AU ledger (Folklore analog)

**Claim to support:** Querying the shared Git ledger beats a single-node cache of one contributor’s history (same decision rule / false-accept budget).

**Inputs**
- Embeddings of report bodies + consensus.md (Phase 2 wiki path)
- Query set: paraphrases of real research questions (“What was NVDA sentiment before earnings?”)

**Procedure**
1. Build single-node cache = one `github_username` history
2. Build federated pool = all merged reports (or all contributors)
3. At ≤2% false-accept (cross-encoder or score threshold), measure recall@1 of retrieving a relevant prior answer
4. Report SciFact-style table for AU tickers (or FiQA-style finance queries over AU text)

**Outputs:** AU version of Table `tab:federation`.

**Blockers:** Phase 2 embeddings/RAG not shipped; need embedding + eval harness.

---

### 3. Cheap verify cascade (yes/no + cross-encoder)

**Claim to support:** Verifiers can be ≪ research cost without collapsing quality.

**Inputs**
- 200–500 labeled (claim, source_snippet, support∈{yes,no,unknown}) pairs from real PRs
- Models: GPT-4o-mini yes/no; local cross-encoder NLI (e.g. DeBERTa-MNLI / Provenance-style)

**Procedure**
1. Baseline: full research agent re-derives report (\$)
2. Cascade A: LLM yes/no only
3. Cascade B: cross-encoder then LLM on low-confidence
4. Report \$/decision, latency, F1 vs human labels

**Outputs:** Cost/quality table for Section `sec:cheap-verify`.

---

### 4. Source-diversity weighting

**Claim to support:** Weighting by URL/model/modality diversity beats n-count herding.

**Procedure**
1. On days with n≥5 reports, compute equal-weight, stake-only, and diversity-weighted medians
2. Score each against next-day return sign or ex-post consensus
3. Ablate diversity features

**Blockers:** Needs Phase 3 consensus automation + enough multi-report days.

---

### 5. Adversarial probes

**Claim to support:** Bound (not over-claim) IPI and Sybil risk.

**Procedure**
1. Inject prompt-injection payloads into cited HTML; measure verifier approve rate
2. Sybil ring: k accounts, coordinated scores; measure MAD + reputation response
3. Author rewrites Adversarial section after measured ASR

**Blockers:** Author sign-off (TODO in tex); red-team harness.

---

## Phase roadmap mapping

| Phase | Product work | Experiments unlocked |
|-------|----------------|----------------------|
| 1 (active) | Daily PR + CI | Backtest once depth exists; label verify pairs |
| 2 | Hourly shards, embeddings, wiki | Federation-style reuse (#2); RAG query demos |
| 3 | Automated consensus | Diversity weights (#4) |
| 4 | Reputation / attestation | Sybil sims (#5); stake gating |

## Minimum viable “results” section for next paper revision

1. Run #1 on whatever history exists (even 30–60 days) with clear caveats  
2. Prototype #3 on 100 hand-labeled claims (cheap, no Phase 2 required)  
3. Keep Folklore Table `tab:federation` as external analogy until #2 lands on AU data  
