def normalize_csv_row(row: dict) -> dict:
    def parse_float(value):
        return float(value) if value not in ("", None) else None

    def parse_str(value):
        return str(value) if value not in ("", None) else None

    return {
        "first_name": parse_str(row.get("first_name")),
        "last_name": parse_str(row.get("last_name")),
        "email": parse_str(row.get("email")),
        "date_of_birth": parse_str(row.get("date_of_birth")),
        "home_town": parse_str(row.get("home_town")),
        "math_score": parse_float(row.get("math_score")),
        "literature_score": parse_float(row.get("literature_score")),
        "english_score": parse_float(row.get("english_score")),
    }
