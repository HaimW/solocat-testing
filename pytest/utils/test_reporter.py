"""
Test Reporting and Alerting System
Comprehensive test result tracking, reporting, and alert generation
"""
import json
import time
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Any
import sys


class TestReporter:
    """Comprehensive test reporting and alerting system"""
    
    def __init__(self, output_dir="test-reports"):
        self.output_dir = output_dir
        self.test_results = []
        self.metrics = defaultdict(lambda: defaultdict(int))
        self.alerts = []
        self.thresholds = {
            'max_failure_rate': 0.20,  # 20% max failure rate
            'max_test_duration': 300,   # 5 minutes max per test
            'min_coverage': 0.80,       # 80% minimum coverage
            'max_memory_usage': 500,    # 500MB max memory
            'max_response_time': 2.0    # 2 seconds max API response
        }
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def record_test_result(self, test_info: Dict[str, Any]):
        """Record individual test result"""
        test_record = {
            'timestamp': time.time(),
            'test_name': test_info.get('test_name'),
            'test_category': test_info.get('test_category'),
            'status': test_info.get('status'),  # passed, failed, skipped
            'duration': test_info.get('duration', 0),
            'error_message': test_info.get('error_message'),
            'memory_usage': test_info.get('memory_usage', 0),
            'assertions': test_info.get('assertions', 0)
        }
        
        self.test_results.append(test_record)
        self._update_metrics(test_record)
        self._check_alerts(test_record)
    
    def _update_metrics(self, test_record: Dict[str, Any]):
        """Update running metrics"""
        category = test_record['test_category']
        status = test_record['status']
        
        self.metrics[category]['total'] += 1
        self.metrics[category][status] += 1
        self.metrics[category]['total_duration'] += test_record['duration']
        
        # Overall metrics
        self.metrics['overall']['total'] += 1
        self.metrics['overall'][status] += 1
        self.metrics['overall']['total_duration'] += test_record['duration']
    
    def _check_alerts(self, test_record: Dict[str, Any]):
        """Check for alert conditions"""
        alerts = []
        
        # High failure rate alert
        category = test_record['test_category']
        if self.metrics[category]['total'] >= 5:  # After at least 5 tests
            failure_rate = (
                self.metrics[category]['failed'] / 
                self.metrics[category]['total']
            )
            if failure_rate > self.thresholds['max_failure_rate']:
                alerts.append({
                    'type': 'HIGH_FAILURE_RATE',
                    'severity': 'WARNING',
                    'message': f"High failure rate in {category}: {failure_rate:.1%}",
                    'timestamp': time.time(),
                    'data': {'category': category, 'failure_rate': failure_rate}
                })
        
        # Long test duration alert
        if test_record['duration'] > self.thresholds['max_test_duration']:
            alerts.append({
                'type': 'SLOW_TEST',
                'severity': 'INFO',
                'message': f"Slow test: {test_record['test_name']} took {test_record['duration']:.2f}s",
                'timestamp': time.time(),
                'data': {'test_name': test_record['test_name'], 'duration': test_record['duration']}
            })
        
        # Memory usage alert
        if test_record['memory_usage'] > self.thresholds['max_memory_usage']:
            alerts.append({
                'type': 'HIGH_MEMORY_USAGE',
                'severity': 'WARNING',
                'message': f"High memory usage: {test_record['memory_usage']}MB",
                'timestamp': time.time(),
                'data': {'memory_usage': test_record['memory_usage']}
            })
        
        self.alerts.extend(alerts)
        
        # Log critical alerts immediately
        for alert in alerts:
            if alert['severity'] in ['ERROR', 'CRITICAL']:
                print(f"🚨 ALERT [{alert['severity']}]: {alert['message']}")
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive test summary report"""
        total_tests = len(self.test_results)
        if total_tests == 0:
            return {'message': 'No tests recorded'}
        
        # Calculate overall statistics
        passed = sum(1 for t in self.test_results if t['status'] == 'passed')
        failed = sum(1 for t in self.test_results if t['status'] == 'failed')
        skipped = sum(1 for t in self.test_results if t['status'] == 'skipped')
        
        total_duration = sum(t['duration'] for t in self.test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        # Category breakdown
        category_stats = {}
        categories = set(t['test_category'] for t in self.test_results)
        for category in categories:
            cat_tests = [t for t in self.test_results if t['test_category'] == category]
            cat_passed = sum(1 for t in cat_tests if t['status'] == 'passed')
            cat_failed = sum(1 for t in cat_tests if t['status'] == 'failed')
            cat_total = len(cat_tests)
            
            category_stats[category] = {
                'total': cat_total,
                'passed': cat_passed,
                'failed': cat_failed,
                'skipped': cat_total - cat_passed - cat_failed,
                'pass_rate': cat_passed / cat_total if cat_total > 0 else 0,
                'avg_duration': sum(t['duration'] for t in cat_tests) / cat_total if cat_total > 0 else 0
            }
        
        # Recent failures (last 10)
        recent_failures = [
            t for t in sorted(self.test_results, key=lambda x: x['timestamp'], reverse=True)
            if t['status'] == 'failed'
        ][:10]
        
        # Performance metrics
        slowest_tests = sorted(
            self.test_results, 
            key=lambda x: x['duration'], 
            reverse=True
        )[:5]
        
        return {
            'summary': {
                'total_tests': total_tests,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'pass_rate': passed / total_tests if total_tests > 0 else 0,
                'total_duration': total_duration,
                'average_duration': avg_duration,
                'test_efficiency': passed / total_duration if total_duration > 0 else 0
            },
            'category_breakdown': category_stats,
            'recent_failures': recent_failures,
            'slowest_tests': slowest_tests,
            'alerts': {
                'total_alerts': len(self.alerts),
                'critical_alerts': len([a for a in self.alerts if a['severity'] == 'CRITICAL']),
                'warning_alerts': len([a for a in self.alerts if a['severity'] == 'WARNING']),
                'recent_alerts': self.alerts[-10:]  # Last 10 alerts
            },
            'timestamp': time.time(),
            'report_id': f"test_report_{int(time.time())}"
        }
    
    def export_detailed_report(self, format='json') -> str:
        """Export detailed test report"""
        report = self.generate_summary_report()
        report['detailed_results'] = self.test_results
        report['all_alerts'] = self.alerts
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filename = f"{self.output_dir}/test_report_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
        
        elif format == 'html':
            filename = f"{self.output_dir}/test_report_{timestamp}.html"
            html_content = self._generate_html_report(report)
            with open(filename, 'w') as f:
                f.write(html_content)
        
        return filename
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML report"""
        summary = report['summary']
        
        # Status color coding
        pass_rate = summary['pass_rate']
        if pass_rate >= 0.95:
            status_color = '#28a745'  # green
            status_text = 'EXCELLENT'
        elif pass_rate >= 0.80:
            status_color = '#ffc107'  # yellow
            status_text = 'GOOD'
        else:
            status_color = '#dc3545'  # red
            status_text = 'NEEDS ATTENTION'
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Audio Processing System - Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
        .status {{ background: {status_color}; color: white; padding: 10px; border-radius: 4px; display: inline-block; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .alerts {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .failure {{ background: #f8d7da; padding: 10px; margin: 5px 0; border-radius: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎵 Audio Processing System - Test Report</h1>
        <div class="status">{status_text} - {pass_rate:.1%} Pass Rate</div>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <div class="metric-value">{summary['total_tests']}</div>
            <div>Total Tests</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{summary['passed']}</div>
            <div>Passed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{summary['failed']}</div>
            <div>Failed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{summary['total_duration']:.1f}s</div>
            <div>Total Duration</div>
        </div>
    </div>
    
    <h2>📊 Category Breakdown</h2>
    <table>
        <tr>
            <th>Category</th>
            <th>Total</th>
            <th>Passed</th>
            <th>Failed</th>
            <th>Pass Rate</th>
            <th>Avg Duration</th>
        </tr>
        {self._generate_category_rows(report['category_breakdown'])}
    </table>
    
    <h2>🚨 Recent Alerts ({len(report['alerts']['recent_alerts'])})</h2>
    <div class="alerts">
        {self._generate_alert_items(report['alerts']['recent_alerts'])}
    </div>
    
    <h2>❌ Recent Failures</h2>
    {self._generate_failure_items(report['recent_failures'])}
    
    <h2>🐌 Slowest Tests</h2>
    <table>
        <tr>
            <th>Test Name</th>
            <th>Category</th>
            <th>Duration</th>
            <th>Status</th>
        </tr>
        {self._generate_slow_test_rows(report['slowest_tests'])}
    </table>
</body>
</html>
"""
        return html_template
    
    def _generate_category_rows(self, categories: Dict[str, Any]) -> str:
        rows = []
        for category, stats in categories.items():
            pass_rate = stats['pass_rate']
            color = '#d4edda' if pass_rate >= 0.8 else '#f8d7da' if pass_rate < 0.5 else '#fff3cd'
            rows.append(f"""
                <tr style="background-color: {color}">
                    <td>{category}</td>
                    <td>{stats['total']}</td>
                    <td>{stats['passed']}</td>
                    <td>{stats['failed']}</td>
                    <td>{pass_rate:.1%}</td>
                    <td>{stats['avg_duration']:.2f}s</td>
                </tr>
            """)
        return ''.join(rows)
    
    def _generate_alert_items(self, alerts: List[Dict[str, Any]]) -> str:
        if not alerts:
            return "<p>✅ No recent alerts</p>"
        
        items = []
        for alert in alerts:
            severity_emoji = {'CRITICAL': '🔴', 'WARNING': '🟡', 'INFO': '🔵'}.get(alert['severity'], '⚪')
            items.append(f"<p>{severity_emoji} <strong>{alert['type']}</strong>: {alert['message']}</p>")
        return ''.join(items)
    
    def _generate_failure_items(self, failures: List[Dict[str, Any]]) -> str:
        if not failures:
            return "<p>✅ No recent failures</p>"
        
        items = []
        for failure in failures:
            items.append(f"""
                <div class="failure">
                    <strong>{failure['test_name']}</strong> ({failure['test_category']})
                    <br><small>Error: {failure.get('error_message', 'No error message')}</small>
                    <br><small>Duration: {failure['duration']:.2f}s</small>
                </div>
            """)
        return ''.join(items)
    
    def _generate_slow_test_rows(self, slow_tests: List[Dict[str, Any]]) -> str:
        rows = []
        for test in slow_tests:
            duration = test['duration']
            color = '#f8d7da' if duration > 60 else '#fff3cd' if duration > 30 else ''
            rows.append(f"""
                <tr style="background-color: {color}">
                    <td>{test['test_name']}</td>
                    <td>{test['test_category']}</td>
                    <td>{duration:.2f}s</td>
                    <td>{test['status']}</td>
                </tr>
            """)
        return ''.join(rows)
    
    def send_alert_notification(self, alert_config: Dict[str, Any] = None):
        """Send alert notifications (mock implementation)"""
        critical_alerts = [a for a in self.alerts if a['severity'] == 'CRITICAL']
        warning_alerts = [a for a in self.alerts if a['severity'] == 'WARNING']
        
        if critical_alerts or len(warning_alerts) > 5:
            print("\n🚨 ALERT NOTIFICATION")
            print(f"Critical Alerts: {len(critical_alerts)}")
            print(f"Warning Alerts: {len(warning_alerts)}")
            
            if critical_alerts:
                print("\nCritical Issues:")
                for alert in critical_alerts[-3:]:  # Last 3 critical
                    print(f"  • {alert['message']}")
            
            print("\n📧 Notification sent to test team")
            print("📱 Slack/Teams message posted")
            print("📊 Dashboard updated")
    
    def get_trend_analysis(self, days_back: int = 7) -> Dict[str, Any]:
        """Analyze test trends over time"""
        cutoff_time = time.time() - (days_back * 24 * 3600)
        recent_tests = [t for t in self.test_results if t['timestamp'] > cutoff_time]
        
        if not recent_tests:
            return {'message': 'No recent test data for trend analysis'}
        
        # Group by day
        daily_stats = defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0})
        for test in recent_tests:
            day = datetime.fromtimestamp(test['timestamp']).strftime('%Y-%m-%d')
            daily_stats[day]['total'] += 1
            daily_stats[day][test['status']] += 1
        
        # Calculate trends
        days = sorted(daily_stats.keys())
        if len(days) > 1:
            recent_pass_rate = daily_stats[days[-1]]['passed'] / daily_stats[days[-1]]['total'] if daily_stats[days[-1]]['total'] > 0 else 0
            previous_pass_rate = daily_stats[days[-2]]['passed'] / daily_stats[days[-2]]['total'] if daily_stats[days[-2]]['total'] > 0 else 0
            trend = recent_pass_rate - previous_pass_rate
        else:
            trend = 0
        
        return {
            'daily_stats': dict(daily_stats),
            'trend_direction': 'improving' if trend > 0.05 else 'declining' if trend < -0.05 else 'stable',
            'trend_value': trend,
            'analysis_period': f"{days_back} days",
            'total_recent_tests': len(recent_tests)
        }


# Global reporter instance
test_reporter = TestReporter()


# Integration functions for pytest
def pytest_runtest_protocol(item, nextitem):
    """Pytest hook to record test start"""
    test_name = item.name
    test_category = item.parent.name if hasattr(item, 'parent') else 'unknown'
    
    # Record test start (can be used for timeout monitoring)
    print(f"🧪 Starting test: {test_name}")


def pytest_runtest_makereport(item, call):
    """Pytest hook to record test results"""
    if call.when == 'call':  # Only record the actual test call, not setup/teardown
        test_name = item.name
        test_category = getattr(item.parent, 'name', 'unknown')
        
        status = 'passed' if call.excinfo is None else 'failed'
        duration = call.duration if hasattr(call, 'duration') else 0
        error_message = str(call.excinfo.value) if call.excinfo else None
        
        test_reporter.record_test_result({
            'test_name': test_name,
            'test_category': test_category,
            'status': status,
            'duration': duration,
            'error_message': error_message,
            'memory_usage': 0,  # Could be enhanced with actual memory tracking
            'assertions': 1     # Could be enhanced with actual assertion counting
        })


def generate_final_report():
    """Generate final test report"""
    print("\n📊 Generating Test Report...")
    
    # Export reports
    json_report = test_reporter.export_detailed_report('json')
    html_report = test_reporter.export_detailed_report('html')
    
    print(f"📄 JSON Report: {json_report}")
    print(f"🌐 HTML Report: {html_report}")
    
    # Generate summary
    summary = test_reporter.generate_summary_report()
    print(f"\n✅ Tests Completed: {summary['summary']['total_tests']}")
    print(f"✅ Pass Rate: {summary['summary']['pass_rate']:.1%}")
    print(f"⏱️  Total Duration: {summary['summary']['total_duration']:.1f}s")
    
    # Check for alerts
    if summary['alerts']['total_alerts'] > 0:
        print(f"🚨 Alerts Generated: {summary['alerts']['total_alerts']}")
        test_reporter.send_alert_notification()
    
    return summary 