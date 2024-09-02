import re

def extract_number(text):
    # Use regular expression to find numbers, including decimals
    match = re.search(r'\b\d+(\.\d+)?\b', text)
    if match:
        return match.group()
    else:
        return None

# Example usage
text1 = "111115. Lay's Mix Variety Pack Potato Chips, 30 pk. $16.48"
number1 = extract_number(text1)
print(number1)  # Output: 1