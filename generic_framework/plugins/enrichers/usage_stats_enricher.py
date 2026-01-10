"""
Usage Stats Enricher Plugin

Adds usage statistics and feedback information to patterns.
Tracks how often patterns are used and their success rates.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.enrichment_plugin import EnrichmentPlugin, EnrichmentContext


class UsageStatsEnricher(EnrichmentPlugin):
    """
    Adds usage statistics to patterns.

    Simulates usage tracking data:
    - Usage count
    - Success rate
    - Last used timestamp
    - User ratings
    - Common variations

    Configuration:
        - simulate_data: bool (default: true) - Generate realistic mock data
        - include_ratings: bool (default: true) - Include user ratings
        - include_variations: bool (default: true) - Include common variations
    """

    name = "Usage Stats Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.simulate_data = self.config.get("simulate_data", True)
        self.include_ratings = self.config.get("include_ratings", True)
        self.include_variations = self.config.get("include_variations", True)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Add usage stats to patterns."""
        patterns = response_data.get("patterns", [])
        if not patterns:
            return response_data

        enriched_patterns = []
        for pattern in patterns:
            enriched = pattern.copy()

            # Add usage statistics
            stats = await self._get_usage_stats(pattern, context)
            if stats:
                enriched["usage_stats"] = stats

            # Add ratings if enabled
            if self.include_ratings:
                ratings = self._generate_ratings(pattern)
                if ratings:
                    enriched["ratings"] = ratings

            # Add common variations if enabled
            if self.include_variations:
                variations = self._generate_variations(pattern)
                if variations:
                    enriched["common_variations"] = variations

            enriched_patterns.append(enriched)

        response_data["patterns"] = enriched_patterns
        return response_data

    async def _get_usage_stats(
        self,
        pattern: Dict[str, Any],
        context: EnrichmentContext
    ) -> Optional[Dict[str, Any]]:
        """Generate usage statistics for a pattern."""
        if not self.simulate_data:
            return None

        pattern_id = pattern.get("id") or pattern.get("pattern_id", "")

        # Simulate usage data based on pattern characteristics
        base_usage = random.randint(10, 500)

        # Patterns with more examples tend to be used more
        example_count = len(pattern.get("examples", []))
        usage_multiplier = 1 + (example_count * 0.1)

        # Calculate final stats
        total_uses = int(base_usage * usage_multiplier)

        # Success rate (weighted by pattern quality indicators)
        base_success = random.uniform(0.75, 0.98)

        # Patterns with clear descriptions have higher success
        if pattern.get("description"):
            base_success += 0.02

        # Patterns with steps have higher success
        if pattern.get("steps"):
            base_success += 0.03

        success_rate = min(0.99, base_success)

        # Last used (recent patterns used more recently)
        days_ago = random.randint(1, 365)
        last_used = datetime.now() - timedelta(days=days_ago)

        # Average time to apply (in minutes)
        complexity = pattern.get("type", "")
        if complexity in ["algorithm", "technique"]:
            avg_time = random.randint(15, 60)
        elif complexity in ["pattern", "design"]:
            avg_time = random.randint(30, 120)
        else:
            avg_time = random.randint(5, 30)

        return {
            "total_uses": total_uses,
            "success_rate": round(success_rate, 3),
            "last_used": last_used.isoformat(),
            "days_since_last_use": days_ago,
            "avg_time_to_apply_minutes": avg_time,
            "trend": self._generate_trend(total_uses, days_ago)
        }

    def _generate_trend(self, total_uses: int, days_ago: int) -> str:
        """Generate trend indicator."""
        if days_ago < 7:
            return "hot"  # Recently used
        elif days_ago < 30:
            return "stable"
        elif total_uses > 100:
            return "classic"
        else:
            return "declining"

    def _generate_ratings(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user rating data."""
        # Number of ratings (correlated with usage)
        num_ratings = random.randint(5, 50)

        # Average rating (weighted by pattern quality)
        base_rating = random.uniform(3.5, 5.0)

        # Adjust based on pattern characteristics
        if pattern.get("solution"):
            base_rating += 0.1
        if pattern.get("examples"):
            base_rating += 0.1
        if pattern.get("steps"):
            base_rating += 0.05

        avg_rating = min(5.0, base_rating)

        # Rating distribution
        distribution = self._generate_rating_distribution(avg_rating, num_ratings)

        return {
            "average": round(avg_rating, 1),
            "count": num_ratings,
            "distribution": distribution,
            "recent_rating": round(random.uniform(3.0, 5.0), 1)
        }

    def _generate_rating_distribution(self, avg: float, count: int) -> Dict[str, int]:
        """Generate rating distribution (1-5 stars)."""
        distribution = {}

        # Generate distribution centered around average
        for star in range(5, 0, -1):
            weight = max(0.1, 1.0 - abs(star - avg) / 4.0)
            num = int(count * weight / sum(
                max(0.1, 1.0 - abs(s - avg) / 4.0) for s in range(5, 0, -1)
            ))
            distribution[f"{star}_star"] = num

        return distribution

    def _generate_variations(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate common pattern variations."""
        pattern_name = pattern.get("name", "").lower()
        pattern_type = pattern.get("type", "")

        variations = []

        # Common variations based on pattern type
        if pattern_type == "algorithm":
            variations.append({
                "name": "Optimized version",
                "description": "Time-optimized implementation",
                "usage_percent": random.randint(20, 40)
            })
            variations.append({
                "name": "Space-optimized version",
                "description": "Memory-efficient implementation",
                "usage_percent": random.randint(10, 30)
            })

        elif pattern_type == "technique":
            variations.append({
                "name": "Alternative approach",
                "description": "Different method to achieve same result",
                "usage_percent": random.randint(15, 35)
            })

        # Add language-specific variations
        for lang in ["Python", "JavaScript", "Java"]:
            if random.random() > 0.5:
                variations.append({
                    "name": f"{lang} implementation",
                    "description": f"Language-specific version",
                    "usage_percent": random.randint(5, 25)
                })

        return variations[:4]  # Limit variations


class TrendingEnricher(EnrichmentPlugin):
    """
    Adds trending information to patterns.

    Shows which patterns are currently popular,
    rising, or declining in usage.
    """

    name = "Trending Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.time_window_days = self.config.get("time_window_days", 30)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Add trending information."""
        # Add overall trending info to response
        patterns = response_data.get("patterns", [])

        if not patterns:
            return response_data

        # Mark patterns as trending if applicable
        enriched_patterns = []
        for pattern in patterns:
            enriched = pattern.copy()

            trending = self._check_trending(pattern)
            if trending:
                enriched["trending"] = trending

            enriched_patterns.append(enriched)

        response_data["patterns"] = enriched_patterns

        # Add trending summary
        response_data["trending_summary"] = self._generate_trending_summary(
            enriched_patterns
        )

        return response_data

    def _check_trending(self, pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if pattern is trending."""
        # Simulate trending check
        if random.random() > 0.3:  # 30% chance of being trending
            return None

        trend_types = ["rising", "hot", "viral", "stable", "declining"]
        trend_type = random.choice(trend_types)

        # Generate trend data
        return {
            "status": trend_type,
            "rank": random.randint(1, 100),
            "change_percent": random.randint(-50, 200),
            "period_days": self.time_window_days
        }

    def _generate_trending_summary(self, patterns: List[Dict]) -> Dict[str, Any]:
        """Generate overall trending summary."""
        trending = [p for p in patterns if "trending" in p]

        if not trending:
            return {}

        rising = len([p for p in trending if p["trending"]["status"] == "rising"])
        hot = len([p for p in trending if p["trending"]["status"] == "hot"])

        return {
            "total_trending": len(trending),
            "rising_count": rising,
            "hot_count": hot,
            "top_pattern": trending[0].get("name") if trending else None
        }


class FeedbackEnricher(EnrichmentPlugin):
    """
    Adds user feedback to patterns.

    Shows user comments, suggestions, and improvements.
    """

    name = "Feedback Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_comments = self.config.get("max_comments", 3)
        self.include_suggestions = self.config.get("include_suggestions", True)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Add user feedback to patterns."""
        patterns = response_data.get("patterns", [])
        if not patterns:
            return response_data

        enriched_patterns = []
        for pattern in patterns:
            enriched = pattern.copy()

            # Add user comments
            comments = self._generate_comments(pattern)
            if comments:
                enriched["user_comments"] = comments[:self.max_comments]

            # Add suggestions
            if self.include_suggestions:
                suggestions = self._generate_suggestions(pattern)
                if suggestions:
                    enriched["suggested_improvements"] = suggestions

            enriched_patterns.append(enriched)

        response_data["patterns"] = enriched_patterns
        return response_data

    def _generate_comments(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate user comments."""
        comments = []

        # Sample comment templates
        templates = [
            "This pattern saved me hours of work!",
            "Very clear explanation, thanks.",
            "Used this in production, works great.",
            "Would be helpful to have more examples.",
            "The step-by-step approach is perfect.",
            "I modified this slightly for my use case."
        ]

        num_comments = random.randint(1, 5)

        for i in range(num_comments):
            days_ago = random.randint(1, 180)
            comments.append({
                "text": random.choice(templates),
                "author": f"user_{random.randint(1000, 9999)}",
                "date": (datetime.now() - timedelta(days=days_ago)).isoformat(),
                "upvotes": random.randint(0, 50)
            })

        # Sort by upvotes
        comments.sort(key=lambda c: c["upvotes"], reverse=True)
        return comments

    def _generate_suggestions(self, pattern: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []

        # Check for missing elements
        if not pattern.get("examples"):
            suggestions.append("Add more practical examples")

        if not pattern.get("steps"):
            suggestions.append("Include step-by-step instructions")

        if not pattern.get("code_examples"):
            suggestions.append("Add code snippets in popular languages")

        # Random additional suggestions
        random_suggestions = [
            "Add performance comparison",
            "Include edge case handling",
            "Add troubleshooting section",
            "Provide alternative implementations",
            "Link to related patterns"
        ]

        if random.random() > 0.5:
            suggestions.append(random.choice(random_suggestions))

        return suggestions


class QualityScoreEnricher(EnrichmentPlugin):
    """
    Calculates and adds quality scores to patterns.

    Quality based on:
    - Completeness (has examples, steps, code)
    - Clarity (description, structure)
    - Popularity (usage, ratings)
    - Recency (last updated)
    """

    name = "Quality Score Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Add quality scores to patterns."""
        patterns = response_data.get("patterns", [])
        if not patterns:
            return response_data

        enriched_patterns = []
        for pattern in patterns:
            enriched = pattern.copy()

            # Calculate quality score
            score = self._calculate_quality_score(pattern)
            enriched["quality_score"] = score

            enriched_patterns.append(enriched)

        response_data["patterns"] = enriched_patterns
        return response_data

    def _calculate_quality_score(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality score for a pattern."""
        scores = {
            "completeness": 0.0,
            "clarity": 0.0,
            "popularity": 0.0,
            "overall": 0.0
        }

        # Completeness (40%)
        if pattern.get("description"):
            scores["completeness"] += 0.25
        if pattern.get("solution"):
            scores["completeness"] += 0.30
        if pattern.get("examples"):
            scores["completeness"] += 0.25
        if pattern.get("steps") or pattern.get("code_examples"):
            scores["completeness"] += 0.20

        # Clarity (30%)
        if pattern.get("description") and len(pattern.get("description", "")) > 50:
            scores["clarity"] += 0.40
        if pattern.get("problem"):
            scores["clarity"] += 0.30
        if pattern.get("tags"):
            scores["clarity"] += 0.30

        # Popularity (30%)
        usage_stats = pattern.get("usage_stats", {})
        if usage_stats:
            # Normalize usage count (0-100 uses: 0.0-0.5, 100+: 0.5-1.0)
            uses = usage_stats.get("total_uses", 0)
            if uses > 0:
                scores["popularity"] += min(0.5, uses / 200)
            # Success rate
            success = usage_stats.get("success_rate", 0)
            scores["popularity"] += success * 0.5

        # Overall score
        scores["overall"] = (
            scores["completeness"] * 0.4 +
            scores["clarity"] * 0.3 +
            scores["popularity"] * 0.3
        )

        # Round and add grade
        scores["overall"] = round(scores["overall"], 2)
        scores["grade"] = self._score_to_grade(scores["overall"])

        return scores

    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
