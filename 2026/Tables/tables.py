import os, time, bext

class Tables:
    def __init__(self, rows: list):
        self.rows = rows
        self.column_widths = []
        self.max_column_width = 50

        for col in range(len(rows[0])):
            self.column_widths.append(min(self.max_column_width, max([len(row[col]) for row in self.rows])))
          
        self.cursor = Cursor(len(self.rows), len(self.rows[0]))

    def print_table(self):
        for y in range(len(self.rows)):
            lines_per_row = divmod(max([len(col) for col in self.rows[y]]))
            
            for x in range(len(self.rows[0])):


                if x > 0:
                    print(" | ", end="")
                if len(self.rows[y][x] <= self.max_column_width):
                    print(f" {self.rows[y][x]:{self.column_widths[x]}} ", end="")
                else:

            print()

    def interactive_table(self) -> None:
        try:
            while True:
                os.system("cls")
                for y in range(len(self.rows)):
                    for x in range(len(self.rows[0])):
                        if x > 0:
                            print(" | ", end="")
                        
                        if y == self.cursor.y and x == self.cursor.x:
                            bext.bg("white")
                            bext.fg("black")
                            print(f" {self.rows[y][x]:{self.column_widths[x]}} ", end="")
                            bext.fg("white")
                            bext.bg("black")

                        else:
                            print(f" {self.rows[y][x]:{self.column_widths[x]}} ", end="")
                    print()

                self.cursor.move_cursor()

        except (KeyboardInterrupt, QuitTable):
            os.system("cls")
            print("Exited.")



class Cursor:
    def __init__(self, number_of_rows: int, number_of_cols: int):
        self.y = 1
        self.x = 0
        self.y_min = 1
        self.x_min = 0
        self.y_max = number_of_rows - 1
        self.x_max = number_of_cols - 1        
    
    def keyboard_input(self) -> str:
        key_stroke = bext.get_key()
        if key_stroke in ["up", "down", "left", "right"]:
            return key_stroke
        if key_stroke == "q":
            return "quit"

        return None

    def move_cursor(self) -> tuple:
        key_stroke = self.keyboard_input()

        if key_stroke == "up":
            self.y = self.y_min  + (self.y - self.y_min - 1) % (self.y_max - self.y_min + 1)

        if key_stroke == "down":
            self.y = self.y_min  + (self.y - self.y_min + 1) % (self.y_max - self.y_min + 1)

        if key_stroke == "right":
            self.x = self.x_min  + (self.x - self.x_min + 1) % (self.x_max - self.x_min + 1)

        if key_stroke == "left":
            self.x = self.x_min  + (self.x - self.x_min - 1) % (self.x_max - self.x_min + 1)

        if key_stroke == "quit":
            raise QuitTable
        
        return self.y, self.x
            
class QuitTable(Exception):
    pass

def main():
    rows = [
        ["Date", "Who booked?", "Who played?"],
        ["07/01/26", "Aida, Jamie", "Aida, Gabe, Hans, Jamie, Louis, Oscar"],
        ["14/01/26", "Cam, Dave, Ruth", "Aida, Archie, Cam, Dave, Gabe, Hans, Jamie, Jess, Jo, Louis, Oscar, Paddy, Ruth"],
        ["21/01/26", "Gabe, Hans", "Aida, David, Gabe, Hans, Jamie, Jess, Jo, Ruth"]
    ]

    table   = Tables(rows)

    table.interactive_table()



main()