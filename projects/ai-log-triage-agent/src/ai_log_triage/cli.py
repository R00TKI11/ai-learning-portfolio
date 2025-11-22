#!/usr/bin/env python3
"""
AI Log Triage Agent - CLI Interface

This module provides the command-line interface for the AI Log Triage Agent.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .log_parser import LogParser, LogEvent
from .triage_agent import TriageAgent, TriageResult


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='ai-log-triage',
        description="AI Log Triage Agent - Intelligent log analysis using LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single log file
  ai-log-triage --input data/webserver_error.log

  # Analyze all logs in data directory
  ai-log-triage --all

  # Save results to JSON file
  ai-log-triage --input data/auth_failures.log --output results.json --format json

  # Dry run to test parsing without API calls
  ai-log-triage --all --dry-run

  # Limit events for testing
  ai-log-triage --all --max-events 5

  # Use different model
  ai-log-triage --input data/java_exception.log --model x-ai/grok-4.1-fast
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input', '-i',
        type=str,
        help='Path to a specific log file or directory'
    )
    input_group.add_argument(
        '--all', '-a',
        action='store_true',
        help='Process all log files in the default data directory'
    )

    # Processing options
    parser.add_argument(
        '--chunk-method', '-c',
        type=str,
        choices=['event', 'line'],
        default='event',
        help='Chunking method: "event" (multi-line events) or "line" (line-by-line). Default: event'
    )

    parser.add_argument(
        '--model', '-m',
        type=str,
        help='LLM model to use (overrides default from config)'
    )

    parser.add_argument(
        '--max-events',
        type=int,
        help='Maximum number of events to process (useful for testing or free tier limits)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse logs but do not call LLM (useful for testing parsing logic)'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path (default: print to console)'
    )

    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['text', 'json', 'summary'],
        default='text',
        help='Output format: "text" (detailed), "json", or "summary". Default: text'
    )

    parser.add_argument(
        '--priority-filter', '-p',
        type=str,
        choices=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'],
        help='Only show results with this priority or higher'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    return parser


def filter_by_priority(results: List[TriageResult], min_priority: str) -> List[TriageResult]:
    """
    Filter results by minimum priority level.

    Args:
        results: List of triage results
        min_priority: Minimum priority level to include

    Returns:
        Filtered list of triage results
    """
    priority_order = {
        'CRITICAL': 0,
        'HIGH': 1,
        'MEDIUM': 2,
        'LOW': 3,
        'INFO': 4
    }

    min_level = priority_order[min_priority]
    return [
        result for result in results
        if priority_order[result.priority.value] <= min_level
    ]


def output_text(results: List[TriageResult], output_file: Optional[str] = None) -> None:
    """
    Output results in detailed text format.

    Args:
        results: List of triage results
        output_file: Optional file path to write output
    """
    output = ""

    for result in results:
        output += str(result) + "\n"

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Results written to {output_file}")
    else:
        print(output)


def output_json(results: List[TriageResult], output_file: Optional[str] = None) -> None:
    """
    Output results in JSON format.

    Args:
        results: List of triage results
        output_file: Optional file path to write output
    """
    data = [result.to_dict() for result in results]

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"JSON results written to {output_file}")
    else:
        print(json.dumps(data, indent=2))


def output_summary(results: List[TriageResult], output_file: Optional[str] = None) -> None:
    """
    Output summary report.

    Args:
        results: List of triage results
        output_file: Optional file path to write output
    """
    agent = TriageAgent()
    summary = agent.generate_summary_report(results)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary written to {output_file}")
    else:
        print(summary)


def run_dry_run(log_events: List[LogEvent]) -> None:
    """
    Run dry-run mode: parse and display log events without calling LLM.

    Args:
        log_events: List of parsed log events
    """
    print("\n=== DRY RUN MODE - Parsing Only (No LLM Calls) ===\n")

    for event in log_events:
        print(f"File: {event.source_file}, Line: {event.line_number}")
        print(f"Category: {event.category}, Level: {event.log_level}, Timestamp: {event.timestamp}")
        print(f"Content ({len(event.raw_content)} chars, {len(event.raw_content.split(chr(10)))} lines):")
        print(event.truncate_content(max_lines=10, max_chars=500))
        print("-" * 80)

    print(f"\nDry run complete. Parsed {len(log_events)} event(s).")


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        # Initialize parser and agent
        if args.verbose:
            print("Initializing Log Parser and Triage Agent...")

        log_parser = LogParser()
        agent = TriageAgent(model=args.model)

        # Parse log files
        log_events: List[LogEvent] = []

        if args.all:
            if args.verbose:
                print("Processing all log files in data directory...")
            log_events = list(log_parser.parse_all_logs(chunk_method=args.chunk_method))

        elif args.input:
            input_path = Path(args.input)

            # Check if input is a directory
            if input_path.is_dir():
                if args.verbose:
                    print(f"Processing all log files in {input_path}...")
                temp_parser = LogParser(data_dir=str(input_path))
                log_events = list(temp_parser.parse_all_logs(chunk_method=args.chunk_method))
            else:
                if args.verbose:
                    print(f"Processing log file: {input_path}...")
                log_events = list(log_parser.parse_log_file(str(input_path), chunk_method=args.chunk_method))

        if not log_events:
            print("No log events found to process.", file=sys.stderr)
            return 1

        print(f"\nFound {len(log_events)} log event(s) to analyze.")

        # Apply max-events limit if specified
        if args.max_events and len(log_events) > args.max_events:
            print(f"Limiting to first {args.max_events} event(s) (use --max-events to change)")
            log_events = log_events[:args.max_events]

        # Handle dry-run mode
        if args.dry_run:
            run_dry_run(log_events)
            return 0

        # Triage events
        print("Analyzing logs with LLM... (this may take a moment)\n")
        triage_results = agent.triage_batch(log_events)

        # Filter by priority if specified
        if args.priority_filter:
            original_count = len(triage_results)
            triage_results = filter_by_priority(triage_results, args.priority_filter)
            print(f"Filtered to {len(triage_results)} result(s) with priority {args.priority_filter} or higher (from {original_count} total)\n")

        if not triage_results:
            print("No results match the specified priority filter.", file=sys.stderr)
            return 0

        # Output results
        if args.format == 'text':
            output_text(triage_results, args.output)
        elif args.format == 'json':
            output_json(triage_results, args.output)
        elif args.format == 'summary':
            output_summary(triage_results, args.output)

        print(f"\nAnalysis complete! Processed {len(log_events)} event(s), generated {len(triage_results)} triage result(s).")

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
