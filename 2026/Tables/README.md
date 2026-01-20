Table TUI v2

Interactive, terminal-based table viewer that allows the user to
navigate the table with the arrow keys.

The logic is layered into three parts for clarity and scalability.

Structure:
----------

1. Model (TableData)
    - Stores table data as a list of rows
    - Provides safe access to cell contents and table size
    - Handles any future data manipulation (sorting, editing, filtering)

2. View (TableRenderer)
    - Renders the table to the terminal
    - Computes column withds for proper alignment
    - Highlights the currently selected cell
    - Stateless: does not modify data or cursor state

3. Controller (TableApp)
    - Manages the main event loop
    - Receives input from the user via the Cursor object
    - Updates the cursor state and triggers redraws
    - Allows user to quit (Ctrl-C or "q") cleanly

4. Cursor
    - Tracks currently selected cell
    - Uses the bext module to handle input
    - Handles movement with arrows keys, wrapped around edges
    - Isolated from rendering logic

Features:
---------

- Arrow-key navigation with wrap-around
- Cell hihglighting
- Clean exit via "q" input from user