"""
Log Parser Module
Loads raw log files, chunks them into events, and prepares them for LLM processing.

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""

import re
from pathlib import Path
from typing import List, Dict, Generator
from dataclasses import dataclass


@dataclass
class LogEvent:
    """Represents a single log event or chunk."""
    raw_content: str
    line_number: int
    timestamp: str = None
    log_level: str = None
    source_file: str = None
    category: str = None

    def to_dict(self) -> Dict:
        """Convert log event to dictionary for LLM processing."""
        return {
            'content': self.raw_content,
            'line_number': self.line_number,
            'timestamp': self.timestamp,
            'log_level': self.log_level,
            'source_file': self.source_file,
            'category': self.category
        }

    def truncate_content(self, max_lines: int = 50, max_chars: int = 5000) -> str:
        """
        Truncate content to avoid excessive token usage.

        Args:
            max_lines: Maximum number of lines to include
            max_chars: Maximum number of characters to include

        Returns:
            Truncated content with indication if truncated
        """
        lines = self.raw_content.split('\n')
        truncated = False
        result = self.raw_content

        # Truncate by lines
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            truncated = True

        # Truncate by characters
        result = '\n'.join(lines)
        if len(result) > max_chars:
            result = result[:max_chars]
            truncated = True

        if truncated:
            result += f"\n... [truncated - original was {len(self.raw_content)} chars, {len(self.raw_content.split(chr(10)))} lines]"

        return result


class LogParser:
    """
    Parses log files and chunks them into events for LLM processing.
    Handles multi-line events (e.g., stack traces) intelligently.
    """

    # Common log level patterns
    LOG_LEVEL_PATTERN = re.compile(r'\b(TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\b', re.IGNORECASE)

    # Common timestamp patterns
    TIMESTAMP_PATTERNS = [
        re.compile(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}'),  # ISO format
        re.compile(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'),  # Bracketed
        re.compile(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}'),      # MM/DD/YYYY
    ]

    # Category detection patterns (filename or content-based)
    CATEGORY_PATTERNS = {
        'auth': ['auth', 'login', 'authentication', 'oauth', 'token'],
        'web': ['webserver', 'http', 'nginx', 'apache', 'api'],
        'database': ['db', 'database', 'sql', 'postgres', 'mysql', 'mongo'],
        'security': ['security', 'firewall', 'intrusion', 'vuln'],
        'deployment': ['deploy', 'pipeline', 'ci', 'cd', 'build'],
        'performance': ['performance', 'perf', 'latency', 'slow'],
    }

    def __init__(self, data_dir: str = None):
        """
        Initialize the log parser.

        Args:
            data_dir: Directory containing log files. Defaults to ../data relative to this file.
        """
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            # Default to data directory relative to this file
            self.data_dir = Path(__file__).parent.parent.parent / 'data'

        # Ensure a data dir is found    
        if not self.data_dir.exists():
                raise FileNotFoundError(f"Data directory does not exist: {self.data_dir}")

    def load_log_file(self, file_path: str) -> List[str]:
        """
        Load a log file and return its lines.

        Args:
            file_path: Path to the log file (can be absolute or relative to current directory or data_dir)

        Returns:
            List of log lines
        """
        path = Path(file_path)

        # If it's an absolute path, use it directly
        if path.is_absolute():
            target_path = path
        # If the relative path exists from current directory, use it
        elif path.exists():
            target_path = path
        # Otherwise, try relative to data_dir
        else:
            target_path = self.data_dir / file_path

        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found: {target_path}")
        except Exception as e:
            raise Exception(f"Error reading log file {target_path}: {str(e)}")

    def extract_timestamp(self, line: str) -> str:
        """Extract timestamp from a log line."""
        for pattern in self.TIMESTAMP_PATTERNS:
            match = pattern.search(line)
            if match:
                return match.group(0).strip('[]')
        return None

    def extract_log_level(self, line: str) -> str:
        """Extract log level from a log line."""
        match = self.LOG_LEVEL_PATTERN.search(line)
        if match:
            return match.group(0).upper()
        return None

    def detect_category(self, source_file: str) -> str:
        """
        Detect log category based on filename patterns.

        Args:
            source_file: Name of the source file

        Returns:
            Category string or 'general' if no match
        """
        if not source_file:
            return 'general'

        filename_lower = source_file.lower()

        for category, keywords in self.CATEGORY_PATTERNS.items():
            if any(keyword in filename_lower for keyword in keywords):
                return category

        return 'general'

    def is_continuation_line(self, line: str) -> bool:
        """
        Determine if a line is a continuation of a previous event.
        Continuation lines typically start with whitespace or are stack trace lines.
        """
        if not line.strip():
            return False

        # Stack trace patterns
        stack_trace_indicators = [
            line.strip().startswith('at '),
            line.strip().startswith('Caused by:'),
            line.strip().startswith('...'),
            re.match(r'^\s+at\s+', line),
            re.match(r'^\s+\.\.\.', line),
            re.match(r'^\s+Caused by:', line),
        ]

        if any(stack_trace_indicators):
            return True

        # If line starts with whitespace and doesn't have timestamp/log level, it's likely a continuation
        if line.startswith((' ', '\t')):
            if not self.extract_timestamp(line) and not self.extract_log_level(line):
                return True

        return False

    def chunk_by_event(self, lines: List[str], source_file: str = None) -> Generator[LogEvent, None, None]:
        """
        Chunk log lines into events. Multi-line events (like stack traces) are kept together.

        Args:
            lines: List of log file lines
            source_file: Name of the source file (for tracking)

        Yields:
            LogEvent objects
        """
        if not lines:
            return

        category = self.detect_category(source_file)
        current_event = []
        current_line_number = 1
        event_timestamp = None
        event_log_level = None

        for i, line in enumerate(lines, start=1):
            # Skip empty lines between events
            if not line.strip() and not current_event:
                continue

            # Check if this is a continuation of the previous event
            if current_event and self.is_continuation_line(line):
                current_event.append(line.rstrip())
            else:
                # Yield the previous event if it exists
                if current_event:
                    yield LogEvent(
                        raw_content='\n'.join(current_event),
                        line_number=current_line_number,
                        timestamp=event_timestamp,
                        log_level=event_log_level,
                        source_file=source_file,
                        category=category
                    )

                # Start a new event
                current_event = [line.rstrip()]
                current_line_number = i
                event_timestamp = self.extract_timestamp(line)
                event_log_level = self.extract_log_level(line)

        # Don't forget the last event
        if current_event:
            yield LogEvent(
                raw_content='\n'.join(current_event),
                line_number=current_line_number,
                timestamp=event_timestamp,
                log_level=event_log_level,
                source_file=source_file,
                category=category
            )

    def chunk_by_line(self, lines: List[str], source_file: str = None) -> Generator[LogEvent, None, None]:
        """
        Chunk log lines individually (simple line-by-line processing).

        Args:
            lines: List of log file lines
            source_file: Name of the source file (for tracking)

        Yields:
            LogEvent objects (one per line)
        """
        category = self.detect_category(source_file)

        for i, line in enumerate(lines, start=1):
            if line.strip():  # Skip empty lines
                yield LogEvent(
                    raw_content=line.rstrip(),
                    line_number=i,
                    timestamp=self.extract_timestamp(line),
                    log_level=self.extract_log_level(line),
                    source_file=source_file,
                    category=category
                )

    def parse_log_file(self, file_path: str, chunk_method: str = 'event') -> Generator[LogEvent, None, None]:
        """
        Parse a log file and yield log events.

        Args:
            file_path: Path to the log file
            chunk_method: 'event' for intelligent multi-line chunking, 'line' for line-by-line

        Yields:
            LogEvent objects
        """
        lines = self.load_log_file(file_path)
        source_file = Path(file_path).name

        if chunk_method == 'event':
            yield from self.chunk_by_event(lines, source_file)
        elif chunk_method == 'line':
            yield from self.chunk_by_line(lines, source_file)
        else:
            raise ValueError(f"Invalid chunk_method: {chunk_method}. Must be 'event' or 'line'")

    def get_all_log_files(self) -> List[Path]:
        """Get all .log files in the data directory."""
        return list(self.data_dir.glob('*.log'))

    def parse_all_logs(self, chunk_method: str = 'event') -> Generator[LogEvent, None, None]:
        """
        Parse all log files in the data directory.

        Args:
            chunk_method: 'event' for intelligent multi-line chunking, 'line' for line-by-line

        Yields:
            LogEvent objects from all log files
        """
        log_files = self.get_all_log_files()

        if not log_files:
            raise ValueError(f"No log files found in {self.data_dir}")

        for log_file in log_files:
            yield from self.parse_log_file(log_file, chunk_method)


# Example usage
if __name__ == "__main__":
    parser = LogParser()

    print("=== Parsing all log files ===\n")

    for event in parser.parse_all_logs(chunk_method='event'):
        print(f"File: {event.source_file}, Line: {event.line_number}")
        print(f"Timestamp: {event.timestamp}, Level: {event.log_level}")
        print(f"Content:\n{event.raw_content}")
        print("-" * 80)
