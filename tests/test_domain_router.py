"""Tests for domain_router.py — AI-primary routing, folder matching, and heuristic fallback."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from domain_router import (
    _build_routing_prompt,
    _propose_new_major_domain,
    build_routing_context,
    clear_folder_cache,
    collect_folder_summaries,
    discover_domain_tree,
    infer_domain,
    infer_domain_decision,
    infer_domain_with_ai,
    load_routing_guide,
    load_routing_policy,
    load_routing_skill,
    match_existing_folders,
    match_route,
)


class TestDiscoverDomainTree(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        (self.root / "operations-research").mkdir()
        (self.root / "operations-research" / "inventory-planning").mkdir()
        (self.root / "operations-research" / "knowledge-root-card.md").write_text("---\nid: root\n---\n", encoding="utf-8")
        (self.root / "llm").mkdir()
        (self.root / "llm" / "mixture-of-experts").mkdir()
        (self.root / "general").mkdir()
        (self.root / ".hidden").mkdir()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_discovers_major_and_subdomain_levels(self):
        domain_tree = discover_domain_tree(self.root)
        self.assertIn("operations-research", domain_tree)
        self.assertIn("inventory-planning", domain_tree["operations-research"])
        self.assertIn("", domain_tree["operations-research"])
        self.assertIn("llm", domain_tree)
        self.assertIn("mixture-of-experts", domain_tree["llm"])
        self.assertIn("general", domain_tree)

    def test_excludes_hidden_dirs(self):
        domain_tree = discover_domain_tree(self.root)
        self.assertNotIn(".hidden", domain_tree)

    def test_returns_empty_for_missing_root(self):
        self.assertEqual(discover_domain_tree(Path("/nonexistent")), {})


class TestMatchExistingFolders(unittest.TestCase):
    """Test the zero-config folder-name matching (Tier 2)."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        (self.root / "operations-research").mkdir()
        (self.root / "operations-research" / "inventory-planning").mkdir()
        (self.root / "llm").mkdir()
        (self.root / "llm" / "mixture-of-experts").mkdir()
        self.domain_tree = discover_domain_tree(self.root)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_matches_subdomain_by_name(self):
        self.assertEqual(
            match_existing_folders("inventory planning basics", self.domain_tree),
            ("operations-research", "inventory-planning"),
        )

    def test_matches_major_domain_by_name(self):
        self.assertEqual(
            match_existing_folders("operations research optimization", self.domain_tree),
            ("operations-research", None),
        )

    def test_matches_mixture_of_experts(self):
        self.assertEqual(
            match_existing_folders("mixture of experts routing", self.domain_tree),
            ("llm", "mixture-of-experts"),
        )

    def test_no_match_returns_none(self):
        self.assertIsNone(match_existing_folders("renaissance painting basics", self.domain_tree))


