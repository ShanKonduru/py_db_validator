# Data Validation Test Framework — Understanding, Strategy & Implementation Approach

## Overview
This document describes the understanding, strategy, and implementation approach for a CSV-driven, object-oriented test automation framework in Python (3.10+) for data validation across Oracle, SQL Server, and PostgreSQL. Oracle will use the oracledb package. Tests are defined in a CSV and reference DB connection profiles stored in a JSON file; credentials are supplied via a .env file. Detailed per-test reports (JSON, markdown, HTML, CSV) are produced for each execution.

Date: 10/03/2025

---

## 1. Final Requirements (Concise)
- Language: Python 3.10+ (default; can target 3.13 if requested).
- DBs supported: Oracle (oracledb), PostgreSQL (psycopg2), SQL Server (pyodbc).
- Test definition source: CSV (each row = test). Tests can be enabled/disabled via CSV field.
- DB connection profiles: db_profiles.json (non-secret fields). Credentials from .env (DB_USER_<PROFILE>, DB_PWD_<PROFILE>). for each database USN and PWD may be needed
- Authentication: username/password only.
- Test types:
  - ConnectionTest
  - TableExistenceTest
  - PermissionsTest
  - RowExistenceTest
  - RowCountTest (SRC vs TGT)
  - ColumnToColumnTest (SRC vs TGT)
  - SchemaCompareTest (explicit per-column diffs) (SRC vs TGT)
  - SmokeTest (composed)
- Numeric tolerance: relative tolerance (configurable per-test). Null handling: NULL==NULL => PASS, NULL vs value => WARN.
- Data volume expectation: small (<1M rows) — direct comparisons by default.
- Reporting: per-test detailed reports (JSON + markdown + HTML + CSV summary). Reports stored in timestamped output folder.
- Testing: pytest used for unit tests.

---

## 2. CSV & External Configuration Design

- CSV role: primary test-definition artifact. Each row maps to a TestDefinition object.
- CSV core columns (example, extensible):
  - test_id
  - enabled (Y/N)
  - test_type (SMOKE - (CONNECTION, TABLE_EXIST, PERMISSIONS, ROW_EXISTS), REGRESSION - (ROW_COUNT, COL_TO_COL, SCHEMA_COMPARE))
  - db_type_src (Oracle, SQL Server, PostgreSQL)
  - table_src
  - column_src (comma-separated if multiple)
  - filter_src (optional WHERE clause)
  - db_type_src (Oracle, SQL Server, PostgreSQL)
  - table_tgt
  - column_tgt (comma-separated if multiple)
  - comparison_keys (comma-separated)
  - ignore_columns (comma-separated)
  - tags
  - report_level (INFO/DEBUG)
  - notes

- db_profiles.json (example structure per profile_id):
  - profile_id
  - db_type ("oracle"|"postgres"|"sqlserver")
  - host
  - port
  - service_name or database
  - driver (optional)
  - extra_params (optional)

- .env:
  - oracle_DB_USER=...
  - oracle_DB_PWD=...
  - sqlserver_DB_USER=...
  - sqlserver_DB_PWD=...
  - postgresql_DB_USER=...
  - postgresql_DB_PWD=...

Security note: Credentials are NOT stored in CSV/JSON; .env used for simplicity per requirement.

---

## 3. High-Level Architecture

Modules:
- parser
  - csv_parser.py: parses CSV rows -> TestDefinition objects; validates required fields for each test type.
  - config_loader.py: loads db_profiles.json and merges with .env secrets.
- adapters
  - base_adapter.py: DBAdapter interface (connect, execute, fetch_one, fetch_all, fetch_schema, check_permissions, close)
  - oracle_adapter.py: implements DBAdapter using oracledb
  - postgres_adapter.py: implements DBAdapter using psycopg2
  - sqlserver_adapter.py: implements DBAdapter using pyodbc
