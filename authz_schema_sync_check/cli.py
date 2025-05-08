"""
Command-line interface for the pre-commit hook.
"""

import argparse
import sys
from pathlib import Path
from typing import TypedDict, List, Tuple, Optional
import colorama
import jinja2

from .parser import SchemaParser
from .generator import TypeGenerator
from .git_utils import get_diff, apply_changes


class ProcessResult(TypedDict):
    """Result of processing an output mapping."""

    output_path: Path
    template_name: str
    success: bool
    error: Optional[str]
    has_diff: bool
    diff_output: str
    created: bool
    updated: bool


class InvalidMapping(TypedDict):
    """Invalid output mapping."""

    mapping: str
    reason: str


def colorize_diff(diff_text: str) -> str:
    """
    Add colors to a unified diff output.

    Args:
        diff_text: The unified diff text

    Returns:
        Colorized diff text
    """
    colorized_lines = []

    for line in diff_text.splitlines():
        if line.startswith("---") or line.startswith("+++"):
            # File headers
            colorized_lines.append(
                f"{colorama.Fore.BLUE}{line}{colorama.Style.RESET_ALL}"
            )
        elif line.startswith("-"):
            # Removed lines
            colorized_lines.append(
                f"{colorama.Fore.RED}{line}{colorama.Style.RESET_ALL}"
            )
        elif line.startswith("+"):
            # Added lines
            colorized_lines.append(
                f"{colorama.Fore.GREEN}{line}{colorama.Style.RESET_ALL}"
            )
        elif line.startswith("@@"):
            # Hunk headers
            colorized_lines.append(
                f"{colorama.Fore.CYAN}{line}{colorama.Style.RESET_ALL}"
            )
        else:
            # Context lines
            colorized_lines.append(line)

    return "\n".join(colorized_lines)


def process_output_mapping(
    schema_parser: SchemaParser,
    output_path: Path,
    template_name: str,
    auto_fix: bool,
    verbose: bool,
    colorized_diff: bool,
) -> ProcessResult:
    """
    Process a single output mapping.

    Args:
        schema_parser: The schema parser
        output_path: Path to the output file
        template_name: Name of the template to use
        auto_fix: Whether to automatically fix issues
        verbose: Whether to print verbose output
        colorized_diff: Whether to colorize diff output

    Returns:
        A ProcessResult containing the result of processing
    """
    result: ProcessResult = {
        "output_path": output_path,
        "template_name": template_name,
        "success": False,
        "error": None,
        "has_diff": False,
        "diff_output": "",
        "created": False,
        "updated": False,
    }

    # Create generator
    generator = TypeGenerator(schema_parser)

    # Generate content
    try:
        generated_content = generator.generate_code(template_name)
    except jinja2.exceptions.TemplateNotFound:
        result["error"] = f"Template '{template_name}' not found"
        return result
    except Exception as e:
        result["error"] = f"Error generating code: {e}"
        return result

    # Check if output file exists
    if not output_path.exists():
        if auto_fix:
            try:
                apply_changes(output_path, generated_content)
                result["created"] = True
                # Always mark as unsuccessful even though we created the file
                # This ensures the user must manually add the file to git
                result["success"] = False
                result["error"] = "Output file did not exist but has been created"
            except Exception as e:
                result["error"] = f"Error creating file: {e}"
        else:
            result["error"] = "Output file does not exist"
        return result

    # Compare with existing file
    try:
        has_diff, diff_output = get_diff(output_path, generated_content)
        result["has_diff"] = has_diff
        result["diff_output"] = diff_output

        if has_diff:
            if auto_fix:
                try:
                    apply_changes(output_path, generated_content)
                    result["updated"] = True
                    result["success"] = True
                except Exception as e:
                    result["error"] = f"Error updating file: {e}"
                    return result
            else:
                result["error"] = "File is out of sync with schema"
                return result

        # If we got here and there's no diff, the operation was successful
        result["success"] = True
        return result

    except Exception as e:
        result["error"] = f"Error comparing files: {e}"
        return result


def parse_output_mappings(
    mappings: List[str],
) -> Tuple[List[Tuple[Path, str]], List[InvalidMapping]]:
    """
    Parse output mappings from command line arguments.

    Args:
        mappings: List of mapping strings in format 'output_path[:template_name]'
                 If template_name is not provided, it will be inferred from the file extension

    Returns:
        Tuple of (valid_mappings, invalid_mappings)
    """
    valid_mappings: List[Tuple[Path, str]] = []
    invalid_mappings: List[InvalidMapping] = []

    for mapping in mappings:
        if ":" in mapping:
            # Explicit template specified
            try:
                output_path_str, template_name = mapping.split(":", 1)
                valid_mappings.append((Path(output_path_str), template_name))
            except ValueError:
                invalid_mappings.append(
                    {
                        "mapping": mapping,
                        "reason": "Invalid format. Should be 'output_path[:template_name]'",
                    }
                )
        else:
            # No template specified, infer from file extension
            path_obj = Path(mapping)
            if path_obj.suffix == ".py":
                template_name = "default_types.py.jinja"
                valid_mappings.append((path_obj, template_name))
            elif path_obj.suffix == ".ts":
                template_name = "default_types.ts.jinja"
                valid_mappings.append((path_obj, template_name))
            else:
                invalid_mappings.append(
                    {
                        "mapping": mapping,
                        "reason": "Cannot infer template from file extension. Please specify template explicitly.",
                    }
                )

    return valid_mappings, invalid_mappings


