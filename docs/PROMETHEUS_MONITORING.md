# 🔍 Prometheus Monitoring & Test Reporting

Comprehensive monitoring and alerting system for the Audio Processing Test Framework.

## 📊 Overview

The monitoring stack provides:
- **Real-time metrics** collection during test execution
- **Automated alerting** for test failures and performance issues
- **Visual dashboards** for test trends and system health
- **Historical reporting** with trend analysis

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Suite   │───▶│   Prometheus    │───▶│    Grafana      │
│   (Metrics)    │    │   (Storage)     │    │  (Dashboard)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Push Gateway   │    │  Alert Manager  │    │   Test Reports  │
│   (Metrics)     │    │   (Alerts)      │    │     (HTML)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Start Monitoring Stack
```bash
# Start all monitoring services
docker-compose up -d prometheus grafana pushgateway alertmanager

# Verify services are running
docker-compose ps
```

### 2. Access Dashboards
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093
- **Push Gateway**: http://localhost:9091

### 3. Run Tests with Monitoring
```bash
# Run tests with metrics collection
make test-all

# Check metrics
curl http://localhost:8000/metrics
```

## 📈 Metrics Collection

### Core Test Metrics
- `test_execution_total` - Total test executions (by status, category)
- `test_duration_seconds` - Test execution duration histogram
- `algorithm_processing_seconds` - Algorithm processing time
- `message_broker_operations_total` - Message broker operations
- `database_operations_total` - Database operations
- `security_test_results_total` - Security test results
- `system_health_status` - System component health

### Example Metrics Usage
```python
from prometheus_client import TEST_METRICS

# Record test execution
TEST_METRICS['test_execution_counter'].labels(
    test_type='unit', 
    status='passed'
).inc()

# Record processing time
TEST_METRICS['algorithm_processing_time'].labels(
    algorithm_name='AlgorithmA'
).observe(0.150)

# Record security test result
TEST_METRICS['security_test_results'].labels(
    test_name='jwt_validation',
    result='pass'
).inc()
```

## 🔔 Alerting Rules

### Configured Alerts

| Alert | Threshold | Severity | Description |
|-------|-----------|----------|-------------|
| `HighTestFailureRate` | >20% failures | Warning | High test failure rate detected |
| `CriticalTestFailureRate` | >50% failures | Critical | Critical failure rate - immediate attention |
| `SlowAlgorithmProcessing` | >2s (95th percentile) | Warning | Algorithm processing is slow |
| `SecurityTestFailures` | Any failure | Critical | Security tests failing |
| `DatabaseOperationFailures` | >5% error rate | Warning | Database operation failures |
| `NoTestsRunning` | No tests for 10min | Warning | No test executions detected |

### Alert Routing
```yaml
# alertmanager.yml
routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
    
  - match:
      severity: warning  
    receiver: 'warning-alerts'
```

## 📊 Grafana Dashboards

### Main Test Dashboard
- **Test Execution Rate**: Tests per minute by category
- **Pass/Fail Ratio**: Success rate trends
- **Test Duration**: Execution time percentiles
- **Algorithm Performance**: Processing time trends
- **System Health**: Component status overview

### Performance Dashboard  
- **Response Times**: API and algorithm latencies
- **Throughput**: Messages processed per second
- **Resource Usage**: CPU, memory, disk usage
- **Error Rates**: Failure rates by component

### Security Dashboard
- **Security Test Results**: Pass/fail trends
- **Vulnerability Detection**: Security alerts over time
- **Authentication Metrics**: Login attempts, failures
- **Access Patterns**: Unusual access patterns

## 📄 Test Reporting

### Automated Reports

The system generates multiple report formats:

#### HTML Reports
```bash
# Generated automatically after test runs
open test-reports/test_report_20240122_143022.html
```

#### JSON Reports
```bash
# Detailed JSON data for analysis
cat test-reports/test_report_20240122_143022.json
```

#### Prometheus Metrics Export
```bash
# Export current metrics
curl -s http://localhost:9090/api/v1/query?query=test_execution_total
```

