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
