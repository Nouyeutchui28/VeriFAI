"""
Metrics and monitoring for VeriFAI LLM
"""

import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from functools import wraps


@dataclass
class ScanMetrics:
    """Data class for scan metrics"""
    scan_id: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    files_scanned: int = 0
    vulnerabilities_found: int = 0
    semgrep_time: Optional[float] = None
    llm_time: Optional[float] = None
    code_size_bytes: int = 0
    status: str = "pending"
    error_message: Optional[str] = None


class MetricsCollector:
    """Collects and manages metrics"""

    def __init__(self, metrics_dir: str = "metrics"):
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(exist_ok=True)
        self.current_scan: Optional[ScanMetrics] = None

    def start_scan(self, scan_id: str) -> ScanMetrics:
        """
        Start tracking a new scan

        Args:
            scan_id: Unique identifier for the scan

        Returns:
            ScanMetrics instance
        """
        self.current_scan = ScanMetrics(
            scan_id=scan_id,
            start_time=datetime.now().isoformat()
        )
        return self.current_scan

    def end_scan(self, status: str = "completed", error_message: Optional[str] = None):
        """
        End current scan and save metrics

        Args:
            status: Final status (completed, failed, etc.)
            error_message: Error message if failed
        """
        if not self.current_scan:
            return

        self.current_scan.end_time = datetime.now().isoformat()
        self.current_scan.status = status
        self.current_scan.error_message = error_message

        # Calculate duration
        start = datetime.fromisoformat(self.current_scan.start_time)
        end = datetime.fromisoformat(self.current_scan.end_time)
        self.current_scan.duration_seconds = (end - start).total_seconds()

        self._save_metrics()

    def update_scan(self, **kwargs):
        """Update current scan metrics"""
        if not self.current_scan:
            return

        for key, value in kwargs.items():
            if hasattr(self.current_scan, key):
                setattr(self.current_scan, key, value)

    def _save_metrics(self):
        """Save metrics to file"""
        if not self.current_scan:
            return

        metrics_file = self.metrics_dir / f"{self.current_scan.scan_id}.json"
        with open(metrics_file, 'w') as f:
            json.dump(asdict(self.current_scan), f, indent=2)

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        metrics_files = list(self.metrics_dir.glob("*.json"))

        if not metrics_files:
            return {"total_scans": 0}

        total_scans = len(metrics_files)
        total_time = 0
        completed = 0
        failed = 0
        total_vulnerabilities = 0

        for metrics_file in metrics_files:
            with open(metrics_file) as f:
                data = json.load(f)
                if data.get("duration_seconds"):
                    total_time += data["duration_seconds"]
                if data.get("status") == "completed":
                    completed += 1
                elif data.get("status") == "failed":
                    failed += 1
                total_vulnerabilities += data.get("vulnerabilities_found", 0)

        return {
            "total_scans": total_scans,
            "completed": completed,
            "failed": failed,
            "total_time_seconds": total_time,
            "average_time_seconds": total_time / total_scans if total_scans > 0 else 0,
            "total_vulnerabilities": total_vulnerabilities,
            "success_rate": (completed / total_scans * 100) if total_scans > 0 else 0
        }


def track_performance(metrics_collector: Optional[MetricsCollector] = None):
    """
    Decorator to track function performance

    Args:
        metrics_collector: MetricsCollector instance
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if metrics_collector:
                    # Log to metrics collector
                    pass
        return wrapper
    return decorator


class PerformanceMonitor:
    """Monitor performance of operations"""

    def __init__(self):
        self.operations: Dict[str, list] = {}

    def record_operation(self, operation_name: str, duration_seconds: float, success: bool = True):
        """Record an operation's performance"""
        if operation_name not in self.operations:
            self.operations[operation_name] = []

        self.operations[operation_name].append({
            "duration": duration_seconds,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })

    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for an operation"""
        if operation_name not in self.operations:
            return {}

        ops = self.operations[operation_name]
        durations = [op["duration"] for op in ops]
        successes = sum(1 for op in ops if op["success"])

        return {
            "count": len(ops),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "success_rate": (successes / len(ops) * 100) if ops else 0
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all operations"""
        return {
            op_name: self.get_operation_stats(op_name)
            for op_name in self.operations.keys()
        }
