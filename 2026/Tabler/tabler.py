"""
tabler.py

Watches the system clipboard for Excel/Shets table data and converts it 
into Markdown table format automatically.

Usage:
1. Run the script.
2. Copy a table from Excel, Google Sheets.
3. The clipboard contents will be converted into markdown table syntax.

Behaviour:
- The script continuously monitors the clipboard.
- When new content appears, it attempts to parse it as a tab-delimited table.
- If the content looks like a table (>= 2 rows), it converts it to Markdown.
- Line breaks inside cells are replaced nwith spaces to prevent formatting issues
- The converted table is written back to the clipboard automatically. 

Halt program with Ctrl-C
"""
# TODO: 
# - Add optional user input to put negative numbers in parenthesis
# - Stop stripping bold text
# - Right justify numbers

import  pyperclip, time, sys, threading

paused = False
right_justified = True
accounting = True

def input_listener():
    global paused
    global right_justified
    global accounting


    while True:
        cmd = input().strip().lower()

        if cmd == "p":
            paused = not paused
            print("Paused." if paused else "Resumed.")

        if cmd == "r":
            right_justified = not right_justified
            print("Right justification for numeric columns toggled ON." if right_justified else "Right justification for numeric columns toggled OFF.")

        if cmd == "a":
            accounting = not accounting
            print("Accounting numbers toggled ON." if accounting else "Accounting numbers toggled OFF.")

def strip_number_formatting(s):
    s = s.strip()

    # Remove common spreadsheet formatting
    s = s.replace(",", "")
    s = s.replace("£", "")
    s = s.replace("(", "-").replace(")","")

    return s


def is_number(s):
    if not s:
        return False
    
    s = strip_number_formatting(s)

    try:
        float(s)
        return True
    except ValueError:
        return False



# Convert tab-delimited spreadsheet clipboard data into Markdown table
def tabler(copied_data, right_justify: bool=True, accounting: bool=True) -> str:
    rows = []

    # Validate clipboard data is tab delimited 
    if "\t" not in copied_data:
        return copied_data
    
    # Validate clipboard data contains multiple lines
    if "\n" not in copied_data:
        return copied_data

    # Split clipboard text into rows
    for r in copied_data.strip().split("\r\n"):

        # Skip blank rows
        if not r.strip():
            continue
        
        cleaned_row = []

        # Split row into cells using tab delimiter
        for cell in r.split("\t"):

            # Remove internal line breaks 
            cell = str(cell).replace("\r", " ").replace("\n", " ").strip()

            # Remove surrounding quotation marks if present
            if cell.startswith('"') and cell.endswith('"'):
                cell = cell[1:-1]

            cleaned_row.append(cell)

        rows.append(cleaned_row)
    

    # ==================
    # = Table elements =
    # ==================
     
    header = "| " + " | ".join(rows[0]) + " |\n"

    # right justify numeric columns if right_justify=True
    if right_justify:
        spacers = []
        for col in range(len(rows[0])):  
            numeric = True  # assume column is numeric, look for non-numeric cell values 

            for row in rows[2:]:
                    if row[col].strip() and not is_number(row[col]):
                        numeric = False
                        break

            if numeric:
                spacers.append("--:")
            else:
                spacers.append("---")
        
        divider = "| " + " | ".join(spacers) + " |\n"

    else:
        divider = "| " + " | ".join(["---"] * len(rows[0])) + " |\n"

    body = ""
    for row in rows[1:]:
        if accounting:
            for i, cell in enumerate(row):
                if is_number(cell):
                    if float(strip_number_formatting(cell)) < 0:
                        row[i] = "(" + cell.strip("-") + ")"

        body += "| " + " | ".join(row) + " |\n"

    table = header + divider + body

    return table

def main():
    print("Recording clipboard. Ctrl-C to stop, p to pause.")
    print("Right justification for numeric columns ON. Press 'r' to toggle.")
    print("Accounting numbers ON (negative numbers parethesised). Press 'a' to toggle.")
    previous_content = ""

    # start input thread
    threading.Thread(target=input_listener, daemon=True).start()

    try:
        while True:

            # Only process clipboard when not paused
            if not paused:
                content = pyperclip.paste()

                if content != previous_content:
                    content = tabler(content, right_justify=right_justified)

                    pyperclip.copy(content)

                    previous_content = content
                
                time.sleep(0.1)

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Failed to copy table to clipboard.")
        print(f"Error: {e}")
        exit(1)