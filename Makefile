.PHONY: doctor check test test-integration test-template telemetry-check telemetry-summary opencode-acceptance

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
	@test ! -L template_tests || { echo 'NOT CONFIGURED: symlinked template_tests is unsupported' >&2; exit 2; }
	@find template_tests -maxdepth 1 -type f -name 'test_*.py' 2>/dev/null | grep -q . || { echo 'NOT CONFIGURED: template_tests are missing' >&2; exit 2; }
	python3 -m unittest discover -s template_tests -p 'test_*.py'

telemetry-check:
	python3 scripts/validate-telemetry.py

telemetry-summary:
	python3 scripts/telemetry-summary.py

opencode-acceptance:
	python3 scripts/opencode-acceptance.py
