import click
import os
import importlib.util
import inspect
from dataclasses import dataclass
from typing import List, Callable
from pathlib import Path
import sys

from reftrace import Module

@dataclass
class ModuleError:
    line: int
    error: str

@dataclass
class ModuleWarning:
    line: int
    warning: str

@dataclass
class LintResults:
    module_path: str
    errors: List[ModuleError]
    warnings: List[ModuleWarning]

def load_rules(rules_file: str = "rules.py") -> List[Callable]:
    """Load all functions starting with 'rule_' from rules.py"""
    if not os.path.exists(rules_file):
        click.secho(f"No {rules_file} found in current directory", fg="red")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("rules", rules_file)
    rules_module = importlib.util.module_from_spec(spec)
    
    # Inject our classes into the module's namespace
    rules_module.LintResults = LintResults
    rules_module.ModuleError = ModuleError
    rules_module.ModuleWarning = ModuleWarning
    
    spec.loader.exec_module(rules_module)

    rules = []
    for name, obj in inspect.getmembers(rules_module):
        if name.startswith("rule_") and inspect.isfunction(obj):
            rules.append(obj)
    
    return rules

def find_nf_files(directory: str) -> List[str]:
    """Recursively find all .nf files in directory"""
    nf_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".nf"):
                nf_files.append(os.path.join(root, file))
    return nf_files

def run_lint(directory: str, rules_file: str) -> List[LintResults]:
    """Main linting function"""
    results = []
    
    # Load rules
    rules = load_rules(rules_file)
    if not rules:
        click.secho(f"No rules found in {rules_file}", fg="yellow")
        return results

    # Find .nf files
    nf_files = find_nf_files(directory)
    if not nf_files:
        click.secho("No .nf files found", fg="yellow")
        return results

    # Process each module
    for nf_file in nf_files:
        module = Module(nf_file)
        module_results = LintResults(
            module_path=nf_file,
            errors=[],
            warnings=[]
        )

        # Run all rules on the module
        for rule in rules:
            rule_result = rule(module)
            module_results.errors.extend(rule_result.errors)
            module_results.warnings.extend(rule_result.warnings)

        results.append(module_results)

    return results

@click.command()
@click.argument('rules_file', type=click.Path(exists=True))
@click.argument('directory', type=click.Path(exists=True))
def main(rules_file: str, directory: str):
    """Lint .nf files using specified rules file.
    
    RULES_FILE: Path to the rules.py file
    DIRECTORY: Directory to scan for .nf files
    """
    results = run_lint(directory, rules_file)
    
    # Sort results by module path
    results.sort(key=lambda x: x.module_path)

    has_errors = False

    # Print results
    for result in results:
        if result.warnings or result.errors:
            click.echo(f"\nModule: {click.style(result.module_path, fg='cyan')}")

        for warning in result.warnings:
            click.echo(f"  • Line {click.style(str(warning.line), fg='cyan')}")
            click.secho(f"    {warning.warning}", fg="yellow")

        for error in result.errors:
            has_errors = True
            click.echo(f"  • Line {click.style(str(error.line), fg='cyan')}")
            click.secho(f"    {error.error}", fg="red")

    if has_errors:
        sys.exit(1)

if __name__ == "__main__":
    main()