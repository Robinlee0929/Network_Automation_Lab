import argparse
from pathlib import Path

import pytest

import network_lab
from network_lab_task_registry import (
    CANONICAL_TASK_NAMES,
    TASK_ALIASES,
    UnknownTaskError,
    get_cli_task_choices,
    resolve_task_handler,
    resolve_task_name,
)


def _handler_args() -> argparse.Namespace:
    return argparse.Namespace(
        profile=str(network_lab.DEFAULT_PROFILE),
        dry_run=True,
        intent_text="show latest reports",
        allow_live_wireguard=False,
        wireguard_config=network_lab.DAY12_WIREGUARD_CONFIG,
        run_iperf=False,
    )


def test_canonical_task_resolution_returns_same_name():
    assert resolve_task_name("reviewer-evidence-intake-outcome-ledger") == (
        "reviewer-evidence-intake-outcome-ledger"
    )
    assert resolve_task_name("report-index") == "report-index"


def test_alias_resolution_returns_canonical_task_name():
    assert resolve_task_name("deferred-evidence-collection-log") == (
        "reviewer-evidence-intake-outcome-ledger"
    )
    assert resolve_task_name("broker-review-queue-decision-state") == "broker-review-queue"


def test_unknown_task_rejection():
    with pytest.raises(UnknownTaskError):
        resolve_task_name("unknown-network-lab-task")


def test_handler_lookup_returns_callable_for_canonical_and_alias_tasks():
    calls = []
    handlers = {
        "reviewer-evidence-intake-outcome-ledger": lambda: calls.append("day119") or 0,
    }

    canonical = resolve_task_handler("reviewer-evidence-intake-outcome-ledger", handlers)
    alias = resolve_task_handler("deferred-evidence-collection-log", handlers)

    assert canonical.canonical_name == "reviewer-evidence-intake-outcome-ledger"
    assert canonical.is_alias is False
    assert alias.canonical_name == "reviewer-evidence-intake-outcome-ledger"
    assert alias.is_alias is True
    assert callable(canonical.handler)
    assert callable(alias.handler)
    assert alias.handler() == 0
    assert calls == ["day119"]


def test_network_lab_registers_callable_handlers_for_all_canonical_tasks():
    handlers = network_lab._build_task_handlers(_handler_args(), Path.cwd())

    assert set(handlers) == set(CANONICAL_TASK_NAMES)
    assert all(callable(handler) for handler in handlers.values())


def test_cli_choices_preserve_catalog_tasks_and_aliases():
    catalog_ids = {task["id"] for task in network_lab.list_tasks()}
    choices = get_cli_task_choices()

    assert set(CANONICAL_TASK_NAMES).issubset(catalog_ids)
    assert set(CANONICAL_TASK_NAMES).issubset(set(choices))
    assert set(TASK_ALIASES).issubset(set(choices))
    for alias_name, canonical_name in TASK_ALIASES.items():
        assert alias_name not in CANONICAL_TASK_NAMES
        assert canonical_name in catalog_ids
        assert choices.index(alias_name) == choices.index(canonical_name) + 1
