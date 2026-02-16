import re

import pytest

from src.bot import DraftingBot


def test_twitter_effective_length_counts_urls_as_tco():
    bot = DraftingBot()
    rules = bot.platforms["twitter"]

    text = "Check this https://example.com/abc and this http://test.com/x"
    eff = bot._effective_length(text, "twitter", rules)

    # effective = non-url chars + (num_urls * tco_url_length)
    url_re = re.compile(r"https?://\S+")
    urls = list(url_re.finditer(text))
    non_url_len = len(text) - sum(len(m.group(0)) for m in urls)
    expected = non_url_len + len(urls) * rules["tco_url_length"]
    assert eff == expected


def test_trim_to_platform_effective_respects_effective_budget_with_urls():
    bot = DraftingBot()
    rules = bot.platforms["twitter"]

    # Make long text where raw length != effective length due to URL counting.
    text = (
        "A" * 50
        + " https://example.com/some/really/long/path/that/should/count_fixed "
        + "B" * 50
    )

    max_len = 40
    rules = {**rules, "max_length": max_len}

    trimmed = bot._trim_to_platform_effective(text, "twitter", rules, ellipsis="...")

    # Must satisfy effective length constraint.
    assert bot._effective_length(trimmed, "twitter", rules) <= max_len
    assert trimmed.endswith("...")


def test_instagram_hashtag_enforcement_only_removes_when_enforce_true():
    bot = DraftingBot()
    rules = bot.platforms["instagram"]

    # Build 35 hashtags; limit is 30.
    tags = " ".join([f"#t{i}" for i in range(35)])
    text = f"hello {tags} bye"

    kept, warnings_no_enforce = bot._apply_platform_rules(text, "instagram", rules, enforce=False)
    assert kept == text
    assert any("hashtag limit exceeded" in w.lower() for w in warnings_no_enforce)

    enforced, warnings_enforce = bot._apply_platform_rules(text, "instagram", rules, enforce=True)
    assert enforced != text
    remaining_tags = re.findall(r"(?<!\w)#\w+", enforced)
    assert len(remaining_tags) == rules["hashtag_limit"]
    assert any("removed" in w.lower() for w in warnings_enforce)


def test_linkedin_normalizes_line_breaks():
    bot = DraftingBot()
    rules = bot.platforms["linkedin"]

    raw = "line1\r\nline2\rline3\nline4"
    processed, _warnings = bot._apply_platform_rules(raw, "linkedin", rules, enforce=False)

    assert "\r" not in processed
    assert processed == "line1\nline2\nline3\nline4"
