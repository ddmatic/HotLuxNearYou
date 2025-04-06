import re
import os
from config import ROOT, BAT_FILE_PATH, DATA_DIR, SCRIPTS_DIR


def roman_to_arabic(roman):
    values = {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000
    }

    result = 0
    prev_value = 0

    # Process the Roman numeral from right to left
    for char in reversed(roman):
        current_value = values[char]

        # If current value is greater than or equal to previous value, add it
        # Otherwise subtract it (handles cases like IV = 4, IX = 9)
        if current_value >= prev_value:
            result += current_value
        else:
            result -= current_value

        prev_value = current_value

    return result


def convert_mixed_numerals(num: str) -> str:
    if "VPR" in num or "PR" in num:
        return re.sub(r"PR|VPR", "Ground Floor", num)

    if "/" not in num:
        return str(roman_to_arabic(num)) + "/?"

    parts = num.split("/")
    roman = parts[0]

    arabic_num = roman_to_arabic(roman)

    return f"{arabic_num}/{parts[1]}"


def create_hyperlink(url):
    return f'=HYPERLINK("{url}", "ClickToGo")'


def create_or_update_bat_file():
    src_dir = os.path.join(ROOT, "src")

    # Generate the full path for the .bat file
    bat_content = f'''@echo off
    cd /d "{src_dir}"
    python main.py
    pause
    '''

    # Write the content to the .bat file
    with open(BAT_FILE_PATH, 'w') as bat_file:
        bat_file.write(bat_content)

    print(f"\nCreated or updated the .bat file at {BAT_FILE_PATH}")

def create_paths():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SCRIPTS_DIR, exist_ok=True)