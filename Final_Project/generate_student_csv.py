import csv
import random
from datetime import date, timedelta

YEARS = [2000, 2001, 2002, 2003, 2004, 2005, 2006]
TOTAL_RECORDS = 100
OUTPUT_FILE = "random_students.csv"

first_names = [
    "Nam", "An", "Minh", "Hoa", "Tuan", "Lan", "Hung", "Mai", "Long", "Nga"
]

last_names = [
    "Nguyen", "Tran", "Le", "Pham", "Do", "Vu", "Bui", "Ho", "Dang", "Phan", "Trinh"
]

home_towns = [
    "Ha Noi", "HCM", "Da Nang", "Hai Phong", "Can Tho", "Hung Yen", "Nam Dinh", "Thai Nguyen",
    "Bac Giang", "Bac Ninh"
]


def random_date() -> date:
    year = random.choice(YEARS)
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def random_score():
    if random.random() < 0.02:
        # some invalid data
        return None
    return round(random.uniform(3.0, 10.0), 1)

def generate_email(first_name_str: str, last_name_str: str) -> str | None:
    if random.random() < 0.05:
        # some invalid data
        return None
    if first_name_str is None and last_name_str is None:
        return None
    elif first_name_str is None and last_name_str is not None:
        return f"{last_name_str.lower()}{i}@gmail.com"
    elif first_name_str is not None and last_name_str is None:
        return f"{first_name_str.lower()}{i}@gmail.com"

    return f"{first_name_str.lower()}.{last_name_str.lower()}{i}@gmail.com"

def generate_dob() -> str | None:
    if random.random() < 0.03:
        # some invalid data
        return None
    return random_date().isoformat()

def generate_home_town() -> str | None:
    if random.random() < 0.03:
        return None
    return random.choice(home_towns)

students = []


def generate_first_name() -> str | None:
    if random.random() < 0.02:
        return None
    return random.choice(first_names)


def generate_last_name():
    if random.random() < 0.02:
        return None
    return random.choice(last_names)


for i in range(1, TOTAL_RECORDS + 1):
    first_name = generate_first_name()
    last_name = generate_last_name()

    student = {
        "first_name": first_name,
        "last_name": last_name,
        "email": generate_email(first_name, last_name),
        "date_of_birth": generate_dob(),
        "home_town": generate_home_town(),
        "math_score": random_score(),
        "literature_score": random_score(),
        "english_score": random_score(),
    }

    students.append(student)

# Shuffle to ensure DOB order is random
random.shuffle(students)

with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "first_name",
            "last_name",
            "email",
            "date_of_birth",
            "home_town",
            "math_score",
            "literature_score",
            "english_score",
        ],
    )
    writer.writeheader()
    writer.writerows(students)

print(f"Generated {TOTAL_RECORDS} students into {OUTPUT_FILE}")