- tests
  - base_test.py: BaseTest class with lifecycle (setup, run, validate, teardown), logging, retry handling.
  - connection_test.py, table_existence_test.py, permissions_test.py, row_existence_test.py, row_count_test.py, column_to_column_test.py, schema_compare_test.py, smoke_test.py
- runner
  - orchestrator.py: reads TestDefinition list, resolves profiles, executes enabled tests sequentially (parallel optional later), handles retries/timeouts, collects results.
- reporter
  - reporter.py: writes per-test JSON, markdown, HTML reports; writes suite summary (index.md/index.html) and CSV.
- utils
  - logger.py: structured logging helper
  - sql_utils.py: helper SQL templates, safe identifier quoting, param binding
  - compare_utils.py: numeric relative tolerance comparator, null rules, diff summarizers
- tests (pytest)
  - unit tests for parser, compare_utils, adapters (mocked), and sample end-to-end using a lightweight DB or mocks.

---

## 4. Key Design Decisions & Rationale

- OOP & Modularity: BaseTest and polymorphic Test classes make adding new tests straightforward. DBAdapter interface ensures DB-specific code is centralized.
- CSV + External JSON + .env: separates test intent (CSV) from environment-specific config (JSON) and secrets (.env). This keeps tests portable and secure.
- oracledb for Oracle: per your requirement. Use thin mode by default; thick optional if needed.
- pyodbc for SQL Server: broad driver compatibility.
- Relative tolerance comparator for numeric columns: flexible for floating point differences.
- Null handling as specified: NULL==NULL pass; NULL vs value becomes WARN (not fail).
- Schema comparison: explicit per-column metadata diffs (name, type, precision/scale, nullability, default) — no auto-generated SQL transformations.
- Small data volumes: direct joins and in-memory comparison acceptable; code will fetch only required columns and use limit/sample parameters for report examples.
- Reporting: per-test JSON for automation; markdown/HTML for human consumption. Files written to timestamped output folder per run.

---

## 5. Test Execution Flow (Sequence)

1. Runner invoked with CSV path, db_profiles.json path, output folder (optional).
2. Config loader reads db_profiles.json and loads .env secrets into profile objects.
3. CSV parser reads CSV, validates rows, converts to TestDefinition objects.
4. Orchestrator filters enabled tests and sorts by optional priority/tag.
5. For each TestDefinition:
   - Instantiate appropriate Test class with adapters for profile_src/profile_tgt.
   - Test.setup(): adapters connect, optional pre-checks.
   - Test.run(): perform validation logic (issue SQL, compare results).
   - Test.validate(): apply comparator rules, determine PASS/WARN/FAIL, collect mismatch samples.
   - Test.teardown(): close connections, cleanup.
   - Reporter writes per-test report (JSON + markdown + HTML), and logs details.
6. After all tests, orchestrator writes aggregated summary report (index.md/index.html, summary.json, summary.csv).
7. Exit with non-zero return code if any test failed (configurable).

---

## 6. Test Implementations — Key Details

- ConnectionTest:
  - Attempt connection via adapter; run simple SELECT 1 or DB-specific connectivity check.
  - Report: connection time, any warnings.

- TableExistenceTest:
  - Adapter.fetch_schema or metadata query to check presence of schema.table.
  - Report: existence boolean, table metadata (column list summary).

- PermissionsTest:
  - Accept permissions_list or default to ["SELECT"].
  - Adapter implements check_permissions(profile_user, object, permission) using engine-specific queries.
  - Report: per-permission pass/fail, missing grants.

- RowExistenceTest:
  - Execute SELECT 1 FROM table WHERE <filter> FETCH FIRST 1 ROW ONLY.
  - Report: sample row (if any), pass/fail.

- RowCountTest:
  - Execute SELECT COUNT(*) FROM table [WHERE filter]
  - If SRC-TGT: compare counts; PASS if equal or within configured bounds.
  - Report: counts, delta, pass/fail.

