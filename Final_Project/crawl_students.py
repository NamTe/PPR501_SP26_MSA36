import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait


def extract_rows_from_html(html_text: str) -> list[dict]:
    # Parse the rendered HTML table into raw row dictionaries.
    soup = BeautifulSoup(html_text, "html.parser")
    tbody = soup.select_one("#student-rows")
    rows = tbody.find_all("tr") if tbody else soup.select("table tbody tr")

    records = []
    for row in rows:
        cells = row.find_all("td")
        # Skip placeholder or malformed rows.
        if not cells:
            continue
        if len(cells) == 1 and (cells[0].has_attr("colspan") or "empty" in row.get("class", [])):
            continue
        if len(cells) < 8:
            continue

        # Map table cells to the expected schema.
        student_id = cells[0].get_text(strip=True)
        full_name = cells[1].get_text(strip=True)
        email = cells[2].get_text(strip=True)
        date_of_birth = cells[3].get_text(strip=True)
        home_town = cells[4].get_text(strip=True)
        math_score = cells[5].get_text(strip=True)
        literature_score = cells[6].get_text(strip=True)
        english_score = cells[7].get_text(strip=True)

        records.append(
            {
                "student_id": student_id,
                "full_name": full_name,
                "email": email,
                "date_of_birth": date_of_birth,
                "home_town": home_town,
                "math_score": math_score,
                "literature_score": literature_score,
                "english_score": english_score,
            }
        )

    return records


def fetch_rendered_html(url: str, timeout_ms: int, driver_path: str | None) -> str:
    # Use headless Chrome to execute JS and return the fully rendered page source.
    timeout_sec = max(timeout_ms / 1000, 1)
    # Configure Chrome for headless crawling.
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = ChromeService(executable_path=driver_path) if driver_path else None
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.set_page_load_timeout(timeout_sec)
        driver.get(url)
        # Wait for a non-placeholder row to appear in the table body.
        def has_data(d) -> bool:
            rows = d.find_elements(By.CSS_SELECTOR, "#student-rows tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    continue
                # Ignore a single placeholder cell like "Loading students...".
                if len(cells) == 1:
                    cell_class = cells[0].get_attribute("class") or ""
                    if "empty" in cell_class or "loading" in cells[0].text.lower():
                        continue
                return True
            return False

        WebDriverWait(driver, timeout_sec).until(has_data)
        return driver.page_source
    finally:
        driver.quit()


def clean_data(records: list[dict]) -> pd.DataFrame:
    # Normalize fields, coerce scores, round per rule, and standardize dates.
    df = pd.DataFrame(records)
    if df.empty:
        return df

    # Normalize text fields.
    df["student_id"] = df["student_id"].astype(str).str.strip()
    df["full_name"] = df["full_name"].astype(str).str.strip()
    df["home_town"] = df["home_town"].astype(str).str.strip()
    df["date_of_birth"] = (
        df["date_of_birth"]
        .astype(str)
        .str.replace("\xa0", " ", regex=False)
        .str.strip()
    )

    # Remove duplicate students by ID.
    df = df.drop_duplicates(subset=["student_id"], keep="first")

    score_columns = ["math_score", "literature_score", "english_score"]
    for column in score_columns:
        # Normalize decimal separator and coerce invalid scores to 0.
        df[column] = (
            df[column]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
        # Custom rounding: > .5 round up, < .5 round down, = .5 keep as .5.
        base = np.floor(df[column])
        frac = df[column] - base
        rounded = np.where(frac > 0.5, np.ceil(df[column]), base)
        df[column] = np.where(np.isclose(frac, 0.5), base + 0.5, rounded)

    # Parse dates with day-first bias, then retry with month-first for failures.
    parsed_dates = pd.to_datetime(
        df["date_of_birth"], errors="coerce", dayfirst=True, infer_datetime_format=True
    )
    missing_mask = parsed_dates.isna()
    if missing_mask.any():
        fallback_dates = pd.to_datetime(
            df.loc[missing_mask, "date_of_birth"],
            errors="coerce",
            dayfirst=False,
            infer_datetime_format=True,
        )
        parsed_dates.loc[missing_mask] = fallback_dates

    # Format dates as dd-mm-yyyy.
    df["date_of_birth"] = parsed_dates.dt.strftime("%d-%m-%Y")

    return df


def build_analysis(df: pd.DataFrame) -> pd.DataFrame:
    # Produce per-subject aggregates overall and by hometown.
    if df.empty:
        return pd.DataFrame(columns=["scope", "home_town", "subject", "metric", "value"])

    score_columns = ["math_score", "literature_score", "english_score"]
    rows = []

    # Overall aggregates for each subject.
    for column in score_columns:
        series = df[column].dropna()
        if not series.empty:
            rows.append(
                {"scope": "overall", "home_town": "", "subject": column, "metric": "avg", "value": series.mean()}
            )
            rows.append(
                {"scope": "overall", "home_town": "", "subject": column, "metric": "min", "value": series.min()}
            )
            rows.append(
                {"scope": "overall", "home_town": "", "subject": column, "metric": "max", "value": series.max()}
            )

    # Per-hometown aggregates for each subject.
    if "home_town" in df.columns:
        grouped = df.groupby("home_town", dropna=False)
        for home_town, group in grouped:
            for column in score_columns:
                series = group[column].dropna()
                if series.empty:
                    continue
                rows.append(
                    {
                        "scope": "hometown",
                        "home_town": home_town,
                        "subject": column,
                        "metric": "avg",
                        "value": series.mean(),
                    }
                )
                rows.append(
                    {
                        "scope": "hometown",
                        "home_town": home_town,
                        "subject": column,
                        "metric": "min",
                        "value": series.min(),
                    }
                )
                rows.append(
                    {
                        "scope": "hometown",
                        "home_town": home_town,
                        "subject": column,
                        "metric": "max",
                        "value": series.max(),
                    }
                )

    return pd.DataFrame(rows)


def main() -> None:
    # CLI entrypoint: fetch HTML, clean rows, and write data + analysis to one CSV.
    parser = argparse.ArgumentParser(
        description="Crawl student data from a web page and produce a cleaned CSV."
    )
    parser.add_argument(
        "--input",
        help="Path to a saved HTML file (exported after the page is fully rendered).",
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000",
        help="URL of the rendered student dashboard.",
    )
    parser.add_argument(
        "--output",
        default="students_clean.csv",
        help="Path to the cleaned CSV output.",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=15000,
        help="Timeout for loading the page and waiting for data.",
    )
    parser.add_argument(
        "--driver-path",
        default=None,
        help="Optional path to the WebDriver executable (e.g., chromedriver).",
    )
    args = parser.parse_args()

    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            raise FileNotFoundError(f"Input HTML not found: {input_path}")
        # Use a saved DOM snapshot when provided.
        html_text = input_path.read_text(encoding="utf-8")
    else:
        # Otherwise crawl the live page with Selenium.
        html_text = fetch_rendered_html(args.url, args.timeout_ms, args.driver_path)
    records = extract_rows_from_html(html_text)
    cleaned_df = clean_data(records)
    analysis_df = build_analysis(cleaned_df)
    with open(args.output, "w", encoding="utf-8", newline="") as handle:
        # Write the cleaned data first, then a blank line, then the analysis table.
        cleaned_df.to_csv(handle, index=False, float_format="%.1f", decimal=",")
        handle.write("\n")
        analysis_df.to_csv(handle, index=False, float_format="%.2f", decimal=",")


if __name__ == "__main__":
    main()
