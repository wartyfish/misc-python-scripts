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

import  pyperclip, time, threading

paused = False

def input_listener():
    global paused

    while True:
        cmd = input().strip().lower()

        if cmd == "p":
            paused = not paused
            print("Paused." if paused else "Resumed.")


# Convert ab-delimited spreadsheet clipboard data into Markdown table
def tabler(copied_data) -> str:
    rows = []
    
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

            # Remove surrounding quotation marks if presewnt
            if cell.startswith('"') and cell.endswith('"'):
                cell = cell[1:-1]

            cleaned_row.append(cell)

        rows.append(cleaned_row)

    # Don't overwrite clipboard if it doesn't contain a table
    if len(rows) < 2:
        return copied_data

    header = "| " + " | ".join(rows[0]) + " |\n"
    divider = "| " + " | ".join(["---"] * len(rows[0])) + " |\n"

    body = ""
    for row in rows[1:]:
        body += "| " + " | ".join(row) + " |\n"

    table = header + divider + body

    return table

def main():
    print("Recording clipboard. Ctrl-C to stop, p to pause.")

    previous_content = ""

    # start input therad
    threading.Thread(target=input_listener, daemon=True).start()

    try:
        while True:

            # Only process clipboard when not paused
            if not paused:
                content = pyperclip.paste()

                if content != previous_content:
                    content = tabler(content)

                    pyperclip.copy(content)

                    previous_content = content
                
                time.sleep(0.1)

    except KeyboardInterrupt:
        pass


try:
    main()
except Exception as e:
    print("Failed to copy table to clipboard.")
    print(f"Error: {e}")
    exit(1)