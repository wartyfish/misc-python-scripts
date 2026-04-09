# TODO
Right justify all numeric columns, not just ints
    Try using:
        def is_number(s):
            try:
                float(s)
            except ValueError:  # Failed
                return False
            else:  # Succeeded
                return True

Toggleable option to parethesise negative numbers