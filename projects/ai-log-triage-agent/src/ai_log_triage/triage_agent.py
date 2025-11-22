"""
Triage Agent Module
Uses LLM to analyze log events and provide intelligent triage insights.

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""

import json
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

from .log_parser import LogEvent
from .llm_client import call_llm


class Priority(Enum):
    """Priority levels for log events."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class TriageResult:
    """Result of triaging a log event."""
    log_event: LogEvent
    summary: str
    classification: str
    priority: Priority
    suggested_owner: str
    root_cause: str
    action_items: List[str]
    raw_llm_response: str = None

    def to_dict(self) -> Dict:
        """Convert triage result to dictionary."""
        return {
            'source_file': self.log_event.source_file,
            'line_number': self.log_event.line_number,
            'timestamp': self.log_event.timestamp,
            'log_level': self.log_event.log_level,
            'summary': self.summary,
            'classification': self.classification,
            'priority': self.priority.value,
            'suggested_owner': self.suggested_owner,
            'root_cause': self.root_cause,
            'action_items': self.action_items,
            'original_log': self.log_event.raw_content
        }

    def __str__(self) -> str:
        """String representation of triage result."""
        return f"""
{'='*80}
FILE: {self.log_event.source_file} (Line {self.log_event.line_number})
TIMESTAMP: {self.log_event.timestamp}
PRIORITY: {self.priority.value}
CLASSIFICATION: {self.classification}
SUGGESTED OWNER: {self.suggested_owner}

SUMMARY:
{self.summary}

ROOT CAUSE:
{self.root_cause}

ACTION ITEMS:
{chr(10).join(f'  - {item}' for item in self.action_items)}

ORIGINAL LOG:
{self.log_event.raw_content}
{'='*80}
"""