- ColumnToColumnTest:
  - Requires comparison_keys; if absent, use primary key metadata (if available) or fail.
  - Build query joining SRC and TGT on keys, selecting comparison columns.
  - For numeric columns, use relative tolerance: abs(a-b)/max(abs(a), abs(b), eps) <= tolerance.
  - Null rules applied; NULL vs value => WARN.
  - Report: row mismatch count, per-column mismatch counts, samples (configurable up to default 20).

- SchemaCompareTest:
  - Adapter.fetch_schema returns list of ColumnMetadata (name, type, precision, scale, nullable, default).
  - Compare columns one-by-one; report differences: missing columns, type mismatches, precision/scale diffs, nullability diffs.
  - Report: detailed column-wise diff table and summary counts.

- SmokeTest:
  - Composite test: ConnectionTest + TableExistenceTest + RowExistenceTest (configurable).
  - Report: aggregated status and component reports.

---

## 7. Reporting Specification

Per-test report contents:
- test_id, test_type, description, tags
- status: PASS / FAIL / WARN / ERROR
- start_time, end_time, duration_ms
- profiles used (profile_id only, no secrets)
- queries executed (with parameters; sanitized)
- expected vs actual (counts, schema diffs, mismatch stats)
- mismatch samples (up to N rows; N default 20; configurable)
- warnings and stack traces (on ERROR)
- per-column mismatch summary (for column comparisons)
- file outputs: <output_folder>/<timestamp>/<test_id>.json, .md, .html

Suite summary:
- index.md / index.html with table of tests, statuses, counts of PASS/FAIL/WARN/ERROR, run duration, link to per-test reports
- summary.json and summary.csv for CI/automation consumption

---

## 8. Error Handling, Retries & Timeouts

- Retry policy: per-test retry_count (default 0). Orchestrator retries transient failures (connection timeouts, transient SQL errors) according to retry_count with exponential backoff.
- Timeout: per-test timeout_sec (default configurable). If exceeded, test marked ERROR/FAIL and reported.
- Error classification:
  - CONFIG_ERROR: missing required CSV fields, invalid profile references
  - TRANSIENT_ERROR: connection/timeouts — eligible for retries
  - ASSERTION_FAILURE: validation asserts failed — final FAIL
  - UNEXPECTED_ERROR: runtime exception — ERROR, log stacktrace

---

## 9. Extensibility & Quality

- Clear interfaces: DBAdapter and BaseTest make adding DBs/tests straightforward.
- Plugin hooks: allow registering custom tests or adapters via entrypoints or a plugins folder.
- Type hints and unit tests (pytest). Use mocks for DB adapters in unit tests.
- Linting: black, flake8, mypy recommended.

---

## 10. Implementation Deliverables (Planned Next Steps)

1. Sample artifacts:
   - db_profiles.json (sample)
   - .env.template
   - sample_tests.csv with examples covering each test type
2. Architecture artefacts:
   - class list with method signatures
   - sequence flow description
3. Starter Python codebase skeleton with:
   - CSV parser -> TestDefinition
   - DBAdapter interface + OracleAdapter (oracledb), PostgresAdapter (psycopg2), SqlServerAdapter (pyodbc)
   - BaseTest and implementations for ConnectionTest, TableExistenceTest, RowCountTest, ColumnToColumnTest, SchemaCompareTest, SmokeTest
   - Orchestrator/runner and reporter (JSON + markdown + HTML)
   - pytest unit tests for parser and utilities (adapters mocked)
4. Documentation:
   - README with run instructions and examples
   - Developer guide for adding adapters/tests
   - Sample reports produced by example run


Feature 1 — Project Setup & Foundations

