#!/usr/bin/env python3
"""
XML to HTML Test Report Converter
Automatically converts pytest XML results to enhanced HTML reports
"""
import xml.etree.ElementTree as ET
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import argparse


class XMLToHTMLConverter:
    """Convert pytest XML results to enhanced HTML reports"""
    
    def __init__(self, xml_file: str, output_file: str = None):
        self.xml_file = xml_file
        self.output_file = output_file or xml_file.replace('.xml', '_report.html')
        self.test_data = None
    
    def parse_xml(self) -> Dict[str, Any]:
        """Parse pytest XML file and extract test data"""
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
        except Exception as e:
            print(f"??? Error parsing XML file {self.xml_file}: {e}")
            return None
        
        # Handle both single testsuite and testsuites with multiple suites
        testsuites = []
        if root.tag == 'testsuites':
            testsuites = root.findall('testsuite')
        elif root.tag == 'testsuite':
            testsuites = [root]
        else:
            print(f"??? Unknown XML format in {self.xml_file}")
            return None
        
        all_test_cases = []
        total_time = 0
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0
        
        # Process all test suites
        for testsuite in testsuites:
            suite_name = testsuite.get('name', 'Unknown Suite')
            
            # Parse test cases from this suite
            for testcase in testsuite.findall('testcase'):
                test_info = {
                    'name': testcase.get('name', 'Unknown'),
                    'classname': testcase.get('classname', 'Unknown'),
                    'time': float(testcase.get('time', 0)),
                    'status': 'passed',
                    'error_message': None,
                    'failure_message': None,
                    'skipped_message': None,
                    'suite': suite_name
                }
                
                # Check for failure
                failure = testcase.find('failure')
                if failure is not None:
                    test_info['status'] = 'failed'
                    test_info['failure_message'] = failure.text or failure.get('message', '')
                    total_failures += 1
                
                # Check for error
                error = testcase.find('error')
                if error is not None:
                    test_info['status'] = 'error'
                    test_info['error_message'] = error.text or error.get('message', '')
                    total_errors += 1
                
                # Check for skipped
                skipped = testcase.find('skipped')
                if skipped is not None:
                    test_info['status'] = 'skipped'
                    test_info['skipped_message'] = skipped.text or skipped.get('message', '')
                    total_skipped += 1
                
                all_test_cases.append(test_info)
                total_time += test_info['time']
                total_tests += 1
        
        # Calculate summary
        passed = total_tests - total_failures - total_errors - total_skipped
        
        return {
            'metadata': {
                'name': f"Test Results ({len(testsuites)} suite{'s' if len(testsuites) > 1 else ''})",
                'tests': total_tests,
                'failures': total_failures,
                'errors': total_errors,
                'skipped': total_skipped,
                'time': total_time,
                'timestamp': datetime.now().isoformat(),
                'source_file': os.path.basename(self.xml_file)
            },
            'test_cases': all_test_cases,
            'summary': {
                'total': total_tests,
                'passed': passed,
                'failed': total_failures + total_errors,
                'skipped': total_skipped,
                'pass_rate': passed / total_tests if total_tests > 0 else 0,
                'total_time': total_time,
                'avg_time': total_time / total_tests if total_tests > 0 else 0
            }
        }
    
    def generate_html_report(self) -> str:
        """Generate comprehensive HTML report"""
        if not self.test_data:
            self.test_data = self.parse_xml()
            if not self.test_data:
                return None
        
        metadata = self.test_data['metadata']
        summary = self.test_data['summary']
        test_cases = self.test_data['test_cases']
        
        # Color coding based on pass rate
        pass_rate = summary['pass_rate']
        if pass_rate >= 0.95:
            status_color = '#28a745'
            status_text = 'EXCELLENT'
            status_icon = '????'
        elif pass_rate >= 0.80:
            status_color = '#ffc107'
            status_text = 'GOOD'
            status_icon = '???'
        elif pass_rate >= 0.60:
            status_color = '#fd7e14'
            status_text = 'NEEDS IMPROVEMENT'
            status_icon = '??????'
        else:
            status_color = '#dc3545'
            status_text = 'CRITICAL'
            status_icon = '????'
        
        # Group tests by category/class
        test_categories = {}
        for test in test_cases:
            # Extract category from classname (e.g., test_algorithms.TestAlgorithmA -> TestAlgorithmA)
            category = test['classname'].split('.')[-1] if '.' in test['classname'] else test['classname']
            category = category.replace('Test', '').replace('test_', '') or 'General'
            
            if category not in test_categories:
                test_categories[category] = []
            test_categories[category].append(test)
        
        # Generate category statistics
        category_stats = {}
        for category, tests in test_categories.items():
            total = len(tests)
            passed = len([t for t in tests if t['status'] == 'passed'])
            failed = len([t for t in tests if t['status'] in ['failed', 'error']])
            skipped = len([t for t in tests if t['status'] == 'skipped'])
            
            category_stats[category] = {
                'total': total,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'pass_rate': passed / total if total > 0 else 0,
                'avg_time': sum(t['time'] for t in tests) / total if total > 0 else 0
            }
        
        # Find slowest and failed tests
        slowest_tests = sorted(test_cases, key=lambda x: x['time'], reverse=True)[:10]
        failed_tests = [t for t in test_cases if t['status'] in ['failed', 'error']]
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - Audio Processing System</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            background: #f8f9fa;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 30px; 
            border-radius: 12px; 
            margin-bottom: 30px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header .subtitle {{ font-size: 1.2em; opacity: 0.9; margin-bottom: 15px; }}
        
        .status-badge {{ 
            display: inline-flex; 
            align-items: center; 
            gap: 8px; 
            background: {status_color}; 
            color: white; 
            padding: 12px 20px; 
            border-radius: 25px; 
            font-weight: bold; 
            font-size: 1.1em;
        }}
        
        .metrics-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }}
        .metric-card {{ 
            background: white; 
            padding: 25px; 
            border-radius: 12px; 
            box-shadow: 0 2px 15px rgba(0,0,0,0.08); 
            text-align: center;
            transition: transform 0.2s ease;
        }}
        .metric-card:hover {{ transform: translateY(-2px); }}
        .metric-value {{ font-size: 2.8em; font-weight: bold; margin-bottom: 8px; }}
        .metric-label {{ font-size: 0.9em; color: #666; text-transform: uppercase; letter-spacing: 1px; }}
        .metric-value.passed {{ color: #28a745; }}
        .metric-value.failed {{ color: #dc3545; }}
        .metric-value.skipped {{ color: #6c757d; }}
        
        .section {{ 
            background: white; 
            margin-bottom: 30px; 
            border-radius: 12px; 
            box-shadow: 0 2px 15px rgba(0,0,0,0.08); 
            overflow: hidden; 
        }}
        .section-header {{ 
            background: #f8f9fa; 
            padding: 20px; 
            border-bottom: 1px solid #dee2e6; 
        }}
        .section-header h2 {{ color: #495057; margin: 0; display: flex; align-items: center; gap: 10px; }}
        .section-content {{ padding: 20px; }}
        
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 14px 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ 
            background: #f8f9fa; 
            font-weight: 600; 
            color: #495057; 
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        tr:hover {{ background: #f8f9fa; }}
        
        .status-passed {{ color: #28a745; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .status-skipped {{ color: #6c757d; font-weight: bold; }}
        .status-error {{ color: #fd7e14; font-weight: bold; }}
        
        .progress-bar {{ 
            background: #e9ecef; 
            border-radius: 10px; 
            overflow: hidden; 
            height: 12px; 
            position: relative;
        }}
        .progress-fill {{ 
            height: 100%; 
            transition: width 0.6s ease-in-out; 
            border-radius: 10px;
        }}
        .progress-passed {{ background: linear-gradient(90deg, #28a745, #20c997); }}
        
        .test-details {{ 
            background: #f8d7da; 
            padding: 15px; 
            margin-top: 10px; 
            border-radius: 8px; 
            border-left: 4px solid #dc3545; 
        }}
        .test-details pre {{ 
            white-space: pre-wrap; 
            word-wrap: break-word; 
            font-size: 0.9em; 
            font-family: 'Monaco', 'Consolas', monospace;
            margin: 0;
        }}
        
        .collapsible {{ cursor: pointer; transition: background 0.2s; }}
        .collapsible:hover {{ background: #e9ecef; }}
        
        .footer {{ 
            text-align: center; 
            padding: 30px; 
            color: #6c757d; 
            font-size: 0.9em; 
            background: white;
            border-radius: 12px;
            margin-top: 20px;
        }}
        
        .no-tests {{ 
            text-align: center; 
            padding: 40px; 
            color: #6c757d; 
            font-style: italic; 
        }}
        
        .timestamp {{ 
            font-size: 0.9em; 
            opacity: 0.8; 
            margin-top: 10px; 
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            .metrics-grid {{ grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }}
            .header h1 {{ font-size: 2em; }}
            table {{ font-size: 0.9em; }}
            th, td {{ padding: 10px 8px; }}
        }}
    </style>
    <script>
        function toggleDetails(element) {{
            const details = element.nextElementSibling;
            if (details && details.style.display === 'none') {{
                details.style.display = 'table-row';
                element.style.background = '#fff3cd';
            }} else if (details) {{
                details.style.display = 'none';
                element.style.background = '';
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            // Animate progress bars
            setTimeout(() => {{
                document.querySelectorAll('.progress-fill').forEach(bar => {{
                    const width = bar.getAttribute('data-width');
                    if (width) bar.style.width = width + '%';
                }});
            }}, 500);
        }});
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>???? Audio Processing Test Report</h1>
            <div class="subtitle">Automated Test Results Analysis</div>
            <div class="status-badge">
                <span>{status_icon}</span>
                <span>{status_text} - {pass_rate:.1%} Pass Rate</span>
            </div>
            <div class="timestamp">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
                Source: {metadata['source_file']} | 
                Duration: {summary['total_time']:.2f}s
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{summary['total']}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric-card">
                <div class="metric-value passed">{summary['passed']}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value failed">{summary['failed']}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value skipped">{summary['skipped']}</div>
                <div class="metric-label">Skipped</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{summary['total_time']:.2f}s</div>
                <div class="metric-label">Total Time</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{summary['avg_time']:.3f}s</div>
                <div class="metric-label">Avg Time</div>
            </div>
        </div>
        
        {self._generate_category_section(category_stats)}
        {self._generate_failed_tests_section(failed_tests)}
        {self._generate_slowest_tests_section(slowest_tests)}
        
        <div class="footer">
            <p><strong>Audio Processing System Test Framework</strong></p>
            <p>Report auto-generated from: {metadata['source_file']}</p>
            <p>???? <a href="{self.xml_file}" style="color: #667eea;">View Raw XML Results</a></p>
        </div>
    </div>
</body>
</html>
"""
        return html_content
    
    def _generate_category_section(self, category_stats: Dict[str, Any]) -> str:
        """Generate test categories section"""
        if not category_stats:
            return ""
        
        rows = []
        for category, stats in sorted(category_stats.items()):
            pass_rate = stats['pass_rate']
            progress_width = pass_rate * 100
            
            rows.append(f"""
                <tr>
                    <td><strong>{category}</strong></td>
                    <td>{stats['total']}</td>
                    <td class="status-passed">{stats['passed']}</td>
                    <td class="status-failed">{stats['failed']}</td>
                    <td class="status-skipped">{stats['skipped']}</td>
                    <td><strong>{pass_rate:.1%}</strong></td>
                    <td>{stats['avg_time']:.3f}s</td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-fill progress-passed" data-width="{progress_width}" style="width: 0%"></div>
                        </div>
                    </td>
                </tr>
            """)
        
        return f"""
        <div class="section">
            <div class="section-header">
                <h2>???? Test Categories</h2>
            </div>
            <div class="section-content">
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Total</th>
                            <th>Passed</th>
                            <th>Failed</th>
                            <th>Skipped</th>
                            <th>Pass Rate</th>
                            <th>Avg Time</th>
                            <th>Progress</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    def _generate_failed_tests_section(self, failed_tests: List[Dict[str, Any]]) -> str:
        """Generate failed tests section"""
        if not failed_tests:
            return """
            <div class="section">
                <div class="section-header">
                    <h2>??? No Failed Tests</h2>
                </div>
                <div class="section-content">
                    <div class="no-tests">
                        <h3>???? All tests passed successfully!</h3>
                        <p>Your test suite is working perfectly.</p>
                    </div>
                </div>
            </div>
            """
        
        rows = []
        for i, test in enumerate(failed_tests):
            error_msg = test.get('failure_message') or test.get('error_message', 'No error message available')
            # Truncate very long error messages
            if len(error_msg) > 500:
                error_msg = error_msg[:500] + "... (truncated)"
            
            rows.append(f"""
                <tr class="collapsible" onclick="toggleDetails(this)">
                    <td>{i+1}</td>
                    <td><strong>{test['name']}</strong></td>
                    <td>{test['classname']}</td>
                    <td class="status-{test['status']}">{test['status'].upper()}</td>
                    <td>{test['time']:.3f}s</td>
                    <td style="cursor: pointer;">??????? Click for Details</td>
                </tr>
                <tr style="display: none;">
                    <td colspan="6">
                        <div class="test-details">
                            <strong>Error Details:</strong>
                            <pre>{error_msg}</pre>
                        </div>
                    </td>
                </tr>
            """)
        
        return f"""
        <div class="section">
            <div class="section-header">
                <h2>??? Failed Tests ({len(failed_tests)})</h2>
            </div>
            <div class="section-content">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Test Name</th>
                            <th>Class</th>
                            <th>Status</th>
                            <th>Duration</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    def _generate_slowest_tests_section(self, slowest_tests: List[Dict[str, Any]]) -> str:
        """Generate slowest tests section"""
        if not slowest_tests:
            return ""
        
        # Only show tests that actually took some time
        significant_tests = [t for t in slowest_tests if t['time'] > 0.001][:10]
        
        if not significant_tests:
            return ""
        
        rows = []
        for i, test in enumerate(significant_tests):
            status_class = f"status-{test['status']}"
            
            # Add visual indicator for really slow tests
            time_indicator = ""
            if test['time'] > 5.0:
                time_indicator = "????"
            elif test['time'] > 2.0:
                time_indicator = "???"
            elif test['time'] > 1.0:
                time_indicator = "????"
            
            rows.append(f"""
                <tr>
                    <td>{i+1}</td>
                    <td><strong>{test['name']}</strong></td>
                    <td>{test['classname']}</td>
                    <td class="{status_class}">{test['status'].upper()}</td>
                    <td><strong>{time_indicator} {test['time']:.3f}s</strong></td>
                </tr>
            """)
        
        return f"""
        <div class="section">
            <div class="section-header">
                <h2>???? Slowest Tests (Top {len(significant_tests)})</h2>
            </div>
            <div class="section-content">
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Test Name</th>
                            <th>Class</th>
                            <th>Status</th>
                            <th>Duration</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    def convert(self) -> str:
        """Convert XML to HTML and save the file"""
        html_content = self.generate_html_report()
        
        if not html_content:
            return None
        
        try:
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"??? HTML report generated: {self.output_file}")
            return self.output_file
        
        except Exception as e:
            print(f"??? Error writing HTML file {self.output_file}: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description='Convert pytest XML results to HTML report')
    parser.add_argument('xml_file', help='Input XML file path')
    parser.add_argument('-o', '--output', help='Output HTML file path')
    parser.add_argument('--open', action='store_true', help='Open HTML report in browser')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.xml_file):
        print(f"??? Error: XML file '{args.xml_file}' not found")
        return 1
    
    try:
        converter = XMLToHTMLConverter(args.xml_file, args.output)
        output_file = converter.convert()
        
        if output_file and args.open:
            import webbrowser
            webbrowser.open(f'file://{os.path.abspath(output_file)}')
            print(f"???? Opening report in browser...")
        
        return 0 if output_file else 1
    
    except Exception as e:
        print(f"??? Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