class TriageAgent:
    """
    LLM-based triage agent that analyzes log events and provides actionable insights.
    """

    TRIAGE_PROMPT = """You are an expert DevOps engineer analyzing log events. Your task is to triage the following log entry and provide structured analysis.

Analyze this log event and provide:
1. A brief summary (1-2 sentences)
2. Classification (e.g., "Database Error", "Authentication Failure", "Performance Issue", "Configuration Error", etc.)
3. Priority level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
4. Suggested owner/team (e.g., "Database Team", "Security Team", "Backend Team", "DevOps", etc.)
5. Root cause analysis (what likely caused this issue)
6. Action items (specific steps to resolve or investigate)

Log Event:
{log_content}

Respond in JSON format with the following structure:
{{
    "summary": "brief summary here",
    "classification": "category here",
    "priority": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
    "suggested_owner": "team/owner here",
    "root_cause": "root cause analysis here",
    "action_items": ["action 1", "action 2", ...]
}}

IMPORTANT: Return ONLY valid JSON, no additional text or markdown formatting."""

    def __init__(self, model: str = None):
        """
        Initialize the triage agent.

        Args:
            model: LLM model to use. If not provided, uses the default from config.
        """
        self.model = model

    def build_prompt(self, log_event: LogEvent, use_truncation: bool = True) -> str:
        """
        Build the LLM prompt for a log event.

        Args:
            log_event: LogEvent to analyze
            use_truncation: Whether to truncate long content

        Returns:
            Formatted prompt string
        """
        # Use truncated content if enabled
        content = log_event.truncate_content() if use_truncation else log_event.raw_content

        log_content = f"""File: {log_event.source_file}
Line: {log_event.line_number}
Timestamp: {log_event.timestamp}
Log Level: {log_event.log_level}
Category: {log_event.category}

Content:
{content}
"""
        return self.TRIAGE_PROMPT.format(log_content=log_content)

    def parse_llm_response(self, raw_response: str, log_event: LogEvent) -> TriageResult:
        """
        Parse LLM response into a TriageResult.

        Args:
            raw_response: Raw response from LLM
            log_event: The original log event

        Returns:
            TriageResult object
        """
        analysis = self._parse_llm_response(raw_response)

        return TriageResult(
            log_event=log_event,
            summary=analysis.get('summary', 'No summary provided'),
            classification=analysis.get('classification', 'Unknown'),
            priority=self._parse_priority(analysis.get('priority', 'MEDIUM')),
            suggested_owner=analysis.get('suggested_owner', 'Unknown'),
            root_cause=analysis.get('root_cause', 'Unknown'),
            action_items=analysis.get('action_items', []),
            raw_llm_response=raw_response
        )

    def triage_event(self, log_event: LogEvent, max_tokens: int = 1024, use_truncation: bool = True) -> TriageResult:
        """
        Triage a single log event using LLM analysis.

        Args:
            log_event: LogEvent to analyze
            max_tokens: Maximum tokens for LLM response
            use_truncation: Whether to truncate long log content

        Returns:
            TriageResult with analysis
        """
        try:
            # Build prompt
            prompt = self.build_prompt(log_event, use_truncation=use_truncation)

            # Call LLM API
            raw_response = call_llm(prompt, max_tokens=max_tokens, model=self.model)

            # Parse response
            return self.parse_llm_response(raw_response, log_event)

        except Exception as e:
            # Fallback for errors
            return TriageResult(
                log_event=log_event,
                summary=f"Error during triage: {str(e)}",
                classification="Triage Error",
                priority=Priority.MEDIUM,
                suggested_owner="DevOps",
                root_cause=f"LLM analysis failed: {str(e)}",
                action_items=["Manual review required"],
                raw_llm_response=str(e)
            )

    def triage_batch(self, log_events: List[LogEvent], max_tokens: int = 1024) -> List[TriageResult]:
        """
        Triage multiple log events.

        Args:
            log_events: List of LogEvent objects to analyze
            max_tokens: Maximum tokens per LLM response

        Returns:
            List of TriageResult objects
        """
        results = []
        for event in log_events:
            result = self.triage_event(event, max_tokens)
            results.append(result)
        return results

    def triage_and_group(self, log_events: List[LogEvent]) -> Dict[Priority, List[TriageResult]]:
        """
        Triage events and group by priority.

        Args:
            log_events: List of LogEvent objects

        Returns:
            Dictionary mapping Priority to list of TriageResults
        """
        results = self.triage_batch(log_events)

        grouped = {priority: [] for priority in Priority}
        for result in results:
            grouped[result.priority].append(result)

        return grouped

    def generate_summary_report(self, triage_results: List[TriageResult]) -> str:
        """
        Generate a summary report of all triage results.

        Args:
            triage_results: List of TriageResult objects

        Returns:
            Formatted summary report string
        """
        if not triage_results:
            return "No triage results to report."

        # Count by priority
        priority_counts = {priority: 0 for priority in Priority}
        for result in triage_results:
            priority_counts[result.priority] += 1

        # Count by classification
        classification_counts = {}
        for result in triage_results:
            classification_counts[result.classification] = \
                classification_counts.get(result.classification, 0) + 1

        # Build report
        report = f"""
LOG TRIAGE SUMMARY REPORT
{'='*80}

TOTAL EVENTS ANALYZED: {len(triage_results)}

PRIORITY BREAKDOWN:
"""
        for priority in Priority:
            count = priority_counts[priority]
            if count > 0:
                report += f"  {priority.value}: {count}\n"

        report += f"\nCLASSIFICATION BREAKDOWN:\n"
        for classification, count in sorted(classification_counts.items(), key=lambda x: x[1], reverse=True):
            report += f"  {classification}: {count}\n"

        report += f"\n{'='*80}\n"
        report += "\nDETAILED RESULTS:\n"

        # Sort by priority (CRITICAL first)
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3,
            Priority.INFO: 4
        }
        sorted_results = sorted(triage_results, key=lambda r: priority_order[r.priority])

        for result in sorted_results:
            report += str(result) + "\n"

        return report

    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response, handling potential JSON formatting issues."""
        # Try to extract JSON from markdown code blocks if present
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            response = response[start:end].strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Fallback parsing
            return {
                'summary': 'Failed to parse LLM response',
                'classification': 'Parse Error',
                'priority': 'MEDIUM',
                'suggested_owner': 'DevOps',
                'root_cause': f'JSON parsing failed: {str(e)}',
                'action_items': ['Review LLM response format']
            }

    def _parse_priority(self, priority_str: str) -> Priority:
        """Parse priority string to Priority enum."""
        try:
            return Priority[priority_str.upper()]
        except KeyError:
            return Priority.MEDIUM


# Example usage
if __name__ == "__main__":
    from .log_parser import LogParser

    # Initialize parser and agent
    parser = LogParser()
    agent = TriageAgent()

    print("Starting log triage analysis...\n")

    # Parse logs
    log_events = list(parser.parse_all_logs(chunk_method='event'))
    print(f"Found {len(log_events)} log events to analyze.\n")

    # Triage events
    triage_results = agent.triage_batch(log_events)

    # Generate and print summary report
    report = agent.generate_summary_report(triage_results)
    print(report)

    # Export to JSON
    output_file = "triage_results.json"
    with open(output_file, 'w') as f:
        json.dump([result.to_dict() for result in triage_results], f, indent=2)

    print(f"\nResults exported to {output_file}")
