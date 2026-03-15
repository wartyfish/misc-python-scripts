import pyperclip

copied = pyperclip.paste()

rows = []
row = []

for data in copied.split("\t"):    
    cell = data.split("\r\n")

    row.append(cell.pop(0))
        
    while len(cell) > 0:
        rows.append(row)
        row = [cell.pop(0)]

rows.append(row)

header = "|"
header += "|".join(cell for cell in rows[0])
header += "|\n"


divider = "|"

for col_index in range(len(rows[0])):
    divider += " --- |"

divider += "\n"


body = "|"

for row in rows[1:]:
    body += "|"
    body += "|".join(cell for cell in row)
    body += "|\n"

table = header + divider + body

pyperclip.copy(table)
