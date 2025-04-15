import re


class RomanConverter:
    """Handles conversion of Roman numerals to Arabic numerals and floor notation."""

    @staticmethod
    def roman_to_arabic(roman):
        """Convert a Roman numeral to an Arabic numeral."""
        values = {
            "I": 1, "V": 5, "X": 10, "L": 50,
            "C": 100, "D": 500, "M": 1000
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

    @classmethod
    def convert_mixed_numerals(cls, num):
        """
        Convert mixed floor notation (Roman/Arabic) into a standardized format.
        Examples:
            "VPR" or "PR" -> "Ground Floor"
            "IV/6" -> "4/6"
        """
        if "VPR" in num or "PR" in num:
            return re.sub(r"PR|VPR", "Ground Floor", num)

        if "/" not in num:
            return f"{cls.roman_to_arabic(num)}/?"

        parts = num.split("/")
        roman = parts[0]

        arabic_num = cls.roman_to_arabic(roman)

        return f"{arabic_num}/{parts[1]}"