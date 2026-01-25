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
Diagnostics module for EEFrame.

Provides search quality analysis, pattern health checks, and system diagnostics.
"""

from .search_metrics import SearchMetrics, SearchTrace
from .pattern_analyzer import PatternAnalyzer, PatternHealthReport
from .health_checker import HealthChecker, SystemHealthReport
from .self_test import SelfTestRunner, TestCase, TestResult, TestSuiteResult

__all__ = [
    'SearchMetrics',
    'SearchTrace',
    'PatternAnalyzer',
    'PatternHealthReport',
    'HealthChecker',
    'SystemHealthReport',
    'SelfTestRunner',
    'TestCase',
    'TestResult',
    'TestSuiteResult',
]