### Report Features
- **Executive Summary**: High-level test results and trends
- **Category Breakdown**: Detailed analysis by test type
- **Failure Analysis**: Recent failures with error details
- **Performance Metrics**: Slowest tests and bottlenecks
- **Alert History**: Recent alerts and notifications
- **Trend Analysis**: Week-over-week performance comparison

## 🔧 Configuration

### Environment Variables
```bash
# Test configuration
export PROMETHEUS_PUSHGATEWAY=http://localhost:9091
export TEST_METRICS_ENABLED=true
export REPORT_OUTPUT_DIR=test-reports

# Alert configuration
export ALERT_WEBHOOK_URL=https://hooks.slack.com/...
export ALERT_EMAIL_TO=team@company.com
```

### Custom Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Define custom metrics
custom_metric = Counter(
    'custom_test_operations_total',
    'Custom test operations',
    labelnames=['operation', 'status'],
    registry=REGISTRY
)

# Use in tests
custom_metric.labels(operation='data_validation', status='success').inc()
```

## 📱 Alerting Integration

### Slack Integration
```yaml
# alertmanager.yml
receivers:
  - name: 'slack-alerts'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#test-alerts'
        title: 'Audio Processing Test Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

### Email Alerts
```yaml
receivers:
  - name: 'email-alerts'
    email_configs:
      - to: 'team@company.com'
        subject: 'Test Alert: {{ .GroupLabels.alertname }}'
        body: |
          Alert: {{ .GroupLabels.alertname }}
          Description: {{ range .Alerts }}{{ .Annotations.description }}{{ end }}
```

### Teams Integration
```yaml
receivers:
  - name: 'teams-alerts'
    webhook_configs:
      - url: 'YOUR_TEAMS_WEBHOOK_URL'
        send_resolved: true
```

## 🔍 Troubleshooting

### Common Issues

**Metrics not appearing in Prometheus:**
```bash
# Check pushgateway
curl http://localhost:9091/metrics

# Check prometheus targets
curl http://localhost:9090/api/v1/targets
```

**Alerts not firing:**
```bash
# Check alertmanager status
curl http://localhost:9093/api/v1/status

# Check alert rules
curl http://localhost:9090/api/v1/rules
```

**Grafana dashboard empty:**
```bash
# Check prometheus data source
curl http://localhost:3000/api/datasources

# Import dashboard manually
# Use dashboard ID: 12345 (custom audio processing dashboard)
```

### Debug Commands
```bash
# Check all service logs
docker-compose logs prometheus grafana alertmanager

# Test metric push
echo "test_metric 1" | curl --data-binary @- http://localhost:9091/metrics/job/test

# Query specific metric
curl 'http://localhost:9090/api/v1/query?query=up'
```

## 📚 Best Practices

### Metric Design
- **Use consistent naming**: `component_operation_total`
- **Include relevant labels**: `{test_type, status, component}`
- **Avoid high cardinality**: Limit unique label combinations
- **Use appropriate metric types**: Counter, Gauge, Histogram

### Dashboard Design
- **Focus on business metrics**: Test success rate, performance
- **Use time ranges effectively**: Last 1h, 6h, 24h, 7d
- **Include alerting thresholds**: Visual indicators for limits
- **Group related metrics**: Logical dashboard sections

### Alert Design
- **Actionable alerts only**: Each alert should require action
- **Appropriate severity levels**: Critical, Warning, Info
- **Clear descriptions**: What's wrong and how to fix it
- **Avoid alert fatigue**: Tune thresholds carefully

## 🎯 Example Queries

### Prometheus Queries
```promql
# Test failure rate over last 5 minutes
rate(test_execution_total{status="failed"}[5m]) / rate(test_execution_total[5m])

# 95th percentile test duration
histogram_quantile(0.95, rate(test_duration_seconds_bucket[5m]))

# Error rate by component
rate(message_broker_operations_total{status="error"}[5m])

# Active alerts
ALERTS{alertstate="firing"}
```

### Grafana Visualizations
- **Single Stat**: Current pass rate, total tests
- **Time Series**: Test execution trends, duration over time
- **Bar Chart**: Tests by category, failure distribution  
- **Heatmap**: Test duration distribution
- **Table**: Recent failures, slowest tests

---

**🎉 Ready for comprehensive test monitoring!** The system provides complete observability into test execution, performance, and system health with automated alerting and reporting. 