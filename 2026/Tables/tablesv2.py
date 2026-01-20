"""
Minimal TUI Table Viewer.

A simple TUI for navigating a table and selecting cells. 

Requires: Python 3.12, bext module

"""
import os, bext, textwrap
from itertools import accumulate

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
    
    def get_column_widths(self) -> list:       
        column_widths = []

        for col in range(len(self.table.rows[0])):  # ignore max_col_width for the moment
            column_widths.append(min(self.max_col_width, max([len(row[col]) for row in self.table.rows])))

        return column_widths
    
    @property
    def table_width(self) -> int:
        return sum(self.get_column_widths()) + 3 * len(self.get_column_widths())
    
    
    def print_top_border(self, x_offset: int=0, y_offset: int=0) -> None:
        column_widths = self.get_column_widths()
        bext.goto(x_offset, y_offset)

        print("┌", end="")
        print("─"*(sum(column_widths) + len(column_widths)*3 - 1), end="")
        print("┐")

    def print_headers(self, x_offset: int=0, y_offset: int=0) -> None:
        column_widths = self.get_column_widths()
        bext.goto(x_offset, y_offset)

        print("│", end="")
        for x in range(len(self.table.rows[0])):
            print(f" {self.table.cell(x, 0):{column_widths[x]}} ", end="")
            print("│", end="")
        
    def print_table_seperator(self, x_offset: int=0, y_offset: int=0) -> None:
        column_widths = self.get_column_widths()
        bext.goto(x_offset, y_offset)

        print("│", end="")
        for x in range(len(self.table.rows[0])):
            if x < len(self.table.rows[0]) - 1:
                print("─"*(+column_widths[x]+2), end="┼")
            else:
                print("─"*(+column_widths[x]+2), end="│")

    def wrap_cells(self) -> list:
        cells_wrapped = []
        lines_per_row = []

        for y in range(len(self.table.rows)):
            cells = [textwrap.wrap(self.table.cell(x, y), self.max_col_width) for x in range(len(self.table.rows[0]))]
            lines = (max(len(cell) for cell in cells))

            # Add blankspace beneath unwrapped lined
            for cell in cells:
                while len(cell) < lines:
                    cell.append("")

            cells_wrapped.append(cells)
            lines_per_row.append(lines)

        return cells_wrapped
    
    def print_data_rows(self, x_offset: int=0, y_offset: int=0) -> None:
        col_offsets     = list(accumulate((col + 3 for col in self.get_column_widths()), initial=0)) # +3 to accomodate at least one blank space either side and the vertical bar
        cell_offsets    = [col + 2 for col in col_offsets[:-1]]     # Print cell data two spaces to the right of all but the last column
        cells_wrapped   = self.wrap_cells()
        lines_per_row   = [len(row[0]) for row in cells_wrapped[1:]]

        # Print columns and cell values
        for y in range(1, len(self.table.rows)):            # Skip headers
            for x in range(len(col_offsets)):    
                # Print columns
                for line in range(lines_per_row[y-1]):
                    bext.goto(x_offset + col_offsets[x], y_offset + (y-1) + line)
                    print("│")

                # Print cell values
                if x < len(col_offsets) - 1:                # One more col than header
                    for line in range(lines_per_row[y-1]):
                        bext.goto(x_offset + cell_offsets[x], y_offset + (y-1) + line)
                        print(cells_wrapped[y][x][line])     
                   
            y_offset += lines_per_row[y-1] - 1              # Account for wrap-around lines

    def print_bottom_border(self, x_offset: int=0, y_offset: int=0):
        col_widths      = self.get_column_widths()
        col_offsets     = list(accumulate((col + 3 for col in self.get_column_widths()), initial=0))

        for x in range(len(col_offsets) - 1):
            bext.goto(x_offset + col_offsets[x], y_offset)
            print("└", end="")
            print("─"*col_widths[x], end="")
        bext.goto(x_offset + col_offsets[-1], y_offset)
        print("┘")

        

        


        
"""
    def print_data_rows(self, x_offset: int=0, y_offset: int=0) -> None:
        column_widths = self.get_column_widths()
        col_offsets = list(accumulate((col + 3 for col in column_widths), initial=0))
        row_offset = 0      # calculated in situ

        for y in range(1, len(self.table.rows)):
            # Wrap cells
            cells_wrapped = [textwrap.wrap(self.table.cell(x, y), self.max_col_width) for x in range(len(self.table.rows[0]))]
            number_of_lines = max(len(cell) for cell in cells_wrapped)

            # Add blankspace to the bottom of unwrapped lines
            for cell in cells_wrapped:
                while len(cell) < number_of_lines:
                    cell.append("")

            # Print table boundaries
            for x in range(len(col_offsets)):
                for line in range(number_of_lines):
                    bext.goto(x_offset + col_offsets[x], y_offset + (y - 1) + row_offset + line)
                    print("│")
                
            # Print cells
            for x in range(len(self.table.rows[0])):
                for line in range(number_of_lines):
                    bext.goto(x_offset + col_offsets[x] + 2, y_offset + (y - 1) + row_offset + line)
                    print(cells_wrapped[x][line])
            
            row_offset += number_of_lines - 1

    #def print_bottom_border(self, x_offset=0, y_offset=0):
        


    def print_table(self, x_offset: int = 0, y_offset: int = 0):
        column_widths   = self.get_column_widths()

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
"""

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
    scribe      = TableRenderer(table_data, max_col_width=50)

    os.system("cls")
    #scribe.print_table()
    #table_width = scribe.table_width
    #scribe.print_table()
    #scribe.print_table(starting_x = table_width + 2)

    scribe.print_top_border(10, 5)
    scribe.print_headers(10, 6)
    scribe.print_table_seperator(10, 7)
    scribe.print_data_rows(10, 8)
    scribe.print_bottom_border(10, 12)


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