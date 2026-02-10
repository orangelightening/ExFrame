"""
Tests for Phase 1: Persona + Override System

Simple tests to verify the Phase 1 architecture works correctly.
"""

import pytest
from generic_framework.core.persona import Persona
from generic_framework.core.personas import get_persona, list_personas
from generic_framework.core.query_processor import process_query


class TestPersona:
    """Test Persona class"""

    def test_create_poet(self):
        """Can create poet persona"""
        poet = Persona(name="poet", data_source="void")
        assert poet.name == "poet"
        assert poet.data_source == "void"

    def test_create_librarian(self):
        """Can create librarian persona"""
        librarian = Persona(name="librarian", data_source="library")
        assert librarian.name == "librarian"
        assert librarian.data_source == "library"

    def test_create_researcher(self):
        """Can create researcher persona"""
        researcher = Persona(name="researcher", data_source="internet")
        assert researcher.name == "researcher"
        assert researcher.data_source="internet"

    def test_invalid_data_source(self):
        """Invalid data source raises error"""
        with pytest.raises(ValueError):
            Persona(name="test", data_source="invalid")

    def test_respond_with_override(self):
        """Persona uses patterns when provided"""
        poet = Persona(name="poet", data_source="void")

        patterns = [
            {"name": "Test Pattern", "solution": "Test solution"}
        ]

        response = poet.respond("test query", override_patterns=patterns)

        assert response["source"] == "patterns_override"
        assert response["persona"] == "poet"
        assert response["pattern_count"] == 1

    def test_respond_without_override(self):
        """Persona uses data source when no patterns"""
        poet = Persona(name="poet", data_source="void")

        response = poet.respond("test query")

        assert response["source"] == "void"
        assert response["persona"] == "poet"
        assert response["pattern_count"] == 0


class TestPersonas:
    """Test personas module"""

    def test_get_poet(self):
        """Can get poet persona"""
        poet = get_persona("poet")
        assert poet.name == "poet"
        assert poet.data_source == "void"

    def test_get_librarian(self):
        """Can get librarian persona"""
        librarian = get_persona("librarian")
        assert librarian.name == "librarian"
        assert librarian.data_source == "library"

    def test_get_researcher(self):
        """Can get researcher persona"""
        researcher = get_persona("researcher")
        assert researcher.name == "researcher"
        assert researcher.data_source == "internet"

    def test_get_invalid_persona(self):
        """Invalid persona raises error"""
        with pytest.raises(ValueError):
            get_persona("invalid")

    def test_list_personas(self):
        """Can list all personas"""
        personas = list_personas()
        assert len(personas) == 3
        assert "poet" in personas
        assert "librarian" in personas
        assert "researcher" in personas


class TestQueryProcessor:
    """Test query processor with pattern override"""

    def test_process_query_basic(self):
        """Can process a basic query"""
        # This will use default config if domain doesn't exist
        response = process_query("test query", "test_domain")

        assert "answer" in response
        assert "source" in response
        assert "persona" in response
        assert "domain" in response
        assert response["domain"] == "test_domain"

    def test_process_query_cooking_domain(self):
        """Can process query for cooking domain"""
        response = process_query("How to cook rice", "cooking")

        assert response["domain"] == "cooking"
        assert response["persona_type"] == "researcher"
        assert "answer" in response


class TestCoreDecision:
    """Test the core decision tree: patterns or data source"""

    def test_decision_with_patterns(self):
        """When patterns provided, uses patterns_override"""
        poet = Persona(name="poet", data_source="void")

        patterns = [{"name": "P1", "solution": "S1"}]
        response = poet.respond("test", override_patterns=patterns)

        assert response["source"] == "patterns_override"

    def test_decision_without_patterns(self):
        """When no patterns, uses data source"""
        poet = Persona(name="poet", data_source="void")

        response = poet.respond("test")

        assert response["source"] == "void"

    def test_decision_empty_patterns(self):
        """When empty patterns list, uses data source"""
        poet = Persona(name="poet", data_source="void")

        response = poet.respond("test", override_patterns=[])

        # Empty list is falsy, should use data source
        assert response["source"] == "void"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