class TestMatchRouteLegacy(unittest.TestCase):
    """Test the legacy policy-based match_route (kept for user overrides)."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        (self.root / "operations-research").mkdir()
        (self.root / "operations-research" / "inventory-planning").mkdir()
        (self.root / "llm").mkdir()
        (self.root / "llm" / "mixture-of-experts").mkdir()
        self.policy = load_routing_policy()
        self.domain_tree = discover_domain_tree(self.root)

    def tearDown(self):
        self.tmpdir.cleanup()

    @unittest.skipUnless(load_routing_policy(), "Requires domain_routing_policy.json")
    def test_matches_inventory_planning_via_alias(self):
        self.assertEqual(
            match_route("安全库存和再订货点怎么理解", self.policy, self.domain_tree),
            ("operations-research", "inventory-planning"),
        )

    @unittest.skipUnless(load_routing_policy(), "Requires domain_routing_policy.json")
    def test_matches_major_root_when_no_specific_subdomain(self):
        self.assertEqual(
            match_route("运筹学优化建模基础", self.policy, self.domain_tree),
            ("operations-research", None),
        )


class TestInferDomain(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        (self.root / "operations-research").mkdir()
        (self.root / "operations-research" / "inventory-planning").mkdir()
        (self.root / "general").mkdir()

    def tearDown(self):
        clear_folder_cache()
        self.tmpdir.cleanup()

    def test_matches_existing_folder_by_name(self):
        slug, path = infer_domain("inventory planning framework", self.root, use_ai_fallback=False)
        self.assertEqual(slug, "operations-research/inventory-planning")
        self.assertEqual(path, self.root / "operations-research" / "inventory-planning")

    def test_falls_back_to_new_major_root(self):
        slug, path = infer_domain("quantum entanglement", self.root, use_ai_fallback=False)
        self.assertEqual(slug, "quantum-entanglement")
        self.assertEqual(path, self.root / "quantum-entanglement")

    def test_creates_general_if_missing(self):
        root2 = Path(tempfile.mkdtemp())
        try:
            slug, path = infer_domain("unknown topic", root2, use_ai_fallback=False)
            self.assertEqual(slug, "unknown-topic")
            self.assertTrue(path.exists())
        finally:
            import shutil
            shutil.rmtree(root2)

    def test_uses_ai_fallback_when_available(self):
        with patch("domain_router.infer_domain_with_ai", return_value={"major_domain": "llm", "subdomain": "mixture-of-experts", "reason": "best fit"}):
            slug, path = infer_domain("switch transformer routing", self.root, use_ai_fallback=True)
        self.assertEqual(slug, "llm/mixture-of-experts")
        self.assertTrue(path.exists())

    def test_decision_contains_reason_and_mode_folder_match(self):
        decision = infer_domain_decision("inventory planning basics", self.root, use_ai_fallback=False)
        self.assertEqual(decision["major_domain"], "operations-research")
        self.assertEqual(decision["subdomain"], "inventory-planning")
        self.assertEqual(decision["decision_mode"], "folder_match")

    def test_decision_contains_reason_and_mode_fallback(self):
        decision = infer_domain_decision("quantum entanglement basics", self.root, use_ai_fallback=False)
        self.assertEqual(decision["decision_mode"], "fallback_new_major")

    def test_accepts_card_title_and_summary(self):
        """infer_domain accepts optional card context without error."""
        slug, path = infer_domain(
            "inventory planning", self.root, use_ai_fallback=False,
            card_title="Safety Stock and ROP",
            card_summary="How to calculate safety stock levels",
        )
        self.assertEqual(slug, "operations-research/inventory-planning")


class TestInferDomainWithAi(unittest.TestCase):
    def test_returns_none_without_api_credentials(self):
        with patch("domain_router._router_api_key", return_value=""):
            context = build_routing_context("unknown topic", Path("/nonexistent"))
            self.assertIsNone(infer_domain_with_ai(context))

    def test_uses_openai_compatible_response(self):
        context = build_routing_context(
            "switch transformer routing", Path("/nonexistent"),
            card_title="MoE Routing",
            card_summary="How routing works in mixture of experts",
        )
        with patch("domain_router._call_router_llm", return_value='{"major_domain": "llm", "subdomain": "mixture-of-experts", "reason": "MoE topic"}'):
            route = infer_domain_with_ai(context)
        self.assertEqual(route, {"major_domain": "llm", "subdomain": "mixture-of-experts", "reason": "MoE topic"})

    def test_accepts_new_major_domain_response(self):
        context = build_routing_context("量子纠缠的工程应用", Path("/nonexistent"))
        with patch("domain_router._call_router_llm", return_value='{"major_domain": "quantum-computing", "subdomain": "", "reason": "new domain"}'):
            route = infer_domain_with_ai(context)
        self.assertEqual(route, {"major_domain": "quantum-computing", "subdomain": "", "reason": "new domain"})

    def test_rejects_non_slug_responses(self):
        context = build_routing_context("switch transformer routing", Path("/nonexistent"))
        with patch("domain_router._call_router_llm", return_value='{"major_domain": "llm", "subdomain": "bad slug", "reason": "invalid"}'):
            route = infer_domain_with_ai(context)
        self.assertIsNone(route)


class TestRoutingSkillAndPrompt(unittest.TestCase):
    def test_load_routing_skill(self):
        skill = load_routing_skill()
        self.assertIn("Knowledge Base Routing", skill)
        self.assertIn("major_domain", skill)

    def test_build_prompt_uses_skill_and_context(self):
        context = {
            "query": "安全库存和再订货点怎么理解",
            "card_title": "Safety Stock",
            "card_summary": "How to calculate safety stock",
            "existing_folders": {"operations-research": ["inventory-planning"]},
            "folder_contents": {"operations-research": {"inventory-planning": {"card_count": 3, "titles": ["Safety Stock Basics"]}}},
        }
        system_prompt, user_message = _build_routing_prompt(context)
        self.assertIn("Knowledge Base Routing", system_prompt)
        self.assertIn("安全库存", user_message)
        self.assertIn("Safety Stock", user_message)
        self.assertIn("inventory-planning", user_message)

    def test_load_routing_guide_legacy(self):
        guide = load_routing_guide()
        self.assertIn("Target Structure", guide)

    def test_load_routing_policy_optional(self):
        """Policy loading returns None gracefully if file is missing."""
        with patch("domain_router.POLICY_PATH", Path("/nonexistent/policy.json")):
            self.assertIsNone(load_routing_policy())


class TestNewMajorFallback(unittest.TestCase):
    def test_propose_new_major_domain_from_english_query(self):
        self.assertEqual(_propose_new_major_domain("quantum entanglement basics"), "quantum-entanglement-basics")

    def test_propose_new_major_domain_from_chinese_query(self):
        self.assertEqual(_propose_new_major_domain("量子纠缠的工程应用"), "量子纠缠的工程应用")


class TestFolderSummaries(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        (self.root / "operations-research").mkdir()
        (self.root / "operations-research" / "linear-programming").mkdir()
        (self.root / "operations-research" / "linear-programming" / "card1.md").write_text(
            "---\ntitle: LP Basics\ntags:\n  - lp\n  - simplex\n---\nContent", encoding="utf-8"
        )
        (self.root / "operations-research" / "linear-programming" / "card2.md").write_text(
            "---\ntitle: Duality Theory\ntags:\n  - duality\n---\nContent", encoding="utf-8"
        )
        clear_folder_cache()

    def tearDown(self):
        clear_folder_cache()
        self.tmpdir.cleanup()

    def test_collects_titles_and_tags(self):
        summaries = collect_folder_summaries(self.root)
        lp_summary = summaries.get("operations-research", {}).get("linear-programming")
        self.assertIsNotNone(lp_summary)
        self.assertEqual(lp_summary["card_count"], 2)
        self.assertIn("LP Basics", lp_summary["titles"])
        self.assertIn("Duality Theory", lp_summary["titles"])
        self.assertIn("lp", lp_summary["tags"])
        self.assertIn("duality", lp_summary["tags"])

    def test_empty_folder_has_zero_count(self):
        (self.root / "empty-domain").mkdir()
        clear_folder_cache()
        summaries = collect_folder_summaries(self.root)
        empty = summaries.get("empty-domain", {}).get("")
        self.assertIsNotNone(empty)
        self.assertEqual(empty["card_count"], 0)

    def test_skips_index_files(self):
        (self.root / "operations-research" / "linear-programming" / "_index.md").write_text(
            "---\ntitle: Index\n---\n", encoding="utf-8"
        )
        clear_folder_cache()
        summaries = collect_folder_summaries(self.root)
        lp_summary = summaries["operations-research"]["linear-programming"]
        self.assertEqual(lp_summary["card_count"], 2)  # _index.md not counted


class TestBuildRoutingContext(unittest.TestCase):
    def test_builds_context_with_all_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test-domain").mkdir()
            context = build_routing_context("test query", root, card_title="Test", card_summary="A summary")
            self.assertEqual(context["query"], "test query")
            self.assertEqual(context["card_title"], "Test")
            self.assertEqual(context["card_summary"], "A summary")
            self.assertIn("test-domain", context["existing_folders"])


if __name__ == "__main__":
    unittest.main()
