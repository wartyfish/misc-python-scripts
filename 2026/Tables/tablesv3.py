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
        self.rows = rows                                # rows      = [[<headers>]]
                                                        #              [<row_1>]
                                                        #              [<row_2>]
                                                        #              ...
                                                        #              [<row_n>]]

        self.columns = list(map(list, zip(*self.rows))) # columns   = transposed(rows)
                                                        #           = [[<col_1>], [<col_2>] ... [<col_n]]


    def cell(self, x, y) -> str:        # return selected cell
        return self.rows[y][x]      
    
    def size(self) -> tuple:            # returns number of rows and cols as tuple
        return len(self.rows), len(self.rows[0])
    

#############################
# Viewer: renders the table #
#############################

class TableRenderer():
    def __init__(self, table: TableData, max_table_width: int = 500, min_col_width: int = 8):
        self.table                                  = table
        self.number_of_rows, self.number_of_cols    = self.table.size()
        self.max_table_width                        = max_table_width
        self.min_col_width                          = min_col_width


    ##############
    # Properties #
    ##############

    @property
    def column_widths(self) -> list:
        number_of_cols = len(self.table.columns)

        ideal_widths = [max(len(cell) for cell in col) + 3 for col in self.table.columns]
        
        # Sort by shortest ideal widths
        order           = sorted(range(number_of_cols), key=lambda i: ideal_widths[i])
        ideal_sorted    = sorted(ideal_widths[i] for i in order)

        widths          = [self.min_col_width] * number_of_cols
        remaining       = self.max_table_width - self.min_col_width * number_of_cols

        if remaining <= 0:
            return widths
        
        active = number_of_cols
        current = self.min_col_width
        
        for k, target in enumerate(ideal_sorted):
            delta = target - current

            # If delta is zero or negative, target column is wide enough. Continue to remaining columns.
            if delta <= 0:
                active -=1
                continue

            cost = delta * active

            # If remaining >= cost, all columns can be widened to the width of the next narrowest column
            if remaining >= cost:
                # Widen all active columns to this level
                current = target
                remaining -= cost

                # Fix width of satisfied column
                i = order[k]
                widths[i] = target
                active -= 1

            # If table cannot afford to widen all columns by the target amount, 
            else:
                # Partial raise
                increment, remainder = divmod(remaining, active)
                current += increment
                remaining = 0
                break

        # Apply final level to unsatisfied columns
        for i in range(number_of_cols):
            widths[i] = min(ideal_widths[i], max(widths[i], current))


        return widths

    @property
    def cells_wrapped(self) -> list:
        cells_wrapped = []
        lines_per_row = []
        column_widths = self.column_widths

        for y in range(len(self.table.rows)):
            cells = [textwrap.wrap(self.table.cell(x, y), column_widths[x]) for x in range(len(self.table.rows[0]))]
            lines = (max(len(cell) for cell in cells))

            # Add blankspace beneath unwrapped lined
            for cell in cells:
                while len(cell) < lines:
                    cell.append("")

            cells_wrapped.append(cells)
            lines_per_row.append(lines)

        return cells_wrapped
    

    #############################
    # Render table & components #
    #############################

    def print_table(self, x_offset: int=0, y_offset: int=0) -> None:
        y_offset += self.print_top_border(x_offset, y_offset)
        y_offset += self.print_headers(x_offset, y_offset)
        y_offset += self.print_table_seperator(x_offset, y_offset)
        y_offset += self.print_data_rows(x_offset, y_offset)
        self.print_bottom_border(x_offset, y_offset)



    def print_top_border(self, x_offset: int=0, y_offset: int=0) -> int:        
        bext.goto(x_offset, y_offset)

        print("┌", end="")
        print("─"*(sum(self.column_widths) + len(self.column_widths)*3 - 1), end="")
        print("┐")

        return 1

    def print_headers(self, x_offset: int=0, y_offset: int=0) -> int:
        col_offsets     = list(accumulate((col + 3 for col in self.column_widths), initial=0))  # +3 to accomodate at least one blank space either side and the vertical bar
        cell_offsets    = [col + 2 for col in col_offsets[:-1]]                                 # Print cell data two spaces to the right of all but the last column
        lines           = len(self.cells_wrapped[0][0])

        for x in range(len(col_offsets)):
            # Print columns
            for line in range(lines):
                bext.goto(x_offset + col_offsets[x], y_offset + line)
                print("│")

            # Print cells
            if x < len(col_offsets) - 1:                    # One more column than cell
                for line in range(lines):
                    bext.goto(x_offset + cell_offsets[x], y_offset + line)
                    print(self.cells_wrapped[0][x][line])

        return lines
            
    def print_table_seperator(self, x_offset: int=0, y_offset: int=0) -> int:
        bext.goto(x_offset, y_offset)

        print("│", end="")
        for x in range(len(self.table.rows[0])):
            if x < len(self.table.rows[0]) - 1:
                print("─"*(+ self.column_widths[x]+2), end="┼")
            else:
                print("─"*(+ self.column_widths[x]+2), end="│")

        return 1
    
    def print_data_rows(self, x_offset: int=0, y_offset: int=0) -> int:
        col_offsets     = list(accumulate((col + 3 for col in self.column_widths), initial=0))  # +3 to accomodate at least one blank space either side and the vertical bar
        cell_offsets    = [col + 2 for col in col_offsets[:-1]]                                 # Print cell data two spaces to the right of all but the last column
        lines_per_row   = [len(row[0]) for row in self.cells_wrapped[1:]]

        extra_lines    = 0

        # Print columns and cell values
        for y in range(1, len(self.table.rows)):            # Skip headers
            for x in range(len(col_offsets)):    
                # Print columns
                for line in range(lines_per_row[y-1]):
                    bext.goto(x_offset + col_offsets[x], y_offset + (y-1) + line + extra_lines)
                    print("│")

                # Print cell values
                if x < len(col_offsets) - 1:                # One more column than cell
                    for line in range(lines_per_row[y-1]):
                        bext.goto(x_offset + cell_offsets[x], y_offset + (y-1) + line + extra_lines)
                        print(self.cells_wrapped[y][x][line])     
                   
            extra_lines += lines_per_row[y-1] - 1              # Account for wrap-around lines

        return len(self.table.rows) - 1 + extra_lines

    def print_bottom_border(self, x_offset: int=0, y_offset: int=0) -> None:
        bext.goto(x_offset, y_offset)

        print("└", end="")
        print("─"*(sum(self.column_widths) + len(self.column_widths)*3 - 1), end="")
        print("┘")
    
        

