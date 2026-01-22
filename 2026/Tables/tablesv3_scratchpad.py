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
        
        #if self.max_col_width == None or self.max_col_width * self.number_of_cols > self.max_table_width:
        #    self.max_col_width                      = self.max_table_width // self.number_of_cols


    # Attempt 2: Expand all constrained columns 
    @property
    def column_widths(self):
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




        






    """
    Attempt 1
    @property
    def column_widths(self):
        # GOAL: minimize text-wrapping. 
        #       - minimize columns that need it
        #       - ensure that widest column has the most space
        #
        # TRY: expand all constrained columns to required width of the smallest contrained coll

        # Quotient of the Table width divided by number of columns
        equal_share, remainder = divmod(self.max_table_width, len(self.table.columns))
        
        # Required widths for no wrapping
        col_widths_ideal = [
            max(len(cell) for cell in col) + 3
            for col in self.table.columns
        ]

        col_widths_actual = [width for width in col_widths_ideal]

        if sum(col_widths_ideal) > self.max_table_width:
            # Total width distribute from narrow columns
            wiggle_room = sum([width - equal_share for width in col_widths_ideal if width > 0])
            
            # Create indexed dictionary of contrained columns
            constrained = {}
            for i, col in enumerate(col_widths_ideal):
                if col > equal_share:
                    constrained[i] = col

            number_of_contrained_columns = len(constrained)
            wiggle_room_per_c_c          = wiggle_room // number_of_contrained_columns
            
            # sort by narrowest columns
            constrained = dict(sorted(constrained.items(), key= lambda item: item[1]))

            print(equal_share)
            print(wiggle_room)


            narrowest_contrained_index, narrowest_constrained_width = next(iter(constrained.items()))

            # attempt to unconstrain the narrowest constrained column
            if equal_share + wiggle_room_per_c_c > narrowest_constrained_width:
                increase = narrowest_constrained_width - equal_share
                total_increase = increase * len(constrained)

                equal_share += increase
                wiggle_room -= increase

                print(equal_share)
                print(wiggle_room)

    """
                



                
                
                




        


        

def main():
    log_data = [
        ["Date", "Who booked?", "Who played?"],
        ["07/01/26", "Aida, Jamie", "Aida, Gabe, Hans, Jamie, Louis, Oscar"],
        ["14/01/26", "Aida, Gabe, Hans, Jamie, Louis, Oscar", "Aida, Archie, Cam, Dave, Gabe, Hans, Jamie, Jess, Jo, Louis, Oscar, Paddy, Ruth"],
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
    log_sheet_scribe    = TableRenderer(log_sheet, max_table_width= 100)

    stats_sheet         = TableData(stats_data)
    stats_sheet_scribe  = TableRenderer(stats_sheet, max_table_width= int(window_width // 2 - 2))

    log_sheet_scribe.column_widths

main()