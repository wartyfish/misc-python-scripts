import pyperclip

def main():
    copied = pyperclip.paste()

    rows = []
    row = []

    for data in copied.split("\t"):    
        cell = data.split("\r\n")

        row.append(cell.pop(0))
            
        while cell:
            rows.append(row)
            row = [cell.pop(0)]

    rows.append(row)

    header = "|"
    header += "|".join(rows[0])
    header += "|\n"


    divider = "|"

    for col_index in range(len(rows[0])):
        divider += " --- |"

    divider += "\n"


    for row in rows[1:]:
        body += "|"
        body += "|".join(cell for cell in row)
        body += "|\n"

    table = header + divider + body

    pyperclip.copy(table)


try:
    main()
    print("Table copied to clipboard.")
except :
    print("Failed to copy table to clipboard.")