import ast
from pathlib import Path

import intent_controlled_ai_runtime_entry as entry


UNSAFE_RUNTIME_REFERENCES = {
    "netmiko",
    "openai",
    "paramiko",
    "pyaudio",
    "pyttsx3",
    "requests",
    "socket",
    "speech_recognition",
    "subprocess",
}


def test_day71_controlled_entry_design_is_static_and_disabled():
    design = entry.get_day71_controlled_entry_design()

    assert design["day"] == 71
    assert design["title"] == "Controlled AI Runtime Prototype Entry Design"
    assert design["safety_stage"] == "design_only"
    assert design["execution_allowed"] is False
    assert design["api_integration_allowed"] is False
    assert design["voice_allowed"] is False
    assert design["device_access_allowed"] is False
    assert design["dashboard_action_surface_allowed"] is False
    assert design["mapped_task_execution_allowed"] is False
    assert design["live_execution_allowed"] is False
    assert design["required_reviewer_gate"] is True


def test_day71_contract_fields_match_required_entry_design():
    design = entry.get_day71_controlled_entry_design()

    input_fields = {item["name"] for item in design["input_contract"]}
    output_fields = {item["name"] for item in design["output_contract"]}
    gate_names = [item["name"] for item in design["safety_gate_sequence"]]
    evidence_days = [item["day"] for item in design["reviewer_evidence_map"]]

    assert input_fields == {
        "user_intent_text",
        "requested_operation_type",
        "target_scope",
        "safety_level",
        "evidence_required",
        "reviewer_required",
        "execution_allowed",
    }
    assert output_fields == {
        "normalized_intent",
        "mapped_category",
        "risk_level",
        "required_evidence",
        "reviewer_decision_required",
        "blocked_reason",
        "next_safe_step",
    }
    assert gate_names == [
        "intent normalization",
        "task classification",
        "blocked-action screening",
        "evidence requirement mapping",
        "offline mock validation",
        "reviewer approval",
        "dry-run report generation",
        "explicit human confirmation",
        "future controlled execution consideration",
    ]
    assert evidence_days == [
        "Day57",
        "Day58",
        "Day59",
        "Day60",
        "Day61",
        "Day62",
        "Day63",
        "Day64",
        "Day65",
        "Day66",
        "Day67",
        "Day68",
        "Day69",
        "Day70",
    ]


def test_day71_module_has_no_unsafe_runtime_imports_or_references():
    source_path = Path(entry.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    source_lower = source.lower()
    assert imported_names.isdisjoint(UNSAFE_RUNTIME_REFERENCES)
    assert all(term not in source_lower for term in UNSAFE_RUNTIME_REFERENCES)
    assert "config.json" not in source_lower
    assert "network_lab" not in source_lower
