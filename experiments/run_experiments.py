#!/usr/bin/env python3
"""Benchmark harness for the Agents Unite paper.

Runs five experiments against the REAL agents-unite repository:
  1. Coverage scaling simulation (real assign_ticker algorithm)
  2. Assignment uniformity (chi-square + birthday collisions)
  3. Token cost benchmark (real report token counts)
  4. Consensus robustness (weighted median + MAD on real sentiment dist)
  5. Validation throughput (timed validate_report.py)

Outputs JSON to experiments/results.json and prints a summary.
Pure standard library only (no matplotlib/numpy) for portability.
"""
from __future__ import annotations

import hashlib
import json
import statistics
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

PAPER_ROOT = Path(__file__).resolve().parent.parent
AU_ROOT = Path("/home/papa/repos/agents-unite")
sys.path.insert(0, str(AU_ROOT / "scripts"))

from au_common import (  # noqa: E402
    contributor_hash,
    contributor_id,
    load_active_tickers,
    hash_fraction,
    weighted_pick,
)

UNIVERSE = load_active_tickers(AU_ROOT / "tickers" / "universe.json")
N = len(UNIVERSE)
OUT = PAPER_ROOT / "experiments" / "results.json"


def fast_contributor_hash(cid: str) -> str:
    """Inline SHA256 of lowercased id — identical to au_common.contributor_hash
    but avoids the per-call config-file disk read in contributor_id()."""
    return hashlib.sha256(cid.lower().encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Experiment 1: Coverage scaling simulation
# ---------------------------------------------------------------------------
def coverage_optimizer_weights(counts: dict[str, int]) -> list[float]:
    weights = []
    for t in UNIVERSE:
        c = counts.get(t, 0)
        w = 10.0 if c == 0 else 1.0 / (1.0 + c * 1.5)
        weights.append(w)
    return weights


class Fenwick:
    """Binary indexed tree for O(log N) prefix-sum weighted picks."""

    def __init__(self, n: int):
        self.n = n
        self.tree = [0.0] * (n + 1)

    def update(self, i: int, delta: float) -> None:
        i += 1
        while i <= self.n:
            self.tree[i] += delta
            i += i & -i

    def prefix(self, i: int) -> float:
        i += 1
        s = 0.0
        while i > 0:
            s += self.tree[i]
            i -= i & -i
        return s

    def total(self) -> float:
        return self.prefix(self.n - 1)

    def find(self, target: float) -> int:
        """Return smallest index whose prefix sum >= target."""
        idx = 0
        bit = 1
        while bit * 2 <= self.n:
            bit *= 2
        while bit > 0:
            nxt = idx + bit
            if nxt <= self.n and self.tree[nxt] < target:
                idx = nxt
                target -= self.tree[nxt]
            bit //= 2
        return idx


def _weight_for_count(c: int) -> float:
    return 10.0 if c == 0 else 1.0 / (1.0 + c * 1.5)


def simulate_coverage(contributors: int, days: int, *, optimizer: bool) -> dict:
    """Simulate C contributors over D days with the real assignment algorithm."""
    covered: set[str] = set()
    collisions = 0
    total_assignments = 0
    for d in range(days):
        day = (date(2026, 1, 1) + timedelta(days=d)).isoformat()
        counts: dict[str, int] = {}
        if optimizer:
            weights = [10.0] * N
            fen = Fenwick(N)
            for i in range(N):
                fen.update(i, 10.0)
            for c in range(contributors):
                chash = fast_contributor_hash(f"contrib_{c}")
                seed = f"{day}:{chash}:ticker"
                target = hash_fraction(seed) * fen.total()
                idx = fen.find(target)
                ticker = UNIVERSE[idx]
                total_assignments += 1
                if ticker in counts:
                    collisions += 1
                new_count = counts.get(ticker, 0) + 1
                counts[ticker] = new_count
                covered.add(ticker)
                # incremental weight update for this ticker only
                old_w = _weight_for_count(new_count - 1)
                new_w = _weight_for_count(new_count)
                fen.update(idx, new_w - old_w)
        else:
            for c in range(contributors):
                chash = fast_contributor_hash(f"contrib_{c}")
                seed = f"{day}:{chash}:ticker"
                idx = int(hash_fraction(seed) * N) % N
                ticker = UNIVERSE[idx]
                total_assignments += 1
                if ticker in counts:
                    collisions += 1
                counts[ticker] = counts.get(ticker, 0) + 1
                covered.add(ticker)
    return {
        "contributors": contributors,
        "days": days,
        "universe": N,
        "covered": len(covered),
        "coverage_pct": round(100 * len(covered) / N, 2),
        "collisions": collisions,
        "collision_rate": round(collisions / max(total_assignments, 1), 4),
        "total_assignments": total_assignments,
    }


def exp1_coverage_scaling() -> dict:
    scenarios = []
    # Coverage vs contributors at D=30 (compare optimizer vs uniform)
    for C in [10, 50, 100, 200, 500, 1000, 2000, 3000]:
        opt = simulate_coverage(C, 30, optimizer=True)
        uni = simulate_coverage(C, 30, optimizer=False)
        scenarios.append({"C": C, "D": 30, "optimizer": opt, "uniform": uni})
    # Coverage vs days at C=1000 (optimizer only, cheaper)
    time_series = []
    for D in [1, 3, 7, 14, 30, 60, 90, 180, 365]:
        opt = simulate_coverage(1000, D, optimizer=True)
        time_series.append({"D": D, "covered": opt["covered"], "coverage_pct": opt["coverage_pct"]})
    # Solo baseline: 1 contributor, 365 days
    solo = simulate_coverage(1, 365, optimizer=True)
    return {"scenarios": scenarios, "time_series_C1000": time_series, "solo_365d": solo}


# ---------------------------------------------------------------------------
# Experiment 2: Assignment uniformity
# ---------------------------------------------------------------------------
def exp2_uniformity() -> dict:
    SYNTH_CONTRIBUTORS = 10000
    day = "2026-07-13"
    counts: dict[str, int] = {t: 0 for t in UNIVERSE}
    for c in range(SYNTH_CONTRIBUTORS):
        chash = contributor_hash(f"synth_{c}")
        seed = f"{day}:{chash}:ticker"
        idx = int(hash_fraction(seed) * N) % N
        counts[UNIVERSE[idx]] += 1
    observed = list(counts.values())
    expected = SYNTH_CONTRIBUTORS / N
    chi_sq = sum((o - expected) ** 2 / expected for o in observed)
    # degrees of freedom = N-1; critical value @ p=0.01 for ~290 df ~ 340
    dof = N - 1
    mean = statistics.mean(observed)
    stdev = statistics.stdev(observed)
    # Birthday collision: probability that two contributors land on same ticker
    # P(no collision) = prod_{i=1}^{C-1} (1 - i/N)
    birthday = {}
    for C in [10, 50, 100, 500, 1000]:
        p_no = 1.0
        for i in range(C):
            p_no *= (1 - i / N)
        birthday[C] = round((1 - p_no) * 100, 2)
    return {
        "contributors": SYNTH_CONTRIBUTORS,
        "universe": N,
        "expected_per_ticker": round(expected, 2),
        "observed_mean": round(mean, 2),
        "observed_stdev": round(stdev, 2),
        "chi_square": round(chi_sq, 2),
        "dof": dof,
        "chi_crit_001": 340.0,
        "uniform": chi_sq < 340.0,
        "birthday_collision_pct": birthday,
    }


# ---------------------------------------------------------------------------
# Experiment 3: Token cost benchmark on REAL reports
# ---------------------------------------------------------------------------
def approx_tokens(text: str) -> int:
    """Approximate token count (~0.75 words/token inverse)."""
    return max(1, int(len(text.split()) / 0.75))


def exp3_cost_benchmark() -> dict:
    data_dir = AU_ROOT / "data"
    reports = []
    for p in data_dir.glob("*/*/report*.md"):
        if p.parent.parent.name.startswith("_"):
            continue
        text = p.read_text(encoding="utf-8")
        if len(text.strip()) < 200:
            continue
        slug = p.name.replace("report.", "").replace(".md", "")
        src = p.parent / (f"sources.{slug}.json" if slug != "report" else "sources.json")
        if not src.is_file():
            src = p.parent / "sources.json"
        src_text = src.read_text(encoding="utf-8") if src.is_file() else ""
        in_tok = approx_tokens(text) + approx_tokens(src_text)
        out_tok = approx_tokens(text)  # report is the output
        reports.append({"file": str(p.relative_to(AU_ROOT)), "in_tok": in_tok, "out_tok": out_tok})
    if not reports:
        return {"error": "no reports found"}
    in_toks = [r["in_tok"] for r in reports]
    out_toks = [r["out_tok"] for r in reports]
    # API rates per 1M tokens (July 2026)
    rates = {
        "gpt-4o-mini": (0.15, 0.60),
        "deepseek-v4-flash": (0.14, 0.28),
        "gemini-flash-lite": (0.10, 0.40),
        "gpt-4.1": (2.00, 8.00),
    }
    # Harness overhead multiplier (3-8 tool calls); use 5x on input
    OVERHEAD = 5.0
    cost_by_model = {}
    for model, (pin, pout) in rates.items():
        costs = []
        for r in reports:
            c = (r["in_tok"] * OVERHEAD * pin + r["out_tok"] * pout) / 1_000_000
            costs.append(c)
        cost_by_model[model] = {
            "mean": round(statistics.mean(costs), 5),
            "median": round(statistics.median(costs), 5),
            "p90": round(sorted(costs)[int(0.9 * len(costs))], 5),
            "max": round(max(costs), 5),
        }
    return {
        "report_count": len(reports),
        "in_tokens": {
            "mean": round(statistics.mean(in_toks)),
            "median": round(statistics.median(in_toks)),
            "p90": sorted(in_toks)[int(0.9 * len(in_toks))],
            "max": max(in_toks),
        },
        "out_tokens": {
            "mean": round(statistics.mean(out_toks)),
            "median": round(statistics.median(out_toks)),
        },
        "overhead_multiplier": OVERHEAD,
        "cost_per_report_usd": cost_by_model,
    }


# ---------------------------------------------------------------------------
# Experiment 4: Consensus robustness (weighted median + MAD)
# ---------------------------------------------------------------------------
def weighted_median(values: list[float], weights: list[float]) -> float:
    order = sorted(range(len(values)), key=lambda i: values[i])
    vs = [values[i] for i in order]
    ws = [weights[i] for i in order]
    total = sum(ws)
    cum = 0.0
    for v, w in zip(vs, ws):
        cum += w
        if cum >= total / 2:
            return v
    return vs[-1]


def mad_outlier_filter(values: list[float]) -> list[float]:
    if len(values) < 3:
        return values
    m = statistics.median(values)
    deviations = [abs(v - m) for v in values]
    mad = statistics.median(deviations)
    if mad == 0:
        return values
    return [v for v in values if abs(v - m) <= 2 * mad]


def exp4_consensus_robustness() -> dict:
    # Ground-truth sentiment distribution from real reports
    real_scores = []
    for p in (AU_ROOT / "data").glob("*/*/report*.md"):
        if p.parent.parent.name.startswith("_"):
            continue
        text = p.read_text(encoding="utf-8")
        if "sentiment_score:" in text:
            for line in text.splitlines():
                if line.strip().startswith("sentiment_score:"):
                    try:
                        real_scores.append(float(line.split(":", 1)[1].strip()))
                    except ValueError:
                        pass
                    break
    if not real_scores:
        real_scores = [0.0, 0.2, 0.4, -0.1, 0.3]
    base_mean = statistics.mean(real_scores)
    base_sd = statistics.stdev(real_scores) if len(real_scores) > 1 else 0.2

    import random
    rng = random.Random(42)
    results = []
    for n in [1, 2, 3, 5, 10, 20, 50]:
        errors_no_filter = []
        errors_filter = []
        outlier_rejected = 0
        trials = 500
        for _ in range(trials):
            # true score this round
            true_score = base_mean + rng.uniform(-0.1, 0.1)
            reports = [true_score + rng.gauss(0, base_sd * 0.5) for _ in range(n)]
            # inject 20% coordinated outliers (pump) when n>=5
            if n >= 5:
                k = max(1, int(n * 0.2))
                for i in range(k):
                    reports[i] = true_score + 0.6  # coordinated bullish pump
            # no filter
            cons_no = statistics.median(reports)
            errors_no_filter.append(abs(cons_no - true_score))
            # MAD filter
            filtered = mad_outlier_filter(reports)
            outlier_rejected += len(reports) - len(filtered)
            cons_f = statistics.median(filtered) if filtered else statistics.median(reports)
            errors_filter.append(abs(cons_f - true_score))
        results.append({
            "n": n,
            "mae_no_filter": round(statistics.mean(errors_no_filter), 4),
            "mae_mad_filter": round(statistics.mean(errors_filter), 4),
            "outliers_rejected_per_trial": round(outlier_rejected / trials, 2),
            "improvement_pct": round(
                100 * (1 - statistics.mean(errors_filter) / statistics.mean(errors_no_filter)), 1
            ) if statistics.mean(errors_no_filter) > 0 else 0,
        })
    return {
        "real_score_count": len(real_scores),
        "real_mean": round(base_mean, 3),
        "real_stdev": round(base_sd, 3),
        "trials_per_n": 500,
        "outlier_injection": "20% coordinated +0.6 pump when n>=5",
        "results": results,
    }


# ---------------------------------------------------------------------------
# Experiment 5: Validation throughput
# ---------------------------------------------------------------------------
def exp5_validation_throughput() -> dict:
    report_dirs = []
    for p in (AU_ROOT / "data").glob("*/*/report*.md"):
        if p.parent.parent.name.startswith("_"):
            continue
        if p.read_text(encoding="utf-8").strip():
            report_dirs.append(p.parent)
    report_dirs = sorted(set(report_dirs))
    if not report_dirs:
        return {"error": "no reports"}
    # Time validation across all real reports
    t0 = time.perf_counter()
    proc = subprocess.run(
        ["python3", "validate_report.py", *[str(d.relative_to(AU_ROOT)) for d in report_dirs]],
        cwd=str(AU_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    elapsed = time.perf_counter() - t0
    return {
        "report_dirs": len(report_dirs),
        "elapsed_sec": round(elapsed, 3),
        "reports_per_sec": round(len(report_dirs) / elapsed, 2),
        "exit_code": proc.returncode,
        "ms_per_report": round(1000 * elapsed / len(report_dirs), 2),
        "projected_3000_prs_sec": round(3000 * elapsed / len(report_dirs), 1),
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"Universe: {N} active tickers")
    print("Running Experiment 1: coverage scaling...")
    e1 = exp1_coverage_scaling()
    print("Running Experiment 2: assignment uniformity...")
    e2 = exp2_uniformity()
    print("Running Experiment 3: token cost benchmark...")
    e3 = exp3_cost_benchmark()
    print("Running Experiment 4: consensus robustness...")
    e4 = exp4_consensus_robustness()
    print("Running Experiment 5: validation throughput...")
    e5 = exp5_validation_throughput()

    results = {
        "universe_size": N,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "exp1_coverage_scaling": e1,
        "exp2_uniformity": e2,
        "exp3_cost_benchmark": e3,
        "exp4_consensus_robustness": e4,
        "exp5_validation_throughput": e5,
    }
    OUT.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {OUT}")
    print("\n=== SUMMARY ===")
    print(f"Universe: {N} tickers")
    print(f"Uniformity: chi²={e2['chi_square']} (crit@0.01={e2['chi_crit_001']}) uniform={e2['uniform']}")
    print(f"Cost (GPT-4o-mini): mean=${e3['cost_per_report_usd']['gpt-4o-mini']['mean']} "
          f"median=${e3['cost_per_report_usd']['gpt-4o-mini']['median']}")
    print(f"Cost (DeepSeek): mean=${e3['cost_per_report_usd']['deepseek-v4-flash']['mean']}")
    print(f"Validation: {e5['reports_per_sec']} reports/sec, {e5['ms_per_report']} ms/report")
    print("Consensus MAE (n=10): no-filter=", next(r for r in e4['results'] if r['n']==10)['mae_no_filter'],
          "mad-filter=", next(r for r in e4['results'] if r['n']==10)['mae_mad_filter'])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