def report_result(result: ProcessResult, verbose: bool, colorized_diff: bool) -> None:
    """
    Report the result of processing an output mapping.

    Args:
        result: The ProcessResult
        verbose: Whether to print verbose output
        colorized_diff: Whether to colorize diff output
    """
    output_path = result["output_path"]
    template_name = result["template_name"]

    if result["created"]:
        # Always report created files, even if the operation is marked as unsuccessful
        if verbose:
            print(
                f"{colorama.Fore.CYAN}Created new file: {output_path} (using template: {template_name}){colorama.Style.RESET_ALL}"
            )
        print(
            f"{colorama.Fore.YELLOW}Please review and commit the newly created file: {output_path}{colorama.Style.RESET_ALL}",
            file=sys.stderr,
        )

    if result["success"]:
        if result["updated"]:
            if verbose:
                print(
                    f"{colorama.Fore.YELLOW}Updated file: {output_path}{colorama.Style.RESET_ALL}"
                )
        elif not result["has_diff"]:
            if verbose:
                print(
                    f"{colorama.Fore.GREEN}File {output_path} is in sync!{colorama.Style.RESET_ALL}"
                )
    else:
        print(
            f"{colorama.Fore.RED}Error processing {output_path}: {result['error']}{colorama.Style.RESET_ALL}",
            file=sys.stderr,
        )

        if result["has_diff"] and result["diff_output"]:
            print("\nDiff:", file=sys.stderr)
            if colorized_diff:
                print(colorize_diff(result["diff_output"]), file=sys.stderr)
            else:
                print(result["diff_output"], file=sys.stderr)

        if not result["created"] and not output_path.exists():
            print(
                f"\nRun with {colorama.Fore.YELLOW}--auto-fix{colorama.Style.RESET_ALL} to create the file",
                file=sys.stderr,
            )
        elif result["has_diff"] and not result["updated"]:
            print(
                f"\nRun with {colorama.Fore.YELLOW}--auto-fix{colorama.Style.RESET_ALL} to update the file",
                file=sys.stderr,
            )


def main():
    """
    Main entry point for the CLI.

    Returns:
        Exit code: 0 for success, 1 for validation errors
    """
    # Initialize colorama for cross-platform colored output
    colorama.init()

    parser = argparse.ArgumentParser(
        description="Generate type definitions from schema.zed and check they're in sync"
    )
    parser.add_argument(
        "--schema", type=str, default="schema.zed", help="Path to the schema.zed file"
    )
    parser.add_argument(
        "--outputs",
        type=str,
        nargs="+",
        help="Output paths, optionally with template names in format 'output_path[:template_name]'. "
        "For .py files, the default template is default_types.py.jinja. "
        "For .ts files, the default template is default_types.ts.jinja. "
        "For other file types, you must specify the template explicitly.",
        required=True,
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Automatically apply changes if out of sync",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--colorized-diff",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Enable or disable colorized diff output (true/false)",
    )

    args = parser.parse_args()

    schema_path = Path(args.schema)

    if not schema_path.exists():
        print(f"Error: Schema file '{schema_path}' does not exist", file=sys.stderr)
        return 1

    try:
        # Parse schema
        schema_parser = SchemaParser(schema_path)

        # Parse output mappings
        valid_mappings, invalid_mappings = parse_output_mappings(args.outputs)

        # Report invalid mappings
        if invalid_mappings:
            for invalid in invalid_mappings:
                print(
                    f"{colorama.Fore.RED}Error in mapping '{invalid['mapping']}': {invalid['reason']}{colorama.Style.RESET_ALL}",
                    file=sys.stderr,
                )
            return 1

        # Process each output mapping and collect results
        results: List[ProcessResult] = []

        for output_path, template_name in valid_mappings:
            result = process_output_mapping(
                schema_parser=schema_parser,
                output_path=output_path,
                template_name=template_name,
                auto_fix=args.auto_fix,
                verbose=args.verbose,
                colorized_diff=args.colorized_diff,
            )
            results.append(result)

        # Report results
        for result in results:
            report_result(
                result=result, verbose=args.verbose, colorized_diff=args.colorized_diff
            )

        # Return error code if any errors were encountered
        has_errors = any(not result["success"] for result in results)
        return 1 if has_errors else 0

    except Exception as e:
        print(
            f"{colorama.Fore.RED}Error: {e}{colorama.Style.RESET_ALL}", file=sys.stderr
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