User Story 1.1 — Repo and environment baseline
Tasks:
Create project repository (git) with initial README and LICENSE
Add .gitignore, .editorconfig, and basic repo conventions
Create Python 3.13.7 virtualenv and requirements.txt placeholder
Add pre-commit hooks (black, isort, flake8)
Add CONTRIBUTING.md and code style guidance
User Story 1.2 — Development utilities & templates
Tasks:
Create .env.template
Create db_profiles.json.sample
Create sample_tests.csv template
Create folder structure (docs/, src/, tests/, examples/, reports/)
Add issue / PR templates
Feature 2 — Configuration & Secret Handling

User Story 2.1 — Load and validate DB profiles
Tasks:
Define db_profiles.json schema and validation rules
Implement config_loader to read db_profiles.json
Add unit tests for config_loader (valid/invalid profiles)
User Story 2.2 — .env integration and secret resolution
Tasks:
Implement .env loader (dotenv) to map DB_USER_, DB_PWD_
Add validation that profiles referenced in CSV have credentials available
Add error messages for missing secrets
Unit tests for .env resolver
Feature 3 — CSV Test Definition Parser

User Story 3.1 — Define CSV schema & samples
Tasks:
Finalize CSV columns and field definitions (mandatory per test type)
Produce example CSV rows covering all test types
Document CSV format in README/docs
User Story 3.2 — Implement CSV parser to TestDefinition objects
Tasks:
Implement csv_parser module: read, validate rows, convert to TestDefinition dataclasses
Implement per-TestType validation logic (required fields, allowed values)
Add unit tests for csv_parser (valid/invalid cases)
User Story 3.3 — Support tagging, filtering, and enable/disable flag
Tasks:
Add run-group/tags parsing
Implement filtering API to select tests by tag/TestID/enabled
Unit tests for filtering behavior
Feature 4 — Database Adapter Layer

User Story 4.1 — Define DBAdapter interface
Tasks:
Create base_adapter interface with methods: connect(), execute(), fetch_one(), fetch_all(), fetch_schema(), check_permissions(), close()
Add type hints and docs
Unit tests for interface compliance (mocks)
User Story 4.2 — Oracle adapter (oracledb)
Tasks:
Implement oracle_adapter using oracledb (thin mode default)
Implement connection, execute, fetch_schema (ALL_TAB_COLUMNS query), permission checks
Add error mapping for common Oracle errors
Unit tests (mock oracledb)
User Story 4.3 — PostgreSQL adapter (psycopg2)
Tasks:
Implement postgres_adapter using psycopg2
Implement metadata fetch via information_schema, permission checks
Unit tests (mock psycopg2)
User Story 4.4 — SQL Server adapter (pyodbc)
Tasks:
Implement sqlserver_adapter using pyodbc
Implement metadata queries and permission checks
Unit tests (mock pyodbc)
User Story 4.5 — Adapter utils & dialect handling
Tasks:
Implement helper utilities for quoting identifiers and type mapping
Implement unified ColumnMetadata dataclass returned by fetch_schema
Unit tests for mapping and quoting
Feature 5 — Core Test Classes & Validators

User Story 5.1 — BaseTest lifecycle & utilities
Tasks:
Implement BaseTest class with setup(), run(), validate(), teardown(), retry handling, timeout support
Implement standardized TestResult dataclass capturing status, times, messages, artifacts
Unit tests for lifecycle and retry behavior (mock adapters)
User Story 5.2 — ConnectionTest, TableExistenceTest, RowExistenceTest
Tasks:
Implement ConnectionTest, TableExistenceTest, RowExistenceTest
Add unit tests for each (mocks)
User Story 5.3 — RowCountTest
Tasks:
Implement RowCountTest: single DB and SRC-TGT comparison
Implement delta/tolerance config support
Unit tests
User Story 5.4 — ColumnToColumnTest
Tasks:
Implement join-based comparison using comparison_keys
Implement relative tolerance comparator for numeric columns
Implement null handling rules (NULL==NULL pass; NULL vs value => WARN)
Implement per-column mismatch counters and sample extraction (configurable sample size)
Unit tests
User Story 5.5 — SchemaCompareTest
Tasks:
Implement explicit column-by-column metadata comparison
Implement engine-agnostic type equivalence mapping
Generate structured diff output
Unit tests
User Story 5.6 — PermissionsTest
Tasks:
Implement permission mapping per DB type and adapter.check_permissions calls
Allow CSV to override exact permissions list
Unit tests
User Story 5.7 — SmokeTest (composed)
Tasks:
Implement SmokeTest composition (connection + table exists + min row existence)
Configurable components per-smoke-test row in CSV
Unit tests
Feature 6 — Runner / Orchestrator

