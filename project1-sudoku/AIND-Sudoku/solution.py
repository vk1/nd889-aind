assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    new_values = values.copy()

    # List of boxes to modify
    unit_items_to_change = []

    # Loop over all units
    for unit in unitlist:
        
        # Loop over all boxes within a unit
        for unit_box in unit:

            # Make sure length of the string value is 2 to meet twin criteria
             if len(values[unit_box]) == 2:

                # For each such box, go over all boxes in unit to check if values match
                for choice_box in unit:

                    # Obviously ignore itself
                    if choice_box != unit_box:

                        # If values match, identical twin is found!
                        if values[choice_box] == values[unit_box]:

                            # Identical twin found. Now remove these values from other unit boxes
                            unit_items_to_change.extend(_naked_twins_removal(values, unit, choice_box, unit_box))

    # Now go through list of boxes that need to be modified and replace the twin's options with an empty string
    for item_to_change in unit_items_to_change:
        new_values[item_to_change[0]] = new_values[item_to_change[0]].replace(item_to_change[1], '')

    return new_values

def _naked_twins_removal(values, unit, twin_1, twin_2):
    """
    Create list of boxes to modify based on identical twins within a unit

    Args:
        values (dict): a dictionary of the grid of the form {'box_name': '123456789', ...}
        unit (list): list of boxes in unit
        twin_1 (string): first twin
        twin_2 (string): second twin

    Returns:
        unit_items_to_change (list): List of boxes to modify from unit, in the form
                                     [[box (str), value to remove from options (str)], ...]
    """
    unit_items_to_change = []

    # Loop over all boxes within unit
    for unit_box in unit:

        # Ignore the twins as these are not to be modified
        if unit_box not in (twin_1, twin_2):

            # Go over both values of the twin one-by-one
            for v in values[twin_1]: # 'twin_1' arbitrarily chosen here. Same values as 'twin_2'

                # If any other box in the same unit has a value found in twin_1/twin_2,
                #   then add to the list of boxes that need to be modified
                if v in values[unit_box]:
                    unit_items_to_change.append([unit_box, v])

    return unit_items_to_change
    
def cross(A, B):
    """Cross product of elements in A and elements in B.

    (Using utils.py from course page)
    """
    return [s+t for s in A for t in B]

def get_diag_units(rows, cols):
    """Return diagonal units of grid

    Returns:
        list of diagonal units
    """
    diag_1 = [r+c for r,c in zip(rows,cols)]
    diag_2 = [r+c for r,c in zip(rows,cols[::-1])]

    return [diag_1, diag_2]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.

    (Using utils.py from course page)
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form

    (Using utils.py from course page)
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.

    (Using solution.py from course page)
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values = assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.

    (Using solution.py from course page)
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.

    (Using solution.py from course page)
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the Naked Twins Strategy
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """Using depth-first search and propagation, try all possible values.

    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.

    (Using solution.py from course page)
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)

    return search(values)

def grid_structure():
    """
    Set the grid structure and components

    Returns:
        Variables used by rest of the script

    (Using utils.py from course page)
    """
    rows = 'ABCDEFGHI'
    cols = '123456789'

    boxes = cross(rows, cols)

    row_units = [cross(r, cols) for r in rows]
    column_units = [cross(rows, c) for c in cols]
    square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

    # Fetch the additional diagonal units
    diag_units = get_diag_units(rows, cols)

    # Add the 2 new diagonal units to the units list
    unitlist = row_units + column_units + square_units + diag_units

    units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

    return rows, cols, boxes, unitlist, units, peers

rows, cols, boxes, unitlist, units, peers = grid_structure()


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')