"""
Generic Framework - Core Abstractions

Domain-agnostic assistant framework for expertise management.
"""

from .domain import Domain, DomainConfig, CollectorType
from .collector import Collector, CollectorConfig
from .specialist import Specialist, SpecialistConfig
from .knowledge_base import KnowledgeBase, KnowledgeBaseConfig
from .factory import DomainFactory
from .generic_domain import GenericDomain
from .specialist_plugin import SpecialistPlugin

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
    'GenericDomain',
    'SpecialistPlugin',
]
