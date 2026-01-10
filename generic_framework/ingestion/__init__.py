"""
Ingestion module for pattern extractor.

Scrapes and parses content from various sources.
"""

from .scraper import URLScraper, DomainScraper

__all__ = ['URLScraper', 'DomainScraper']
