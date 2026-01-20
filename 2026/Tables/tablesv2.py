"""
Minimal TUI Table Viewer.

A simple TUI for navigating a table and selecting cells. 

Requires: Python 3.12, bext module

"""
import os, bext

################################
# Table model: stores the data #
################################

class TableData():
    def __init__(self, rows: list):
        self.rows = rows    # rows = [[<headers>]]
                            #         [<row_1>]
                            #         [<row_2>]
                            #         ...
                            #         [<row_n>]]

    def cell(self, x, y) -> str:        # return selected cell
        return self.rows[y][x]      
    
    def size(self) -> tuple:            # returns number of rows and cols as tuple
        return len(self.rows), len(self.rows[0])
    

#############################
# Viewer: renders the table #
#############################

class TableRenderer():
    def __init__(self, table: TableData, max_col_width: int = 50):
        self.table = table
        self.max_col_width = max_col_width
    
    def get_column_widths(self):       
        column_widths = []

        for col in range(len(self.table.rows[0])):  # ignore max_col_width for the moment
            column_widths.append(min(self.max_col_width, max([len(row[col]) for row in self.table.rows])))

        return column_widths
    
    @property
    def table_width(self):
        return sum(self.get_column_widths()) + 3 * len(self.get_column_widths())

    def print_table(self, starting_x: int = 0, starting_y: int = 0):
        column_widths   = self.get_column_widths()
        x_offset = starting_x
        y_offset = starting_y

        for y in range(len(self.table.rows)):
            # Draw top border of the table
            if y == 0:
                bext.goto(x_offset, y_offset + y)
                print("┌", end="")
                print("─"*(sum(column_widths) + len(column_widths)*3 - 1), end="")
                print("┐")
                y_offset += 1
            
            if y == 1:
                bext.goto(x_offset, y_offset + y)
                print("│", end="")
                for x in range(len(self.table.rows[0])):
                    if x < len(self.table.rows[0]) - 1:
                        print("─"*(+column_widths[x]+2), end="┼")
                    else:
                        print("─"*(+column_widths[x]+2), end="│")
                y_offset += 1

            # Print rows
            for x in range(len(self.table.rows[0])):
                bext.goto(x_offset, y_offset + y)
                print("│", end="")
                print(f" {self.table.cell(x, y):{column_widths[x]}} ", end="")
                print("│")
                x_offset += column_widths[x] + 3
            
            x_offset = starting_x

        # Draw bottom border
        bext.goto(x_offset, y_offset + len(self.table.rows))
        print("└", end="")
        print("─"*(sum(column_widths) + len(column_widths)*3 - 1), end="")
        print("┘")


########
# main #
########

def main():
    raw_data = [
        ["Date", "Who booked?", "Who played?"],
        ["07/01/26", "Aida, Jamie", "Aida, Gabe, Hans, Jamie, Louis, Oscar"],
        ["14/01/26", "Cam, Dave, Ruth", "Aida, Archie, Cam, Dave, Gabe, Hans, Jamie, Jess, Jo, Louis, Oscar, Paddy, Ruth"],
        ["21/01/26", "Gabe, Hans", "Aida, David, Gabe, Hans, Jamie, Jess, Jo, Ruth"]
    ]

    table_data  = TableData(raw_data)
    scribe      = TableRenderer(table_data, max_col_width=200)

    os.system("cls")
    #scribe.print_table()

    table_width = scribe.table_width
    scribe.print_table()
    scribe.print_table(starting_x = table_width + 2)


if __name__ == "__main__":
    main()


# TODO:                 
# - Cursor    
# - Bext table positioning      
#   - Seperate row types seperately into individual methods
#   - Calculate absolute positions once: calculate x-offsets per col *before* drawing
#   - Compute y-offset once per row 
# - Max row length text wrapping


# Useful UTF-8 box-drawing characters:
# ┌ ┐ └ ┘ ─ │ ├ ┤ ┬ ┴ ┼