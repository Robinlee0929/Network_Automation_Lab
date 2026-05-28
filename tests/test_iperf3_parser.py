import pytest

import performance_test as day8


def test_parse_sum_received_bits_per_second():
    parsed = day8.parse_iperf3_json(
        {"end": {"sum_received": {"bits_per_second": 946_000_000}}}
    )

    assert parsed["throughput_mbps"] == 946.0
    assert parsed["source_field"] == "end.sum_received.bits_per_second"


def test_fallback_parse_sum_sent_bits_per_second():
    parsed = day8.parse_iperf3_json(
        {"end": {"sum_sent": {"bits_per_second": 812_500_000}}}
    )

    assert parsed["throughput_mbps"] == 812.5
    assert parsed["source_field"] == "end.sum_sent.bits_per_second"


def test_mbps_conversion_is_decimal_mbps():
    parsed = day8.parse_iperf3_json(
        {"end": {"sum_received": {"bits_per_second": 1_234_567_890}}}
    )

    assert parsed["throughput_mbps"] == 1234.56789


def test_missing_required_fields_has_clear_error():
    with pytest.raises(ValueError, match="missing end.sum_received.bits_per_second"):
        day8.parse_iperf3_json({"end": {"cpu_utilization_percent": {}}})
