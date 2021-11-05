import itertools


def _stringify(num, parens=False):
    string = str(abs(num))
    if "/" in string:
        string = r"\frac{%s}{%s}" % (abs(num).numerator, abs(num).denominator)
    if num < 0:
        string = "-" + string
    if num < 0 and parens:
        string = fr"\left( {string} \right)"
    return string


class MatrixWithRowOperations:
    def __init__(self, rows):
        self._color_iter = itertools.cycle([
            r'\red{%s}'.__mod__,
            r'\blue{%s}'.__mod__,
            r'\magenta{%s}'.__mod__,
            r'\green{%s}'.__mod__,
            r'\darkyellow{%s}'.__mod__,
        ])
        self._rows = [list(row) for row in rows]
        self._current_colors = [next(self._color_iter) for row in self._rows]
        self._output = []
        self._append_current_state_to_output()

    def _pick_color(self):
        # Goals:
        #   - Use all available colors
        #   - Do not choose
        #   - Avoid choosing colors that have been recently used
        for color in self._color_iter:
            if color not in self._current_colors:
                return color

    def _append_current_state_to_output(self):
        self._output.append(r"\begin{bmatrix}")
        for index, (color, row) in enumerate(zip(self._current_colors, self._rows)):
            line = " " * 4 + " & ".join(color(_stringify(v)) for v in row)
            if index < len(self._rows):
                line += r" \\"
            self._output.append(line)
        self._output.append(r"\end{bmatrix}")

    # rows[index] *= by
    def multiply_row(self, index, by):
        assert index >= 0
        assert by != 0
        self._output.append(r'&\to')
        old_color = self._current_colors[index]
        new_color = self._pick_color()

        self._rows[index] = [by*v for v in self._rows[index]]
        self._current_colors[index] = new_color
        self._append_current_state_to_output()

        self._output.append(r"\quad")
        self._output.append(new_color(r"\text{new %s}" % self._row_name(index)))
        self._output.append(r"= %s \cdot " % _stringify(by, parens=True))
        self._output.append(old_color(r"\text{old %s}" % self._row_name(index)))
        self._output.append(r'\\')

    def _row_name(self, i):
        assert len(self._rows) == 3
        return ["top", "middle", "bottom"][i]

    # rows[dest] += scalar*rows[src]
    def add_multiple(self, src, dest, scalar):
        assert src != dest
        self._output.append(r'&\to')
        self._rows[dest] = [
            d + scalar * s for d, s in zip(self._rows[dest], self._rows[src])
        ]

        old_color = self._current_colors[dest]
        new_color = self._pick_color()
        self._current_colors[dest] = new_color
        self._append_current_state_to_output()

        self._output.append(r"\quad")
        self._output.append(new_color(r"\text{new %s}" % self._row_name(dest)))
        self._output.append("=")
        self._output.append(old_color(r"\text{old %s}" % self._row_name(dest)))
        self._output.append(r"+ %s \cdot " % _stringify(scalar, parens=True))
        self._output.append(self._current_colors[src](r"\text{%s}" % self._row_name(src)))
        self._output.append(r'\\')

    def get_output(self):
        output = self._output.copy()
        if output[-1] == '\\':
            output.pop()
        return r"\begin{align}" + "\n" + "\n".join(output) + "\n" + r"\end{align}"
