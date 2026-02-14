"""
Logging and Error Handling Module
Provides comprehensive logging, error tracking, and debugging support

Features:
- Structured logging with multiple output levels
- Error tracking and reporting
- Performance monitoring and metrics
- Debug mode for detailed diagnostics
- Log file persistence
"""

import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class HoloMedLogger:
    """
    Central logging system for HoloMed application
    
    Features:
    - Console output with colors
    - File logging with rotation
    - Error tracking
    - Performance metrics
    - Debug mode
    """
    
    def __init__(self, name="HoloMed", log_dir="./logs", level=LogLevel.INFO, 
                 debug=False, log_to_file=True):
        """
        Initialize HoloMed logger
        
        Args:
            name (str): Logger name
            log_dir (str): Directory for log files
            level (LogLevel): Logging level
            debug (bool): Enable debug mode (verbose output)
            log_to_file (bool): Enable file logging
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.level = level
        self.debug_mode = debug
        self.log_to_file = log_to_file
        
        # Create logs directory if needed
        if log_to_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level.value)
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (if enabled)
        if log_to_file:
            log_file = self.log_dir / f"holomed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            file_formatter = logging.Formatter(
                '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            self.log_file = log_file
        else:
            self.log_file = None
        
        # Error tracking
        self.errors = []
        self.warnings = []
        
        # Performance metrics
        self.metrics = {}
        
        # Initial message
        self.info(f"HoloMed Logger initialized (Debug: {debug})")
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
        self.warnings.append({
            'timestamp': datetime.now(),
            'message': message
        })
    
    def error(self, message, exception=None):
        """
        Log error message
        
        Args:
            message (str): Error message
            exception (Exception): Optional exception object
        """
        if exception:
            self.logger.error(f"{message}: {exception}")
            if self.debug_mode:
                self.logger.debug(traceback.format_exc())
        else:
            self.logger.error(message)
        
        self.errors.append({
            'timestamp': datetime.now(),
            'message': message,
            'exception': exception
        })
    
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """
        Handle uncaught exceptions
        
        Can be used with sys.excepthook:
        logger = HoloMedLogger()
        sys.excepthook = logger.handle_exception
        """
        self.error("Uncaught exception", exc_value)
        if self.debug_mode:
            self.logger.debug(''.join(traceback.format_exception(
                exc_type, exc_value, exc_traceback
            )))
    
    def record_metric(self, metric_name, value, unit=""):
        """
        Record a performance metric
        
        Args:
            metric_name (str): Name of metric
            value (float): Metric value
            unit (str): Unit of measurement
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            'timestamp': datetime.now(),
            'value': value,
            'unit': unit
        })
        
        if self.debug_mode:
            self.debug(f"Metric {metric_name}: {value} {unit}")
    
    def get_metric_stats(self, metric_name):
        """
        Get statistics for a metric
        
        Args:
            metric_name (str): Name of metric
            
        Returns:
            dict: Statistics (min, max, avg, count)
        """
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return None
        
        values = [m['value'] for m in self.metrics[metric_name]]
        
        return {
            'metric': metric_name,
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'unit': self.metrics[metric_name][0].get('unit', '')
        }
    
    def print_metrics_summary(self):
        """Print summary of all recorded metrics"""
        if not self.metrics:
            self.info("No metrics recorded")
            return
        
        print("\n" + "="*60)
        print("Performance Metrics Summary")
        print("="*60)
        
        for metric_name in self.metrics.keys():
            stats = self.get_metric_stats(metric_name)
            if stats:
                print(f"\n{metric_name}:")
                print(f"  Count: {stats['count']}")
                print(f"  Min:   {stats['min']:.2f} {stats['unit']}")
                print(f"  Max:   {stats['max']:.2f} {stats['unit']}")
                print(f"  Avg:   {stats['avg']:.2f} {stats['unit']}")
    
    def print_error_report(self):
        """Print error report"""
        if not self.errors:
            self.info("No errors recorded")
            return
        
        print("\n" + "="*60)
        print("Error Report")
        print("="*60)
        print(f"Total errors: {len(self.errors)}\n")
        
        for i, error in enumerate(self.errors, 1):
            print(f"{i}. {error['timestamp'].strftime('%H:%M:%S')} - {error['message']}")
            if error['exception']:
                print(f"   Exception: {error['exception']}")
    
    def print_warning_report(self):
        """Print warning report"""
        if not self.warnings:
            self.info("No warnings recorded")
            return
        
        print("\n" + "="*60)
        print("Warning Report")
        print("="*60)
        print(f"Total warnings: {len(self.warnings)}\n")
        
        for i, warn in enumerate(self.warnings, 1):
            print(f"{i}. {warn['timestamp'].strftime('%H:%M:%S')} - {warn['message']}")
    
    def get_error_count(self):
        """Get number of errors recorded"""
        return len(self.errors)
    
    def get_warning_count(self):
        """Get number of warnings recorded"""
        return len(self.warnings)
    
    def reset_stats(self):
        """Reset error, warning, and metric tracking"""
        self.errors.clear()
        self.warnings.clear()
        self.metrics.clear()
        self.info("Statistics reset")


