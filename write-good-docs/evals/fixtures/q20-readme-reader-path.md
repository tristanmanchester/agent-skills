# Ledgerpeek

Welcome to Ledgerpeek, a powerful, seamless, and comprehensive solution for inspection. In today's data-driven world, viewing tabular data is more important than ever. This README will cover its capabilities and tell you everything you need to know.

## Architecture

The CLI parses arguments and calls its inspection module. The inspection module opens a local CSV file and prints a structural summary. It does not modify that file. These facts mean the CLI can summarize local CSV structure without editing the input.

## Benefits

Ledgerpeek helps you inspect CSV structure. A key benefit is being able to view a summary of your local CSV file. This is useful for viewing structure.

## Example

Run `ledgerpeek inspect sample.csv --format json`. Replace `sample.csv` with your local CSV file path. The command prints JSON to standard output; a successful run exits with code 0.

## Install

Run `pipx install ledgerpeek==1.4.0`. Before installation, Python 3.10 or later and pipx must already be installed. No instructions for installing those prerequisites are supplied.

## Configuration

`LEDGERPEEK_FORMAT` sets the default output format to `json` or `text`; if unset, the default is `text`. An explicit `--format` overrides the environment variable.

## Support

Report reproducible problems at https://example.org/ledgerpeek/support. Include the version and a redacted example; do not upload private data.

## Conclusion

In conclusion, Ledgerpeek is a comprehensive tool for inspecting local CSV files and understanding their structure. We hope this guide has been helpful.
