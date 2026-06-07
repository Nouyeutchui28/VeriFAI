# 📊 VeriFAI LLM: Quality & Test Metrics Framework

This document defines the metrics used to evaluate the health, security, and performance of the VeriFAI LLM project. These benchmarks are enforced via CI/CD pipelines.

## 1. Code Quality Metrics
| Metric | Target | Current | Status |
| :--- | :--- | :--- | :--- |
| **Test Coverage** | > 80% | ~25% | 🟠 Warning |
| **Linting Score (Pylint)** | > 9.0/10 | TBD | ⚪ Pending |
| **Cyclomatic Complexity** | < 10 per function | TBD | ⚪ Pending |
| **Dependency Security** | 0 Critical Vulnerabilities | 0 | 🟢 Pass |

## 2. Security Analysis Metrics (Scanning Performance)
| Metric | Description | Target Benchmark |
| :--- | :--- | :--- |
| **False Positive Rate** | Percentage of flagged issues that are not bugs. | < 15% |
| **Scan Latency (Small)** | Time to scan < 100 lines of code. | < 3 seconds |
| **Scan Latency (Large)** | Time to scan > 5,000 lines of code. | < 45 seconds |
| **Vulnerability Detection** | Success rate in finding known OWASP vulnerabilities. | > 90% |

## 3. System Reliability Metrics
| Metric | Description | Target Benchmark |
| :--- | :--- | :--- |
| **API Response Time** | Average time for backend requests. | < 500ms |
| **Uptime** | Percentage of time the service is available. | 99.9% |
| **Error Rate** | Percentage of failed analysis requests. | < 1% |
| **LLM Recovery Rate** | Success rate of auto-retries on LLM timeouts. | > 95% |

## 4. Test Suite Composition
| Category | Metric | Description |
| :--- | :--- | :--- |
| **Unit Tests** | ~30 Tests | Validates individual core functions (validators, loggers). |
| **Security Tests** | ~20 Tests | Specifically attempts to bypass validators (Path traversal, SQLi). |
| **Integration Tests** | ~10 Tests | Verifies the connection between Frontend, Backend, and LLM. |
| **Performance Tests** | ~5 Tests | Benchmarks analysis speed under heavy load. |

## 5. Continuous Improvement Tracking
- **Quarterly Goal:** Increase test coverage by 15% every 3 months.
- **Immediate Task:** Implement automated complexity checking in the `.github/workflows/quality.yml` pipeline.