class ErrorHandler:
    """
    Centralized error handling with recovery strategies
    """
    
    def __init__(self, logger):
        """
        Initialize error handler
        
        Args:
            logger (HoloMedLogger): Logger instance
        """
        self.logger = logger
        self.recovery_strategies = {}
    
    def register_strategy(self, error_type, strategy_func):
        """
        Register error recovery strategy
        
        Args:
            error_type (str): Error type name
            strategy_func (callable): Recovery function
        """
        self.recovery_strategies[error_type] = strategy_func
    
    def handle_dicom_error(self, error, path=None):
        """Handle DICOM loading errors"""
        self.logger.error(f"DICOM Error", error)
        if path:
            self.logger.error(f"  Path: {path}")
        self.logger.error("  Solution: Verify DICOM files are valid and not corrupted")
    
    def handle_vtk_error(self, error):
        """Handle VTK rendering errors"""
        self.logger.error(f"VTK Error", error)
        self.logger.error("  Solution: Check system graphics drivers, GPU memory available")
    
    def handle_gesture_error(self, error, input_mode=None):
        """Handle gesture input errors"""
        self.logger.error(f"Gesture Input Error", error)
        if input_mode == "mqtt":
            self.logger.error("  Solution: Verify MQTT broker address, WiFi connection")
        elif input_mode == "serial":
            self.logger.error("  Solution: Verify serial port and USB connection")
    
    def handle_network_error(self, error, endpoint=None):
        """Handle network errors"""
        self.logger.error(f"Network Error", error)
        if endpoint:
            self.logger.error(f"  Endpoint: {endpoint}")
        self.logger.error("  Solution: Check network connection, firewall settings")


# Global logger instance
_global_logger = None


def get_logger(name="HoloMed", log_dir="./logs", level=LogLevel.INFO, 
               debug=False, log_to_file=True):
    """
    Get or create global logger instance
    
    Args:
        name (str): Logger name
        log_dir (str): Log directory
        level (LogLevel): Log level
        debug (bool): Debug mode
        log_to_file (bool): Enable file logging
        
    Returns:
        HoloMedLogger: Logger instance
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = HoloMedLogger(
            name=name,
            log_dir=log_dir,
            level=level,
            debug=debug,
            log_to_file=log_to_file
        )
    
    return _global_logger


# Example usage
if __name__ == "__main__":
    print("""
    This module provides logging and error handling for HoloMed.
    
    Usage:
    
    from logging_config import get_logger, ErrorHandler
    
    logger = get_logger(debug=True)
    logger.info("Application started")
    logger.warning("Low disk space")
    logger.error("Failed to load file")
    
    logger.record_metric("fps", 45.2, "frames/sec")
    logger.record_metric("latency", 35.8, "ms")
    
    logger.print_metrics_summary()
    logger.print_error_report()
    """)
