##
# @file       analyze_data.py
# @author     Andrias Zelele
# @date       2025-04-16
# @brief      Analyzes descriptive statistics from a math contest results CSV file.
#
# @description
#   This program reads the same contest CSV used in Challenge-05 and produces
#   a summary CSV report containing:
#     1. The average number of teams entered per institution
#     2. An ordered list of institutions by number of teams entered (descending)
#     3. All institutions whose team(s) earned 'Outstanding Winner' rankings
#        (ordered by institution name)
#     4. All US teams that received 'Meritorious' ranking or better
#        (Meritorious, Finalist, Outstanding Winner)
#
#   Results are written to a CSV report file and also printed to the console.
#
# @usage      python src/analyze_data.py doc/2015.csv
# @version    1.0
##

import argparse
import csv
import os
import sys
from collections import defaultdict

##
# @brief Set of column names that must be present in the input CSV file.
##
REQUIRED_COLUMNS = {
    "Institution", "Team Number", "City",
    "State/Province", "Country", "Advisor",
    "Problem", "Ranking"
}

##
# @brief Rankings considered 'Meritorious or better', from best to lowest.
##
MERITORIOUS_OR_BETTER = {"Meritorious", "Finalist", "Outstanding Winner"}


# ── Argument parsing ───────────────────────────────────────────────────────────

def parse_args() -> str:
    """
    @brief  Resolves the input file path from the command-line argument
            or by prompting the user if none was provided.

    @return The input file path as a string.
    """
    parser = argparse.ArgumentParser(
        description="Analyze descriptive statistics from a math contest CSV file."
    )

    # Optional positional argument — prompts the user if omitted
    parser.add_argument(
        "input_file",
        nargs="?",
        default=None,
        help="Path to the input CSV file (e.g. doc/2015.csv)"
    )

    args = parser.parse_args()

    # If no filename was provided on the command line, prompt the user
    if args.input_file is None:
        print("No file provided.")
        while True:
            input_path = input("Please enter the path to your CSV file: ").strip()
            if input_path:
                return input_path
            print("ERROR: File path cannot be empty. Please try again.")

    return args.input_file


def derive_output_path(input_path: str) -> str:
    """
    @brief  Derives the output report filename from the input filename.

    @details
        e.g. 'doc/2015.csv' -> 'report_2015.csv'

    @param  input_path  Path to the input CSV file.
    @return The output report file path as a string.
    """
    base = os.path.splitext(os.path.basename(input_path))[0]
    return f"report_{base}.csv"


# ── Validation ─────────────────────────────────────────────────────────────────

def validate_file_exists(input_path: str) -> None:
    """
    @brief  Validates that the input file is inside the doc/ folder,
            exists on disk, and is not empty.

    @details
        The program expects all input files to live in the doc/ directory.
        If the user provides a path outside of doc/, or skips the folder
        entirely, we stop early with a clear message explaining where to
        put the file.

    @param  input_path  Path to the input CSV file.
    @return None
    """
    # Normalize the path so we can inspect its parts reliably
    normalized = os.path.normpath(input_path)
    parts = normalized.split(os.sep)

    # The path must have at least two parts and the first must be 'doc'
    if len(parts) < 2 or parts[0] != "doc":
        sys.exit(
            f"ERROR: '{input_path}' is not inside the doc/ folder.\n"
            f"Please provide the file as: doc/<filename>.csv\n"
            f"Example: python src/analyze_data.py doc/2015.csv"
        )

    # File existence
    if not os.path.exists(input_path):
        sys.exit(
            f"ERROR: '{input_path}' not found.\n"
            f"Make sure the file exists at: {os.path.abspath(input_path)}"
        )

    # File is not empty
    if os.path.getsize(input_path) == 0:
        sys.exit(f"ERROR: '{input_path}' is empty.")