User Story 6.1 — Runner core & scheduling
Tasks:
Implement orchestrator to read parsed tests and profiles, resolve credentials, and prepare execution list
Implement sequential executor (initial)
Implement retry and timeout enforcement per-test
Unit tests for orchestrator behavior (mock tests/adapters)
User Story 6.2 — Parallel execution (optional / later)
Tasks:
Design thread/process-based parallel runner (configurable concurrency)
Implement safe adapter resource handling and connection pooling
Integration tests to ensure stability under concurrency
User Story 6.3 — Exit codes and orchestration options
Tasks:
Implement CLI arguments: CSV path, db_profiles path, output folder, tags filter, parallelism, verbosity
Implement exit codes: 0 = all pass, non-zero if any FAIL/ERROR (configurable)
Add integration tests for CLI
Feature 7 — Reporting & Artifacts

User Story 7.1 — TestResult format & storage
Tasks:
Define TestResult JSON schema
Implement reporter interface for writers (JSONWriter, CSVWriter)
Unit tests for writer outputs
User Story 7.2 — Markdown & HTML per-test reports
Tasks:
Implement markdown renderer for per-test detailed reports
Implement HTML renderer (Bootstrap template) for per-test and index
Implement configuration for sample mismatch rows (per-run/per-test)
Unit tests for rendering correctness
User Story 7.3 — Aggregated suite report (index)
Tasks:
Implement suite index page (index.md/index.html) with links and summary metrics
Implement summary.json and summary.csv outputs
Unit/integration tests for aggregated outputs
User Story 7.4 — Report retention and output structure
Tasks:
Implement timestamped run folder creation and cleanup policy (optional retention days)
Add config to specify output folder and sampling size
Tests for folder creation and file permissions
Feature 8 — Logging, Monitoring & Diagnostics

User Story 8.1 — Structured logging
Tasks:
Implement structured logger (JSON lines) with levels and correlation_id per test
Add console-friendly log formatting
Add unit tests for logs (capture & assert)
User Story 8.2 — Error classification & diagnostics
Tasks:
Implement standardized exception types (ConfigError, TransientError, AssertionFailure, AdapterError)
Ensure stack traces are captured in reports for ERROR cases
Unit tests for exception handling
Feature 9 — Testing Strategy & Test Coverage

User Story 9.1 — Unit tests
Tasks:
Add pytest-based unit tests for parser, adapters (mocked), utils, and validators
Aim for strong coverage on core modules
User Story 9.2 — Integration tests (mocked/live)
Tasks:
Create integration test harness with mocks or lightweight containers (optional)
Provide sample integration run documentation
Feature 10 — Documentation & Examples

User Story 10.1 — User docs
Tasks:
Write README: overview, quickstart, CSV schema, db_profiles.json sample, .env usage, running runner
Add example commands and sample outputs
User Story 10.2 — Developer docs
Tasks:
Document architecture, class diagram, module responsibilities
Provide guide to add new adapters and tests
Provide code-level docstrings and type hints
User Story 10.3 — Example artifacts
Tasks:
Provide sample db_profiles.json, .env.template, and sample_tests.csv covering all test types
Provide example reports produced by a sample run
Backlog — Future Enhancements (no CI/CD work)

Secrets manager integration (Vault, AWS) — research & backlog
Performance & large-data strategies — checksum/partitioned comparisons
Additional DB support (if requested later)