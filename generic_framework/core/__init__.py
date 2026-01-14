"""
Generic Framework - Core Abstractions

Domain-agnostic assistant framework for expertise management.
"""

from .domain import Domain, DomainConfig, CollectorType
from .collector import Collector, CollectorConfig
from .specialist import Specialist, SpecialistConfig
from .knowledge_base import KnowledgeBase, KnowledgeBaseConfig
from .factory import DomainFactory
from .specialist_plugin import SpecialistPlugin

# Note: GenericDomain is not exported here to avoid circular import
# with knowledge.json_kb. Import it directly when needed:
# from core.generic_domain import GenericDomain

__all__ = [
    'Domain',
    'DomainConfig',
    'CollectorType',
    'Collector',
    'CollectorConfig',
    'Specialist',
    'SpecialistConfig',
    'KnowledgeBase',
    'KnowledgeBaseConfig',
    'DomainFactory',
    'SpecialistPlugin',
]
