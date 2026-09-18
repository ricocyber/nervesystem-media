from virality.ollama_brain import Idea


def test_idea_schema_is_explicit():
    idea = Idea(
        idea_id="I001",
        concept="What happens when an AI can move money?",
        hook="An AI agent can now initiate a payment.",
        stakes="Bad authorization can create direct financial loss.",
        target_viewer="business owners",
        funnel_stage="discovery",
        recommended_format="longform",
    )
    assert idea.idea_id == "I001"
    assert "money" in idea.concept.lower()