def open_csv(input_path: str) -> list[dict]:
    """
    @brief  Opens and reads a CSV file into a list of row dictionaries,
            handling multiple encodings robustly.

    @param  input_path  Path to the input CSV file.
    @return A list of dicts where each dict represents one row.
    """
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with open(input_path, encoding=encoding, newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            # Clean BOM off the first column name if still present after decoding
            if rows:
                first_key = next(iter(rows[0]))
                clean_key = first_key.encode("latin-1").decode("utf-8").lstrip("\ufeff")
                if first_key != clean_key:
                    for row in rows:
                        row[clean_key] = row.pop(first_key)

            return rows

        except (UnicodeDecodeError, UnicodeError):
            continue

    sys.exit(f"ERROR: Could not decode '{input_path}'. Try saving it as UTF-8.")


def validate_contents(input_path: str, rows: list[dict]) -> None:
    """
    @brief  Validates that the parsed rows have the expected columns
            and at least one data row.

    @param  input_path  Path to the input CSV file (used in error messages).
    @param  rows        List of row dicts returned by open_csv().
    @return None
    """
    if not rows:
        sys.exit(f"ERROR: '{input_path}' has a header but no data rows.")

    columns = set(rows[0].keys())
    missing = REQUIRED_COLUMNS - columns
    if missing:
        sys.exit(
            f"ERROR: '{input_path}' is missing expected column(s): {', '.join(sorted(missing))}\n"
            f"Found columns: {', '.join(sorted(columns))}"
        )

    print(f"OK: '{input_path}' passed all validation checks.")


# ── Analysis functions ─────────────────────────────────────────────────────────

def average_teams_per_institution(rows: list[dict]) -> float:
    """
    @brief  Calculates the average number of teams entered per institution.

    @details
        Counts the total number of teams and divides by the number of unique
        institutions, identified by (Institution, City, State/Province, Country).

    @param  rows  List of row dicts from the CSV.
    @return The average as a float, rounded to 2 decimal places.
    """
    # Use a set to count unique institutions
    unique_institutions = {
        (row["Institution"], row["City"], row["State/Province"], row["Country"])
        for row in rows
    }

    total_teams = len(rows)
    total_institutions = len(unique_institutions)

    return round(total_teams / total_institutions, 2)


def teams_per_institution(rows: list[dict]) -> list[tuple[str, int]]:
    """
    @brief  Counts the number of teams per institution and returns them
            ordered from most teams to fewest.

    @param  rows  List of row dicts from the CSV.
    @return A list of (institution_name, team_count) tuples, sorted descending.
    """
    # defaultdict(int) starts every new key at 0 automatically
    counts = defaultdict(int)

    for row in rows:
        counts[row["Institution"]] += 1

    # Sort by team count descending, then alphabetically for ties
    return sorted(counts.items(), key=lambda x: (-x[1], x[0]))


def outstanding_institutions(rows: list[dict]) -> list[str]:
    """
    @brief  Returns a sorted list of institution names whose team(s) earned
            an 'Outstanding Winner' ranking.

    @param  rows  List of row dicts from the CSV.
    @return A sorted list of unique institution name strings.
    """
    inst_set = {
        row["Institution"]
        for row in rows
        if row["Ranking"] == "Outstanding Winner"
    }

    return sorted(inst_set)


def us_meritorious_or_better(rows: list[dict]) -> list[dict]:
    """
    @brief  Returns all US teams that received a 'Meritorious' ranking or better.

    @details
        'Meritorious or better' includes: Meritorious, Finalist, Outstanding Winner.
        Results are sorted by institution name, then team number.

    @param  rows  List of row dicts from the CSV.
    @return A filtered and sorted list of row dicts.
    """
    filtered = [
        row for row in rows
        if row["Country"] == "USA" and row["Ranking"] in MERITORIOUS_OR_BETTER
    ]

    return sorted(filtered, key=lambda x: (x["Institution"], x["Team Number"]))


# ── Output functions ───────────────────────────────────────────────────────────

def print_summary(
    avg: float,
    top_institutions: list[tuple[str, int]],
    outstanding: list[str],
    us_merit: list[dict]
) -> None:
    """
    @brief  Prints a formatted summary of all statistics to the console.

    @param  avg               Average teams per institution.
    @param  top_institutions  Ordered list of (institution, team_count) tuples.
    @param  outstanding       Sorted list of outstanding institution names.
    @param  us_merit          List of US team row dicts with Meritorious or better.
    @return None
    """
    separator = "-" * 60

    print(f"\n{'=' * 60}")
    print("  CONTEST STATISTICS REPORT — 2015")
    print(f"{'=' * 60}")

    # Section 1: Average teams per institution
    print(f"\n{separator}")
    print(f"  Average teams per institution: {avg}")
    print(separator)

    # Section 2: Top 5 institutions by team count
    print(f"\n{separator}")
    print("  Top 5 institutions by number of teams entered:")
    print(separator)
    for i, (inst, count) in enumerate(top_institutions[:5], start=1):
        print(f"  {i:>2}. {inst} ({count} teams)")
    print(f"  ... ({len(top_institutions)} institutions total, see report CSV for full list)")

    # Section 3: Outstanding institutions
    print(f"\n{separator}")
    print("  Institutions with Outstanding Winner team(s):")
    print(separator)
    for inst in outstanding:
        print(f"  - {inst}")
    print(f"  ({len(outstanding)} institutions total)")

    # Section 4: US teams Meritorious or better (first 5 shown)
    print(f"\n{separator}")
    print("  US teams with Meritorious ranking or better:")
    print(separator)
    for row in us_merit[:5]:
        print(f"  Team {row['Team Number']} | {row['Institution']} | {row['Ranking']}")
    print(f"  ... ({len(us_merit)} teams total, see report CSV for full list)")

    print(f"\n{'=' * 60}\n")


def write_report(
    output_path: str,
    avg: float,
    top_institutions: list[tuple[str, int]],
    outstanding: list[str],
    us_merit: list[dict]
) -> None:
    """
    @brief  Writes all statistics to a CSV report file.

    @details
        The CSV is organized into four clearly labeled sections, each with
        its own header row and data rows, separated by blank lines.

    @param  output_path       Path to write the output CSV file.
    @param  avg               Average teams per institution.
    @param  top_institutions  Ordered list of (institution, team_count) tuples.
    @param  outstanding       Sorted list of outstanding institution names.
    @param  us_merit          List of US team row dicts with Meritorious or better.
    @return None
    """
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Section 1: Average
            writer.writerow(["SECTION", "Average Teams Per Institution"])
            writer.writerow(["Average", avg])
            writer.writerow([])

            # Section 2: Top institutions by team count
            writer.writerow(["SECTION", "Institutions Ordered by Number of Teams Entered"])
            writer.writerow(["Rank", "Institution Name", "Team Count"])
            for i, (inst, count) in enumerate(top_institutions, start=1):
                writer.writerow([i, inst, count])
            writer.writerow([])

            # Section 3: Outstanding institutions
            writer.writerow(["SECTION", "Institutions with Outstanding Winner Team(s)"])
            writer.writerow(["Institution Name"])
            for inst in outstanding:
                writer.writerow([inst])
            writer.writerow([])

            # Section 4: US teams Meritorious or better
            writer.writerow(["SECTION", "US Teams with Meritorious Ranking or Better"])
            writer.writerow(["Team Number", "Institution", "City", "State", "Advisor", "Problem", "Ranking"])
            for row in us_merit:
                writer.writerow([
                    row["Team Number"],
                    row["Institution"],
                    row["City"],
                    row["State/Province"],
                    row["Advisor"],
                    row["Problem"],
                    row["Ranking"]
                ])

        print(f"Report written to '{output_path}'.")

    except PermissionError:
        sys.exit(
            f"ERROR: Permission denied when writing '{output_path}'. "
            f"Is the file open in another program?"
        )


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    """
    @brief  Entry point of the program. Orchestrates all analysis steps.

    @details
        Calls each function in the correct order:
            1. Parse the command-line argument or prompt the user.
            2. Derive the output report filename.
            3. Validate the file exists and is not empty.
            4. Open and parse the CSV file.
            5. Validate the parsed contents.
            6. Run all four analysis functions.
            7. Print the summary to the console.
            8. Write the report CSV file.

    @return None
    """
    # Step 1: Resolve the input file path
    input_path = parse_args()

    # Step 2: Derive the output report filename
    output_path = derive_output_path(input_path)

    # Step 3: Validate the file exists and is not empty
    validate_file_exists(input_path)

    # Step 4: Open and parse the CSV file
    rows = open_csv(input_path)

    # Step 5: Validate the parsed contents
    validate_contents(input_path, rows)

    # Step 6: Run all four analyses
    avg             = average_teams_per_institution(rows)
    top_inst        = teams_per_institution(rows)
    outstanding     = outstanding_institutions(rows)
    us_merit        = us_meritorious_or_better(rows)

    # Step 7: Print the summary to the console
    print_summary(avg, top_inst, outstanding, us_merit)

    # Step 8: Write the report CSV file
    write_report(output_path, avg, top_inst, outstanding, us_merit)


##
# @brief  Standard Python entry point guard.
#         Ensures main() is only called when this script is run directly.
##
if __name__ == "__main__":
    main()