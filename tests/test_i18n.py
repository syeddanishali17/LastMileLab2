"""Frontend copy tables stay in lockstep."""

import i18n
from display import format_km, format_pct, humanize_check_message, status_label
from i18n import STRINGS, t


def test_english_and_german_keys_match() -> None:
    assert set(STRINGS["en"]) == set(STRINGS["de"])


def test_status_badge_copy_is_human() -> None:
    assert status_label("passed") == "Pre-checks passed"


def test_user_facing_copy_avoids_em_dashes() -> None:
    for language in STRINGS.values():
        assert all("—" not in value for value in language.values())


def test_german_number_formatting(monkeypatch) -> None:
    monkeypatch.setattr(i18n, "current_language", lambda: "de")
    assert format_km(30101) == "30,101 km"
    assert format_pct(0.967) == "96,7 %"


def test_check_three_message_is_plain() -> None:
    text = humanize_check_message(
        {
            "code": "CHECK_3",
            "passed": True,
            "message": (
                "minimum vehicles by aggregate demand = 4 "
                "(informational; not a feasibility proof)"
            ),
        }
    )
    assert "4" in text
    assert "informational" not in text
    assert t("check.msg.minvans", n=4) == text
