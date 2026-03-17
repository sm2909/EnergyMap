import csv

FILE = "../data/test_energy_clean.csv"

def is_float(x):
    try:
        float(x)
        return True
    except:
        return False

def validate_csv():

    total = 0
    valid = 0

    errors = {
        "wrong_columns": [],
        "invalid_float": [],
        "empty_fields": [],
        "suspicious_strings": []
    }

    with open(FILE) as f:
        reader = csv.reader(f, delimiter=";")

        for i, row in enumerate(reader, 1):
            total += 1

            # 1. Check column count
            if len(row) != 6:
                errors["wrong_columns"].append((i, row))
                continue

            timestamp, repo, test, duration, package, core = row

            # 2. Check empty fields
            if not all(field.strip() for field in row):
                errors["empty_fields"].append((i, row))
                continue

            # 3. Check float fields
            if not (is_float(timestamp) and is_float(duration)
                    and is_float(package) and is_float(core)):
                errors["invalid_float"].append((i, row))
                continue

            # 4. Detect garbage strings (like your boundary issue)
            if any("boundary" in field or "=" in field for field in row):
                errors["suspicious_strings"].append((i, row))
                continue

            valid += 1

    # ---- REPORT ----
    print(f"\nTotal rows: {total}")
    print(f"Valid rows: {valid}")
    print(f"Invalid rows: {total - valid}")

    print("\nBreakdown:")

    for k, v in errors.items():
        print(f"{k}: {len(v)}")

    # Show some examples
    for k, v in errors.items():
        if v:
            print(f"\nExample {k}:")
            for line_no, row in v[:5]:
                print(f"Line {line_no}: {row}")

if __name__ == "__main__":
    validate_csv()