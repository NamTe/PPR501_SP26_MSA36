def normalize_csv_row(row: dict) -> dict:
    def parse_float(value):
        return float(value) if value not in ("", None) else None

    return {
        "first_name": row.get("first_name"),
        "last_name": row.get("last_name"),
        "email": row.get("email"),
        "date_of_birth": row.get("date_of_birth"),
        "home_town": row.get("home_town"),
        "math_score": parse_float(row.get("math_score")),
        "literature_score": parse_float(row.get("literature_score")),
        "english_score": parse_float(row.get("english_score")),
    }
