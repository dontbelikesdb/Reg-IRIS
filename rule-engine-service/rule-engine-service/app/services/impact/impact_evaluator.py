"""Runs every trade through every rule of the selected regulators."""
from __future__ import annotations

from collections import Counter

from app.schemas.impact import (
    ImpactReport, RegulatorSummary, ReportSummary, RuleFailureCount,
    RuleViolation, TradeResult, RuleRef
)

from app.schemas.internal import Rule, RuleSet
from app.services.impact.trade_loader import ParsedTrades, Trade
from app.services.rules.explanation_builder import explain_failure
from app.services.rules.json_logic_evaluator import (
    EvaluationError, collect_fields, evaluate, extract_fields,
)


def _violation(rs: RuleSet, rule: Rule, explanation: str, evidence: dict) -> RuleViolation:
    return RuleViolation(
        regulator_id=rs.id,
        regulator=rs.name,
        rule_id=rule.id,
        description=rule.description,
        impact=rule.impact,
        explanation=explanation,
        evidence=evidence,
    )


def evaluate_trade(trade: Trade, rulesets: list[RuleSet]) -> TradeResult:
    violations: list[RuleViolation] = []
    regulator_status: dict[str, str] = {}

    for rs in rulesets:
        failed = False
        for rule in rs.rules:
            try:
                trace = evaluate(rule.logic, trade.data)
            except EvaluationError as exc:
                failed = True
                violations.append(_violation(rs, rule, f"Rule could not be evaluated: {exc}", {}))
                continue
            if trace.truthy:
                continue
            failed = True
            violations.append(_violation(rs, rule, explain_failure(trace), collect_fields(trace)))
        regulator_status[rs.id] = "FAIL" if failed else "PASS"

    return TradeResult(
        row_number=trade.row_number,
        trade_id=trade.raw.get("Trade_ID") or f"ROW-{trade.row_number}",
        status="FAIL" if violations else "PASS",
        trade=trade.raw,
        regulator_status=regulator_status,
        violations=violations,
    )


def _missing_column_warnings(columns: list[str], rulesets: list[RuleSet]) -> list[str]:
    used_by: dict[str, list[str]] = {}
    for rs in rulesets:
        for rule in rs.rules:
            for f in extract_fields(rule.logic):
                if f not in columns:
                    used_by.setdefault(f, []).append(rule.id)
    return [
        f"Column '{f}' isn't in the CSV, so rules {', '.join(ids)} will treat it as empty."
        for f, ids in sorted(used_by.items())
    ]


def build_report(parsed: ParsedTrades, rulesets: list[RuleSet]) -> ImpactReport:
    results = [evaluate_trade(t, rulesets) for t in parsed.trades]

    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")

    by_regulator = []
    for rs in rulesets:
        ok = sum(1 for r in results if r.regulator_status.get(rs.id) == "PASS")
        by_regulator.append(
            RegulatorSummary(
                regulator_id=rs.id, name=rs.name, rules_checked=len(rs.rules),
                passed=ok, failed=total - ok,
            )
        )

    counts: Counter = Counter()
    descriptions: dict[tuple[str, str], str] = {}
    for r in results:
        for v in r.violations:
            key = (v.regulator_id, v.rule_id)
            counts[key] += 1
            descriptions[key] = v.description
    rule_failures = [
        RuleFailureCount(regulator_id=k[0], rule_id=k[1], description=descriptions[k], failures=n)
        for k, n in counts.most_common()
    ]

    return ImpactReport(
        summary=ReportSummary(
            total_trades=total,
            passed=passed,
            failed=total - passed,
            pass_rate=round(passed / total * 100, 2) if total else 0.0,
            by_regulator=by_regulator,
            rule_failures=rule_failures,
        ),
        columns=parsed.columns,
        regulators_checked=[rs.id for rs in rulesets],
        rules_checked=[                                                    # <- new
            RuleRef(regulator_id=rs.id, rule_id=r.id, description=r.description)
            for rs in rulesets
            for r in rs.rules
        ],
        warnings=_missing_column_warnings(parsed.columns, rulesets),
        results=results,
    )
