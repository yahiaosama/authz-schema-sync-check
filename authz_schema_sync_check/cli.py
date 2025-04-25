"""
Command-line interface for the pre-commit hook.
"""

import argparse
import sys
from pathlib import Path
import colorama

from .parser import SchemaParser
from .generator import TypeGenerator
from .git_utils import get_diff, apply_changes


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
        "--output",
        type=str,
        default="models.py",
        help="Path to the output models.py file",
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
    output_path = Path(args.output)

    if not schema_path.exists():
        print(f"Error: Schema file '{schema_path}' does not exist", file=sys.stderr)
        return 1

    try:
        # Parse schema and generate types
        schema_parser = SchemaParser(schema_path)
        generator = TypeGenerator(schema_parser)
        generated_content = generator.generate_types()

        # Check if output file exists
        if not output_path.exists():
            if args.auto_fix:
                if args.verbose:
                    print(
                        f"{colorama.Fore.CYAN}Creating new file: {output_path}{colorama.Style.RESET_ALL}"
                    )
                apply_changes(output_path, generated_content)
                print(
                    f"{colorama.Fore.RED}Error: Output file '{output_path}' did not exist but has been created{colorama.Style.RESET_ALL}",
                    file=sys.stderr,
                )
                print(
                    f"{colorama.Fore.YELLOW}Please review and commit the newly created file{colorama.Style.RESET_ALL}",
                    file=sys.stderr,
                )
            else:
                print(
                    f"{colorama.Fore.RED}Error: Output file '{output_path}' does not exist{colorama.Style.RESET_ALL}",
                    file=sys.stderr,
                )
                print(
                    f"\nRun with {colorama.Fore.YELLOW}--auto-fix{colorama.Style.RESET_ALL} to create the file",
                    file=sys.stderr,
                )
            return 1  # Always return error code

        # Compare with existing file
        has_diff, diff_output = get_diff(output_path, generated_content)

        if not has_diff:
            if args.verbose:
                print(
                    f"{colorama.Fore.GREEN}Files are in sync!{colorama.Style.RESET_ALL}"
                )
            return 0

        # Handle differences
        if args.auto_fix:
            if args.verbose:
                print(
                    f"{colorama.Fore.YELLOW}Updating {output_path}{colorama.Style.RESET_ALL}"
                )
            apply_changes(output_path, generated_content)
            return 0
        else:
            print(
                f"{colorama.Fore.RED}Error: {output_path} is out of sync with {schema_path}{colorama.Style.RESET_ALL}",
                file=sys.stderr,
            )
            print("\nDiff:", file=sys.stderr)

            # Apply colorization if enabled
            if args.colorized_diff:
                print(colorize_diff(diff_output), file=sys.stderr)
            else:
                print(diff_output, file=sys.stderr)

            print(
                f"\nRun with {colorama.Fore.YELLOW}--auto-fix{colorama.Style.RESET_ALL} to update the file",
                file=sys.stderr,
            )
            return 1
    except Exception as e:
        print(
            f"{colorama.Fore.RED}Error: {e}{colorama.Style.RESET_ALL}", file=sys.stderr
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
