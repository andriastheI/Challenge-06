# Challenge-06 – Contest Data Analyzer

A console-based Python application that reads a math contest results CSV file
and produces a statistical analysis report, written to both the console and
an output CSV file.

This project demonstrates:

* File I/O with CSV files
* Descriptive statistics and data analysis
* Data filtering and sorting
* Input validation and error handling
* Argument-based program flow

## Project Structure

```
Challenge-06/
├── src/
│   └── analyze_data.py       # Main program logic
├── doc/
│   └── 2015.csv              # CSV file containing contest data
└── README.md                 # Project documentation
```

## How the Program Works

1. The program loads contest data from a CSV file passed as a command-line argument.
2. It validates that the file is inside the `doc/` folder, is not empty, and contains all required columns.
3. It runs four statistical analyses on the data:
   * The average number of teams entered per institution
   * An ordered list of institutions by number of teams entered (descending)
   * All institutions whose team(s) earned an `Outstanding Winner` ranking (alphabetical)
   * All US teams that received a `Meritorious` ranking or better
4. A summary is printed to the console (top 5 preview for long lists).
5. The full results are written to a CSV report file named after the input file.

## How to Run

### Requirements

* Python 3.10 or higher
* No third-party libraries required (uses Python's standard library only)

### Steps

1. Clone the repository from GitHub:

```bash
git clone https://github.com/andriastheI/Challenge-06.git
```

2. Navigate into the project directory:

```bash
cd Challenge-06
```

3. Ensure your contest CSV file is located inside the `doc/` folder.

4. Run the program from the terminal:

```bash
python src/analyze_data.py doc/2015.csv
```

If no filename is provided, the program will prompt you:

```bash
python src/analyze_data.py
No file provided.
Please enter the path to your CSV file: doc/2015.csv
```

### Sample Output

```
OK: 'doc/2015.csv' passed all validation checks.

============================================================
  CONTEST STATISTICS REPORT — 2015
============================================================

------------------------------------------------------------
  Average teams per institution: 5.8
------------------------------------------------------------

------------------------------------------------------------
  Top 5 institutions by number of teams entered:
------------------------------------------------------------
   1. BeiJing University Of Post And Telecommunication (323 teams)
   2. Harbin Institute of Technology (303 teams)
   3. Sun Yat-Sen University (225 teams)
   4. Central South University (202 teams)
   5. Dalian University of Technology (187 teams)
  ... (1128 institutions total, see report CSV for full list)

------------------------------------------------------------
  Institutions with Outstanding Winner team(s):
------------------------------------------------------------
  - Bethel University
  - Central South University
  - Chongqing University
  ...
  (16 institutions total)

------------------------------------------------------------
  US teams with Meritorious ranking or better:
------------------------------------------------------------
  Team 40056 | American Heritage School Plantation | Meritorious
  Team 36178 | Bethel University | Outstanding Winner
  ...
  (69 teams total, see report CSV for full list)

============================================================

Report written to 'report_2015.csv'.
```

## Input File Format

The input CSV must be placed inside the `doc/` folder and have the following
columns (in any order):

| Column         | Description                              |
|----------------|------------------------------------------|
| Institution    | Name of the school or university         |
| Team Number    | Unique registration number for the team  |
| City           | City where the institution is located    |
| State/Province | State or province (may be empty)         |
| Country        | Country where the institution is located |
| Advisor        | Faculty advisor for the team             |
| Problem        | Problem chosen by the team (A, B, C, D)  |
| Ranking        | Final ranking designation                |

> The script handles files saved with a UTF-8 BOM (common when exported from Excel) automatically.

## Output File Format

### report_YYYY.csv

The report file is organized into four labeled sections:

| Section | Description |
|---------|-------------|
| Average Teams Per Institution | Single value — the average across all institutions |
| Institutions Ordered by Number of Teams Entered | Ranked list with institution name and team count |
| Institutions with Outstanding Winner Team(s) | Alphabetical list of institution names |
| US Teams with Meritorious Ranking or Better | Team number, institution, city, state, advisor, problem, and ranking |

## Rankings

The contest uses the following ranking designations from best to worst:

| Ranking               | Included in "Meritorious or Better" |
|-----------------------|--------------------------------------|
| Outstanding Winner    | Yes                                  |
| Finalist              | Yes                                  |
| Meritorious           | Yes                                  |
| Honorable Mention     | No                                   |
| Successful Participant| No                                   |
| Unsuccessful          | No                                   |

## Validation and Error Messages

The script checks for the following before processing:

| Situation                    | Error Message                                                  |
|------------------------------|----------------------------------------------------------------|
| File not in doc/ folder      | `ERROR: 'file.csv' is not inside the doc/ folder.`            |
| File not found               | `ERROR: 'file.csv' not found. Make sure the file exists at ...`|
| File is empty                | `ERROR: 'file.csv' is empty.`                                  |
| Missing required columns     | `ERROR: 'file.csv' is missing expected column(s): ...`         |
| File has no data rows        | `ERROR: 'file.csv' has a header but no data rows.`             |
| Output file is open in Excel | `ERROR: Permission denied when writing '...'.`                 |
| File cannot be decoded       | `ERROR: Could not decode 'file.csv'. Try saving as UTF-8.`     |

## Help

To see usage instructions directly from the command line:

```bash
python src/analyze_data.py --help
```

## Author

Andrias Zelele

Computer Science Student

## Notes

* Input files must be placed inside the `doc/` folder
* The console preview shows the top 5 results for long lists — the full data is always in the report CSV
* `Meritorious or better` includes: Meritorious, Finalist, and Outstanding Winner
* Input validation prevents the program from running on malformed or missing files
* Designed for academic and educational use

## Purpose

This project is intended for academic and educational purposes only.
