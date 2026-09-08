.PHONY: doctor check test test-integration test-template telemetry-check telemetry-summary

doctor:
	./scripts/repo-doctor

# Project-owned gates are intentionally fail-closed in the reusable template.
# Replace these recipes before relying on CI in a repository created from the template.
check:
	@echo "NOT CONFIGURED: replace 'make check' with formatter/linter/type-check commands for your project" >&2
	@exit 2

test:
	@echo "NOT CONFIGURED: replace 'make test' with unit-test commands for your project" >&2
	@exit 2

test-integration:
	@echo "NOT CONFIGURED: replace 'make test-integration' with integration/e2e commands for your project" >&2
	@exit 2

test-template:
	python3 -m unittest discover -s template_tests -p 'test_*.py'

telemetry-check:
	python3 scripts/validate-telemetry.py

telemetry-summary:
	python3 scripts/telemetry-summary.py
