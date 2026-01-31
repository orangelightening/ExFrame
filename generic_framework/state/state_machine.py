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
State Machine Logging System

Provides complete observability of the query-response lifecycle through
structured state transition logging.
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class QueryState(Enum):
    """All possible states in the query lifecycle."""

    # Entry and Routing
    QUERY_RECEIVED = "QUERY_RECEIVED"
    DIRECT_PROMPT_CHECK = "DIRECT_PROMPT_CHECK"
    DIRECT_LLM = "DIRECT_LLM"
    ROUTING_SELECTION = "ROUTING_SELECTION"

    # Specialist Processing
    SINGLE_SPECIALIST_PROCESSING = "SINGLE_SPECIALIST_PROCESSING"
    MULTI_SPECIALIST_PROCESSING = "MULTI_SPECIALIST_PROCESSING"
    RESPONSE_AGGREGATION = "RESPONSE_AGGREGATION"

    # Content Processing
    OUT_OF_SCOPE_CHECK = "OUT_OF_SCOPE_CHECK"
    SEARCHING = "SEARCHING"
    CONTEXT_READY = "CONTEXT_READY"

    # Enrichment
    ENRICHMENT_PIPELINE = "ENRICHMENT_PIPELINE"
    LLM_CONFIRMATION_CHECK = "LLM_CONFIRMATION_CHECK"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    LLM_PROCESSING = "LLM_PROCESSING"
    LLM_POST_PROCESSING = "LLM_POST_PROCESSING"
    ENRICHMENT_COMPLETE = "ENRICHMENT_COMPLETE"

    # Output
    FORMATTING_PHASE = "FORMATTING_PHASE"
    RESPONSE_CONSTRUCTION = "RESPONSE_CONSTRUCTION"

    # Terminal States
    LOG_AND_EXIT = "LOG_AND_EXIT"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    RESPONSE_RETURNED = "RESPONSE_RETURNED"

    def __str__(self) -> str:
        return self.value


