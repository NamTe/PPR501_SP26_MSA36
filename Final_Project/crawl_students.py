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
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt


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
    df.loc[df["home_town"].isin(["", "nan", "none"]), "home_town"] = "unknown"
    df["date_of_birth"] = (
        df["date_of_birth"]
        .astype(str)
        .str.replace("\xa0", " ", regex=False)
        .str.strip()
    )
    df["email"] = df["email"].astype(str).str.strip().str.lower()
    email_mask = df["email"].str.match(r"^[^@\s]+@gmail\.com$", na=False)
    df.loc[~email_mask, "email"] = "system@gmail.com"

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

    total_scores = df[score_columns].sum(axis=1)
    df["graduated"] = np.where(total_scores > 18, 1, 0)

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

def convert_to_vector_data(df: pd.DataFrame) -> pd.DataFrame:
    # Encode categorical columns and scale numeric columns for modeling.
    if df.empty:
        return df

    data = df.copy()
    original_numeric_cols = [
        column for column in data.columns if pd.api.types.is_numeric_dtype(data[column])
    ]
    if "date_of_birth" in data.columns:
        parsed_dob = pd.to_datetime(
            data["date_of_birth"], errors="coerce", dayfirst=True
        )
        data["date_of_birth"] = parsed_dob.map(
            lambda value: value.toordinal() if pd.notna(value) else np.nan
        )
        data["date_of_birth"] = pd.to_numeric(data["date_of_birth"], errors="coerce")

    numeric_cols = list(original_numeric_cols)
    if "date_of_birth" in data.columns and "date_of_birth" not in numeric_cols:
        numeric_cols.append("date_of_birth")
    categorical_cols = [column for column in data.columns if column not in numeric_cols]

    if categorical_cols:
        data = pd.get_dummies(data, columns=categorical_cols, dummy_na=True, dtype=int)

    if numeric_cols:
        numeric_cols = [column for column in numeric_cols if column in data.columns]
        if numeric_cols:
            scaler = StandardScaler()
            data[numeric_cols] = scaler.fit_transform(data[numeric_cols].astype(float))

    return data

def build_analysis():
    # Produce histogram from the cleaned CSV without adding new columns.
    data_path = Path("students_clean.csv")
    if data_path.exists():
        df = pd.read_csv(data_path, decimal=",")
    if df.empty:
        return pd.DataFrame(
            columns=[
                "student_id",
                "full_name",
                "email",
                "date_of_birth",
                "home_town",
                "math_score",
                "literature_score",
                "english_score",
                "graduated"
            ]
        )
    
    math_data = pd.to_numeric(df["math_score"], errors="coerce").dropna()
    literature_data = pd.to_numeric(df["literature_score"], errors="coerce").dropna()
    english_data = pd.to_numeric(df["english_score"], errors="coerce").dropna()

    bins = np.arange(0, 11)
    bin_centers = bins[:-1] + 0.5
    bar_width = 0.25

    math_counts, _ = np.histogram(math_data, bins=bins, range=(0, 10))
    literature_counts, _ = np.histogram(literature_data, bins=bins, range=(0, 10))
    english_counts, _ = np.histogram(english_data, bins=bins, range=(0, 10))

    fig, axes = plt.subplots(1, 3, figsize=(18, 5), layout="constrained")
    ax_hist = axes[0]
    ax_hist.bar(
        bin_centers - bar_width,
        math_counts,
        width=bar_width,
        color="steelblue",
        edgecolor="white",
        label="Math",
    )
    ax_hist.bar(
        bin_centers,
        literature_counts,
        width=bar_width,
        color="seagreen",
        edgecolor="white",
        label="Literature",
    )
    ax_hist.bar(
        bin_centers + bar_width,
        english_counts,
        width=bar_width,
        color="darkorange",
        edgecolor="white",
        label="English",
    )

    ax_hist.set_title("Score Distribution by Subject")
    ax_hist.set_xlabel("Score range")
    ax_hist.set_ylabel("Count")
    ax_hist.set_xticks(bin_centers)
    ax_hist.set_xticklabels([f"{i}-{i+1}" for i in range(0, 10)])
    ax_hist.set_xlim(0, 10)
    ax_hist.legend()

    ax_pie = axes[1]
    if "home_town" in df.columns:
        home_town_counts = df["home_town"].fillna("Unknown").value_counts()
        ax_pie.pie(
            home_town_counts.values,
            labels=home_town_counts.index,
            autopct="%1.1f%%",
            startangle=90,
        )
        ax_pie.set_title("Students by Home Town")
    else:
        ax_pie.axis("off")

    ax_grad = axes[2]
    if "graduated" in df.columns:
        grad_counts = df["graduated"].fillna(0).astype(int).value_counts().sort_index()
        labels = ["Not Graduated", "Graduated"]
        values = [grad_counts.get(0, 0), grad_counts.get(1, 0)]
        ax_grad.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
        )
        ax_grad.set_title("Graduation Status (%)")
    else:
        ax_grad.axis("off")

    fig.savefig("students_charts.png", dpi=150)
    plt.close(fig)


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
    vector_df = convert_to_vector_data(cleaned_df)
    with open(args.output, "w", encoding="utf-8", newline="") as handle:
        cleaned_df.to_csv(handle, index=False, float_format="%.1f", decimal=",")
        handle.write("\n")
    vector_df.to_csv("students_vector.csv", index=False)
    build_analysis()


if __name__ == "__main__":
    main()
