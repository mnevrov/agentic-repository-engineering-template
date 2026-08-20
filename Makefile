.PHONY: doctor check test test-integration test-template telemetry-check telemetry-summary

doctor:
	./scripts/repo-doctor

check:
	@echo "TODO: replace with formatter/linter/type-check commands for your project"

# Intentional placeholder: configure this before relying on the template.
test:
	@echo "TODO: replace with unit-test command for your project"

test-integration:
	@echo "TODO: replace with integration/e2e command for your project"

test-template:
	python3 tests/test_telemetry.py

telemetry-check:
	python3 scripts/validate-telemetry.py

telemetry-summary:
	python3 scripts/telemetry-summary.py