class QueryStateMachine:
    """State machine logger for query pipeline observability.

    Tracks all state transitions during query processing with detailed
    change tracking for enrichers and formatters.

    Example:
        sm = QueryStateMachine()
        sm.transition(QueryState.QUERY_RECEIVED, "api_request", {"query": "..."})
        sm.transition(QueryState.ROUTING_SELECTION, "routing_complete", {"specialist": "..."})
        sm.complete({"status": "success"})
    """

    def __init__(self, query_id: Optional[str] = None, domain: Optional[str] = None):
        """Initialize state machine.

        Args:
            query_id: Unique identifier for this query (auto-generated if None)
            domain: Domain ID for this query
        """
        self.query_id = query_id or self._generate_id()
        self.domain = domain
        self.current_state: Optional[QueryState] = None
        self.state_entered_at: Optional[datetime] = None
        self.events: List[Dict[str, Any]] = []

        # Log file path
        self.log_path = Path("/app/logs/traces/state_machine.jsonl")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _generate_id() -> str:
        """Generate unique query ID using UUID."""
        return f"q_{uuid.uuid4().hex[:12]}"

    def transition(self, to_state: QueryState, trigger: str,
                   data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log state transition with detailed change tracking.

        Args:
            to_state: The state being transitioned to
            trigger: What caused this transition
            data: State-specific data to log

        Returns:
            The event dictionary that was logged
        """
        now = datetime.utcnow()

        # Calculate duration in previous state
        duration_ms = None
        if self.state_entered_at:
            duration_ms = int((now - self.state_entered_at).total_seconds() * 1000)

        # Prepare event data
        event_data = data or {}

        # Add domain if not present
        if 'domain' not in event_data and self.domain:
            event_data['domain'] = self.domain

        # Create event
        event = {
            "query_id": self.query_id,
            "from_state": self.current_state.value if self.current_state else None,
            "to_state": to_state.value,
            "trigger": trigger,
            "timestamp": now.isoformat() + "Z",
            "data": event_data,
            "duration_ms": duration_ms
        }

        # Store in memory for trace retrieval
        self.events.append(event)

        # Write to log file (append)
        self._write_event(event)

        # Update internal state
        self.current_state = to_state
        self.state_entered_at = now

        return event

    def transition_with_changes(
        self,
        to_state: QueryState,
        trigger: str,
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None,
        component: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Log state transition with detailed before/after change tracking.

        This is the detailed logging mode (Option B) that captures exactly what
        each enricher and formatter changed in the response.

        Args:
            to_state: The state being transitioned to
            trigger: What caused this transition
            before: State before the transition
            after: State after the transition
            component: Component name (enricher/formatter name)
            changes: Detailed change information

        Returns:
            The event dictionary that was logged
        """
        now = datetime.utcnow()

        # Calculate duration
        duration_ms = None
        if self.state_entered_at:
            duration_ms = int((now - self.state_entered_at).total_seconds() * 1000)

        # Prepare event data
        event_data = {}
        if changes:
            event_data['changes'] = changes
        if component:
            event_data['component'] = component
        if before is not None:
            event_data['input_size'] = len(str(before))
        if after is not None:
            event_data['output_size'] = len(str(after))
        if self.domain:
            event_data['domain'] = self.domain

        # Create event
        event = {
            "query_id": self.query_id,
            "from_state": self.current_state.value if self.current_state else None,
            "to_state": to_state.value,
            "trigger": trigger,
            "timestamp": now.isoformat() + "Z",
            "data": event_data,
            "duration_ms": duration_ms
        }

        # Store and write
        self.events.append(event)
        self._write_event(event)

        # Update state
        self.current_state = to_state
        self.state_entered_at = now

        return event

    def log_enricher_changes(
        self,
        enricher_name: str,
        before: Dict[str, Any],
        after: Dict[str, Any],
        duration_ms: int
    ) -> Dict[str, Any]:
        """Log enricher execution with detailed change tracking.

        Helper method for enrichers to log what they changed.

        Args:
            enricher_name: Name of the enricher class
            before: Response data before enrichment
            after: Response data after enrichment
            duration_ms: Time taken for enrichment

        Returns:
            The event dictionary that was logged
        """
        changes = self._calculate_changes(before, after)

        event_data = {
            "enricher": enricher_name,
            "input_size": len(str(before)),
            "output_size": len(str(after)),
            "duration_ms": duration_ms,
            "changes": changes
        }

        return self.transition(QueryState.ENRICHMENT_PIPELINE, f"{enricher_name}_executed", event_data)

    def log_formatter_changes(
        self,
        formatter_name: str,
        before: Dict[str, Any],
        after: Union[str, Dict[str, Any]],
        format_type: str,
        duration_ms: int
    ) -> Dict[str, Any]:
        """Log formatter execution with detailed change tracking.

        Args:
            formatter_name: Name of the formatter class
            before: Response data before formatting
            after: Formatted response
            format_type: Target format (markdown, json, etc.)
            duration_ms: Time taken for formatting

        Returns:
            The event dictionary that was logged
        """
        changes = self._calculate_formatter_changes(before, after, format_type)

        event_data = {
            "formatter": formatter_name,
            "format_type": format_type,
            "input_type": type(before).__name__,
            "output_type": type(after).__name__,
            "input_size": len(str(before)),
            "output_size": len(str(after)),
            "duration_ms": duration_ms,
            "changes": changes
        }

        return self.transition(QueryState.FORMATTING_PHASE, f"{formatter_name}_applied", event_data)

    def _calculate_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate what changed between two data dictionaries.

        Args:
            before: Data before the operation
            after: Data after the operation

        Returns:
            Dictionary with 'added', 'removed', 'modified' keys
        """
        changes = {
            "added": {},
            "removed": {},
            "modified": {}
        }

        # Find added keys
        after_keys = set(after.keys()) if isinstance(after, dict) else set()
        before_keys = set(before.keys()) if isinstance(before, dict) else set()

        for key in after_keys:
            if key not in before_keys:
                changes["added"][key] = self._describe_value(after[key])

        # Find removed keys
        for key in before_keys:
            if key not in after_keys:
                changes["removed"][key] = self._describe_value(before[key])

        # Find modified keys
        for key in before_keys & after_keys:
            if before[key] != after[key]:
                changes["modified"][key] = self._compare_values(
                    before[key], after[key]
                )

        return changes

    def _calculate_formatter_changes(
        self,
        before: Dict[str, Any],
        after: Union[str, Dict[str, Any]],
        format_type: str
    ) -> Dict[str, Any]:
        """Calculate changes for formatting operation.

        Args:
            before: Response data before formatting
            after: Formatted response
            format_type: Target format

        Returns:
            Dictionary with 'added', 'removed', 'modified' keys
        """
        changes = {
            "added": {},
            "removed": {},
            "modified": {}
        }

        # Describe the conversion
        changes["added"] = {
            "formatted_content": {
                "type": type(after).__name__,
                "size": len(str(after)),
                "format_type": format_type
            }
        }

        # Describe what was removed
        changes["removed"] = {
            "response_data": {
                "type": type(before).__name__,
                "keys": list(before.keys()) if isinstance(before, dict) else []
            }
        }

        # Describe the transformation
        if isinstance(before, dict) and isinstance(after, str):
            changes["modified"] = {
                "structure": {
                    "from": "dict",
                    "to": "str",
                    "keys_preserved": len(before.keys()) if isinstance(before, dict) else 0
                }
            }

        return changes

    def _describe_value(self, value: Any) -> Dict[str, Any]:
        """Describe a single value for logging.

        Args:
            value: The value to describe

        Returns:
            Dictionary with description of the value
        """
        if isinstance(value, dict):
            return {
                "type": "dict",
                "count": len(value),
                "keys": list(value.keys())[:5],  # First 5 keys
                "all_keys": list(value.keys())
            }
        elif isinstance(value, list):
            return {
                "type": "list",
                "count": len(value),
                "preview": [str(v)[:50] for v in value[:3]]  # First 3 items
            }
        elif isinstance(value, str):
            return {
                "type": "str",
                "length": len(value),
                "preview": value[:100]
            }
        else:
            return {
                "type": type(value).__name__,
                "preview": str(value)[:100]
            }

    def _compare_values(self, before: Any, after: Any) -> Dict[str, Any]:
        """Compare two values and describe the difference.

        Args:
            before: Value before the operation
            after: Value after the operation

        Returns:
            Dictionary describing the difference
        """
        if isinstance(before, dict) and isinstance(after, dict):
            before_keys = set(before.keys())
            after_keys = set(after.keys())

            return {
                "type": "dict_modified",
                "keys_added": list(after_keys - before_keys),
                "keys_removed": list(before_keys - after_keys),
                "keys_modified": list(before_keys & after_keys),
                "size_delta": len(str(after)) - len(str(before))
            }

        # For strings, show length difference
        if isinstance(before, str) and isinstance(after, str):
            return {
                "type": "string_modified",
                "before_length": len(before),
                "after_length": len(after),
                "length_delta": len(after) - len(before)
            }

        # Fallback
        return {
            "type": type(after).__name__,
            "before": str(before)[:100],
            "after": str(after)[:100]
        }

    def error(self, trigger: str, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transition to ERROR state.

        Args:
            trigger: What caused the error
            error_data: Error details

        Returns:
            The event dictionary that was logged
        """
        return self.transition(QueryState.ERROR, trigger, error_data)

    def complete(self, final_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transition to COMPLETE state.

        Args:
            final_data: Final status information

        Returns:
            The event dictionary that was logged
        """
        return self.transition(QueryState.COMPLETE, "query_complete", final_data)

    def get_trace(self) -> List[Dict[str, Any]]:
        """Get all events for this query.

        Returns:
            List of all state transition events in chronological order
        """
        return self.events.copy()

    def _write_event(self, event: Dict[str, Any]) -> None:
        """Write event to log file.

        Args:
            event: The event dictionary to write
        """
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            # Log but don't fail the query
            print(f"[StateMachine] Failed to write event: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the state machine execution.

        Returns:
            Summary with total duration, final state, event count
        """
        if not self.events:
            return {
                "query_id": self.query_id,
                "events_count": 0,
                "final_state": None
            }

        # Get first and last events
        first_event = self.events[0]
        last_event = self.events[-1]

        # Calculate total duration
        total_duration_ms = None
        if len(self.events) >= 2:
            first_time = datetime.fromisoformat(first_event['timestamp'].replace('Z', ''))
            last_time = datetime.fromisoformat(last_event['timestamp'].replace('Z', ''))
            total_duration_ms = int((last_time - first_time).total_seconds() * 1000)

        return {
            "query_id": self.query_id,
            "domain": self.domain,
            "events_count": len(self.events),
            "first_state": first_event['from_state'],
            "final_state": last_event['to_state'],
            "total_duration_ms": total_duration_ms,
            "error_occurred": any(e['to_state'] == 'ERROR' for e in self.events),
            "components_used": self._get_components_used()
        }

    def _get_components_used(self) -> List[str]:
        """Extract list of components that were triggered.

        Returns:
            List of component names (enrichers, formatters, etc.)
        """
        components = []
        for event in self.events:
            if 'component' in event.get('data', {}):
                components.append(event['data']['component'])
            elif 'enricher' in event.get('data', {}):
                components.append(event['data']['enricher'])
            elif 'formatter' in event.get('data', {}):
                components.append(event['data']['formatter'])
        return components
