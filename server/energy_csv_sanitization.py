import csv

INPUT_FILE = "../data/test_energy.csv"
OUTPUT_FILE = "../data/test_energy_clean.csv"


def is_float(x):
    try:
        float(x)
        return True
    except:
        return False


def is_valid_row(row):
    # Must have exactly 6 columns
    if len(row) != 6:
        return False

    timestamp, repo, test, duration, package, core = row

    # No empty fields
    if not all(field.strip() for field in row):
        return False

    # Numeric validation
    if not (
        is_float(timestamp)
        and is_float(duration)
        and is_float(package)
        and is_float(core)
    ):
        return False

    # Reject suspicious injected strings
    bad_patterns = ["boundary", "=", "<meta", "charset"]

    for field in row:
        if any(p in field for p in bad_patterns):
            return False

    return True


def sanitize():
    total = 0
    kept = 0

    with open(INPUT_FILE) as infile, open(OUTPUT_FILE, "w", newline="") as outfile:
        reader = csv.reader(infile, delimiter=";")
        writer = csv.writer(outfile, delimiter=";")

        for row in reader:
            total += 1

            if is_valid_row(row):
                writer.writerow(row)
                kept += 1

    print(f"\nTotal rows: {total}")
    print(f"Kept rows: {kept}")
    print(f"Removed rows: {total - kept}")
    print(f"Clean file written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    sanitize()