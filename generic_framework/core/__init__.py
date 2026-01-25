#
# Copyright 2025 ExFrame Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
