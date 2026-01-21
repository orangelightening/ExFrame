#!/usr/bin/env python3
"""
Test script for Phase 1: Foundation & Core Infrastructure

Tests:
1. Configuration loading from YAML
2. Logger (console + file output)
3. State persistence (save/load/update)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from autonomous_learning.core.config import load_config, Config
from autonomous_learning.core.logger import get_logger, configure_root_logging, log_event, log_metric
from autonomous_learning.core.state import StateManager, get_state_manager


def test_config():
    """Test 1: Configuration loading"""
    print("\n" + "="*60)
    print("TEST 1: Configuration Loading")
    print("="*60)

    try:
        config = load_config(Path("config/autonomous_learning.yaml"))
        print(f"✓ Config loaded successfully")

        # Verify key values
        assert config.supervisor.model == "glm-4", "Model should be glm-4"
        print(f"✓ Supervisor API: {config.supervisor.api_url}")
        print(f"✓ Supervisor Model: {config.supervisor.model}")

        assert len(config.certification.judges) == 5, "Should have 5 judges"
        print(f"✓ Judges: {len(config.certification.judges)} configured")

        assert config.scraping.pilot_domain == "cooking", "Pilot should be cooking"
        print(f"✓ Pilot Domain: {config.scraping.pilot_domain}")

        assert config.ingestion.dedup_method == "text_based", "Should be text-based"
        print(f"✓ Dedup Method: {config.ingestion.dedup_method}")

        print("\n✓ TEST 1 PASSED: Configuration")
        return True

    except Exception as e:
        print(f"\n✗ TEST 1 FAILED: {e}")
        return False


def test_logger():
    """Test 2: Logger functionality"""
    print("\n" + "="*60)
    print("TEST 2: Logger")
    print("="*60)

    try:
        # Test root logger configuration
        configure_root_logging(level="INFO", log_dir=Path("data/logs"))
        print("✓ Root logger configured")

        # Test component logger
        logger = get_logger("test_component", log_dir=Path("data/logs"))
        print("✓ Component logger created")

        # Test different log levels
        logger.debug("This is a debug message (should only appear in file)")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")

        # Test logging with extra context
        log_event(logger, "test_event", test_field="test_value", number=42)
        print("✓ Structured logging with extra fields")

        # Test metric logging
        log_metric(logger, "test_metric", 0.85)
        print("✓ Metric logging")

        # Verify log file was created
        log_file = Path("data/logs/test_component.log")
        assert log_file.exists(), "Log file should exist"
        print(f"✓ Log file created: {log_file}")

        # Show log file content
        with open(log_file, "r") as f:
            lines = f.readlines()
        print(f"✓ Log file contains {len(lines)} entries")

        print("\n✓ TEST 2 PASSED: Logger")
        return True

    except Exception as e:
        print(f"\n✗ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_state_persistence():
    """Test 3: State persistence"""
    print("\n" + "="*60)
    print("TEST 3: State Persistence")
    print("="*60)

    test_state_file = Path("data/state/test_state.json")
    test_backup_dir = Path("data/state/test_backups")

    try:
        # Create fresh state manager for testing
        if test_state_file.exists():
            test_state_file.unlink()
        if test_backup_dir.exists():
            import shutil
            shutil.rmtree(test_backup_dir)

        state_mgr = StateManager(
            state_file=test_state_file,
            backup_dir=test_backup_dir
        )
        print("✓ State manager created")

        # Test initial state
        state = state_mgr.get_state()
        assert state.surveys == {}, "Initial surveys should be empty"
        assert state.workers == {}, "Initial workers should be empty"
        print("✓ Initial state is empty")

        # Test adding a survey
        state_mgr.update_survey(
            "test_survey_1",
            name="Test Survey",
            level="domain",
            universe="default",
            neighbourhood="parksville_bc",
            domain="cooking",
            status="idle"
        )
        print("✓ Survey added")

        # Verify survey was saved
        survey = state_mgr.get_survey("test_survey_1")
        assert survey is not None, "Survey should exist"
        assert survey.name == "Test Survey", "Survey name should match"
        assert survey.domain == "cooking", "Survey domain should match"
        print(f"✓ Survey retrieved: {survey.name} ({survey.level})")

        # Test adding a worker
        state_mgr.update_worker(
            "test_worker_1",
            status="running",
            task="test_task"
        )
        print("✓ Worker added")

        # Verify worker was saved
        worker = state_mgr.get_worker("test_worker_1")
        assert worker is not None, "Worker should exist"
        assert worker.status == "running", "Worker status should match"
        print(f"✓ Worker retrieved: {worker.worker_id} ({worker.status})")

        # Test updating survey
        state_mgr.update_survey("test_survey_1", status="running", progress=0.5)
        updated_survey = state_mgr.get_survey("test_survey_1")
        assert updated_survey.status == "running", "Status should be updated"
        assert updated_survey.progress == 0.5, "Progress should be updated"
        print("✓ Survey updated")

        # Test listing
        survey_ids = state_mgr.list_surveys()
        assert "test_survey_1" in survey_ids, "Survey should be in list"
        worker_ids = state_mgr.list_workers()
        assert "test_worker_1" in worker_ids, "Worker should be in list"
        print(f"✓ Lists: {len(survey_ids)} surveys, {len(worker_ids)} workers")

        # Test state persistence across reload
        state_mgr2 = StateManager(
            state_file=test_state_file,
            backup_dir=test_backup_dir
        )
        reloaded_survey = state_mgr2.get_survey("test_survey_1")
        assert reloaded_survey is not None, "Survey should persist across reload"
        assert reloaded_survey.progress == 0.5, "Progress should persist"
        print("✓ State persisted across reload")

        # Test backup creation
        state_mgr.update_survey("test_survey_1", progress=0.6)
        backup_files = list(test_backup_dir.glob("state_backup_*.json"))
        assert len(backup_files) > 0, "Backup file should be created"
        print(f"✓ Backup created: {backup_files[0].name}")

        # Test removal
        state_mgr.remove_worker("test_worker_1")
        assert state_mgr.get_worker("test_worker_1") is None, "Worker should be removed"
        print("✓ Worker removed")

        # Cleanup
        test_state_file.unlink(missing_ok=True)
        import shutil
        if test_backup_dir.exists():
            shutil.rmtree(test_backup_dir)
        print("✓ Cleanup complete")

        print("\n✓ TEST 3 PASSED: State Persistence")
        return True

    except Exception as e:
        print(f"\n✗ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        # Cleanup on failure
        test_state_file.unlink(missing_ok=True)
        import shutil
        if test_backup_dir.exists():
            shutil.rmtree(test_backup_dir)
        return False


def main():
    """Run all Phase 1 tests"""
    print("\n" + "="*60)
    print("PHASE 1 TEST SUITE")
    print("Foundation & Core Infrastructure")
    print("="*60)

    results = []

    # Run tests
    results.append(("Configuration", test_config()))
    results.append(("Logger", test_logger()))
    results.append(("State Persistence", test_state_persistence()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n✓ PHASE 1 TEST SUITE PASSED")
        return 0
    else:
        print("\n✗ PHASE 1 TEST SUITE FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