########
# main #
########

def main():
    log_data = [
        ["Date", "Who booked?", "Who played?"],
        ["07/01/26", "Aida, Jamie", "Aida, Gabe, Hans, Jamie, Louis, Oscar"],
        ["14/01/26", "Cam, Dave, Ruth", "Aida, Archie, Cam, Dave, Gabe, Hans, Jamie, Jess, Jo, Louis, Oscar, Paddy, Ruth"],
        ["21/01/26", "Gabe, Hans", "Aida, David, Gabe, Hans, Jamie, Jess, Jo, Ruth"]
    ]

    stats_data = [
        ["Name", "Sessions played", "Sessions booked", "Sessions since last booking", "Bookings per session"],
        ["Oscar", "7", "1", "4", "0.14"],
        ["Louis", "5", "1", "2", "0.2"],
        ["Jess", "10", "2", "2", "0.2"],
        ["Aida", "11", "3", "2", "0.27"],
        ["Jamie", "11", "3", "2", "0.27"],
        ["Archie", "1", "0", "1", "0"],
        ["David", "1", "0", "1", "0"],
        ["Max", "4", "1", "1", "0.25"],
        ["Paddy", "8", "2", "1", "0.25"],
        ["Ruth", "8", "2", "1", "0.25"],
        ["Dave", "7", "2", "0", "0.29"],
        ["Hans", "7", "2", "0", "0.29"],
        ["Cam", "3", "1", "0", "0.33"],
        ["Gabe", "10", "4", "0", "0.4"],
        ["Jo", "2", "1", "0", "0.5"]
    ]

    window_width        = bext.width()
    window_height       = bext.height()

    log_sheet           = TableData(log_data)
    log_sheet_scribe    = TableRenderer(log_sheet, max_table_width= int(window_width // 4 - 2))

    stats_sheet         = TableData(stats_data)
    stats_sheet_scribe  = TableRenderer(stats_sheet, max_table_width= int(window_width // 4 - 2))


    os.system("cls")


    log_sheet_scribe.print_table(0, 0)
    stats_sheet_scribe.print_table(int(window_width // 4) + 10, 0)



if __name__ == "__main__":
    main()


# TODO:                 
# - Cursor    
# - Bext table positioning ✓
#   - Seperate row types seperately into individual methods ✓
#   - Calculate absolute positions once: calculate x-offsets per col *before* drawing ✓
#   - Compute y-offset once per row ✓
#   - Investigate rich module 
# - Text wrapping ✓
#   - Optimise col widths to minimize text wrapping ✓
#   - Allow user to specify header height 
#  


# Useful UTF-8 box-drawing characters:
# ┌ ┐ └ ┘ ─ │ ├ ┤ ┬ ┴ ┼