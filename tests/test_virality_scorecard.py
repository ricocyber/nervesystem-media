import pytest

from virality.scorecard import ViralityScorecard, score_idea


def strong_card(**overrides):
    values = dict(
        core_audience_fit=9,
        casual_audience_fit=9,
        new_audience_fit=8,
        stakes=9,
        curiosity_gap=9,
        hook_promise=9,
        proof_specificity=8,
        title_potential=9,
        thumbnail_potential=9,
        novelty=8,
        timeliness=8,
        production_feasibility=8,
        funnel_fit=9,
        shareability=9,
    )
    values.update(overrides)
    return ViralityScorecard(**values)


def test_strong_idea_produces():
    result = score_idea(strong_card())
    assert result.total >= 85
    assert result.decision == "PRODUCE"


def test_weak_audience_is_killed():
    result = score_idea(
        strong_card(core_audience_fit=4, casual_audience_fit=4, new_audience_fit=4)
    )
    assert result.decision == "KILL"


def test_weak_packaging_is_repackage():
    result = score_idea(
        strong_card(title_potential=4, thumbnail_potential=4)
    )
    assert result.decision == "REPACKAGE"


def test_invalid_value_rejected():
    with pytest.raises(ValueError):
        score_idea(strong_card(stakes=11))
