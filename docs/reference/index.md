# Reference

The Reference section contains the complete technical documentation for `mav-grid` — the CLI, the Python API, and test coverage reports.

## In This Section

<div class="grid cards" markdown>

-   **[:material-console: CLI](cli.md)**

    Command-line usage and subcommands.

-   **[:material-api: Python API](python_api/index.md)**

    Complete public Python API documentation.

-   **[:material-shield-check: Python Tests](python_coverage.md)**

    Python coverage reports for unit, integration, functional, and E2E tests.

</div>

## Python API Usage

```python
from mav_grid import (
    SPEC_VERSION,
    LoggingSettings,
    configure_logger,
    get_settings,
    logger,
)

configure_logger(LoggingSettings(enabled=True, level="INFO"))
logger.info(
    "Targeting spec {} with output in {}", SPEC_VERSION, get_settings().output_dir
)
```
