from __future__ import annotations
import html
import re
import itertools
from dataclasses import dataclass
from collections.abc import Iterator
from typing import Self


class MathSyntaxError(Exception):
    pass


def tokenize(asciimath: str) -> Iterator[str]:
    token_regex = r'[0-9]+\.[0-9]+|[0-9]+|sqrt|\w|\+-|>=|<=|[+\-*/()<>=^. \n]|\".*?\"'
    prev_end = 0

    for m in re.finditer(token_regex, asciimath):
        if m.start() != prev_end:
            # TODO: test this
            raise MathSyntaxError(f"cannot tokenize {asciimath[prev_end:m.start()]!r}")

        value = m.group()
        if value != ' ' and value != "\n":
            yield value

        prev_end = m.end()

    if prev_end != len(asciimath):
        # TODO: test this
        raise MathSyntaxError(f"cannot tokenize {asciimath[prev_end:]!r}")


def validate_parens(tokens: Iterator[str]) -> Iterator[str]:
    open2close = {
        '(': ')',
        '[': ']',
        '{': '}',
    }
    opens = open2close.keys()
    closes = open2close.values()

    stack = []
    for t in tokens:
        if t in opens:
            stack.append(t)
        if t in closes:
            if not stack:
                raise MathSyntaxError(f"{t} not closed")
            if open2close[stack[-1]] != t:
                raise MathSyntaxError(f"{t} cannot be closed with {stack[-1]}")
            stack.pop()
        yield t

    if stack:
        raise MathSyntaxError(f"{stack[-1]} without a matching {open2close[stack[-1]]}")


@dataclass
class Variable:
    name: str  # e.g. "x"

    def is_tall(self) -> bool:
        return False

    def mathml(self) -> Iterator[str]:
        yield "<mi>"
        yield html.escape(self.name)
        yield "</mi>"

    def unwrap_parens(self) -> Self:
        return self


@dataclass
class Number:
    value: str  # e.g. "2"

    def is_tall(self) -> bool:
        return False

    def mathml(self) -> Iterator[str]:
        yield "<mn>"
        yield html.escape(self.value)
        yield "</mn>"

    def unwrap_parens(self) -> Self:
        return self


# "foo"
@dataclass
class Text:
    value: str

    def is_tall(self) -> bool:
        return False

    def mathml(self) -> Iterator[str]:
        yield "<mtext>"
        yield html.escape(self.value)
        yield "</mtext>"

    def unwrap_parens(self) -> Self:
        return self


@dataclass
class SimpleOperator:
    text: str  # e.g. "+-"

    def is_tall(self) -> bool:
        return False

    def mathml(self) -> Iterator[str]:
        mapping = {
            "+-": "&plusmn;",
            "-": "&minus;",
        }
        yield "<mo>"
        yield mapping.get(self.text) or html.escape(self.text)
        yield "</mo>"

    def unwrap_parens(self) -> Self:
        return self


# (foo)
@dataclass
class Parentheses:
    between_parens: Row

    def is_tall(self) -> bool:
        return self.between_parens.is_tall()

    def mathml(self) -> Iterator[str]:
        if self.is_tall():
            mo_params = ""
        else:
            mo_params = "stretchy=false"

        yield f"<mo {mo_params}>(</mo>"
        yield from self.between_parens.mathml()
        yield f"<mo {mo_params}>)</mo>"

    def unwrap_parens(self) -> Row:
        return self.between_parens


# top/bottom
@dataclass
class Division:
    top: Element
    bottom: Element

    def is_tall(self) -> bool:
        return True

    def mathml(self) -> Iterator[str]:
        yield "<mfrac>"
        yield from self.top.unwrap_parens().mathml()
        yield from self.bottom.unwrap_parens().mathml()
        yield "</mfrac>"

    def unwrap_parens(self) -> Self:
        return self


# base^exponent
@dataclass
class Power:
    base: Element
    exponent: Element

    def is_tall(self) -> bool:
        # TODO: not always true, consider x^(x^(x^(x^x)))
        return False

    def mathml(self) -> Iterator[str]:
        yield "<msup>"
        yield from self.base.unwrap_parens().mathml()
        yield from self.exponent.unwrap_parens().mathml()
        yield "</msup>"

    def unwrap_parens(self) -> Self:
        
        return self


# sqrt(foo), root(n)(foo)
@dataclass
class Root:
    which_root: Element | None  # None means sqrt
    under_root: Element

    def is_tall(self) -> bool:
        # TODO: does this produce good looking results?
        return True

    def mathml(self) -> Iterator[str]:
        assert self.which_root is None  # TODO
        yield "<msqrt>"
        yield from self.under_root.unwrap_parens().mathml()
        yield "</msqrt>"

    def unwrap_parens(self) -> Self:
        return self


# multiple concatenated math elements, e.g. "1 + 2a" is 4 elements
@dataclass
class Row:
    elements: list[Element]

    def is_tall(self) -> bool:
        return any(elem.is_tall() for elem in self.elements)

    def mathml(self) -> Iterator[str]:
        yield "<mrow>"
        for el in self.elements:
            yield from el.mathml()
        yield "</mrow>"


# Row is not an Element.
# Similar to how Statement is not an Expression in most programming languages.
Element = Variable | Number | Text | SimpleOperator | Parentheses | Division | Power | Root


# Closing paren (typically ')') is consumed from tokens but not included in the result.
def consume_until_closing_paren(tokens: Iterator[str]) -> list[str]:
    depth = 1
    result: list[str] = []
    while True:
        t = next(tokens)  # should never fail, parentheses balance is checked after tokenizing
        if t in "([{":
            depth += 1
        if t in ")]}":
            depth -= 1
            if depth == 0:
                return result
        result.append(t)


# consumes the given tokens as needed
def parse_element(tokens: Iterator[str]) -> Element:
    try:
        token = next(tokens)
    except StopIteration:
        # TODO: test this
        raise MathSyntaxError("unexpected end of math")

    if re.search(r"\d", token):
        # Contains digit character, e.g. "3.14"
        return Number(value=token)
    if re.fullmatch(r"[^\W\d]", token):
        # Wordy but no digits, e.g. "x"
        return Variable(name=token)
    if token in {"=", "-", "+-", "."}:
        return SimpleOperator(text=token)

    # Parenthesized parts must be elementary so that you can do x^(1 + 2)
    if token == '(':
        inside_parens = consume_until_closing_paren(tokens)
        return Parentheses(parse_row(iter(inside_parens)))

    if token.startswith('"'):
        return Text(token.strip('"'))

    # TODO: improve error message
    # TODO: test this
    raise MathSyntaxError(f"unknown token: {token!r}")


def parse_row(tokens: Iterator[str]) -> Row:
    result: list[Element] = []
    while True:
        match next(tokens, None):
            case None:
                break  # end of tokens
            case 'sqrt':
                result.append(Root(which_root=None, under_root=parse_element(tokens)))
            case 'root':
                result.append(Root(which_root=parse_element(tokens), under_root=parse_element(tokens)))
            case '/':
                if not result:
                    raise MathSyntaxError("division with no left side")
                result[-1] = Division(top=result[-1], bottom=parse_element(tokens))
            case '^':
                if not result:
                    raise MathSyntaxError("power with no base")
                result[-1] = Power(base=result[-1], exponent=parse_element(tokens))
            case t:
                result.append(parse_element(itertools.chain([t], tokens)))

    return Row(result)


# inline=True: Used in the middle of sentences.
# inline=False: Centered math blocks in the middle of text.
def asciimath_to_mathml(asciimath: str, inline: bool) -> str:
    raw_tokens = tokenize(asciimath)
    checked_tokens = validate_parens(raw_tokens)
    parsed = parse_row(checked_tokens)
    return "<math>" + "".join(parsed.mathml()) + "</math>"


if __name__ == "__main__":
    parsed = parse_row(validate_parens(tokenize("x = (-b+-sqrt(b^2-4ac))/(2a)")))
    print("".join(parsed.mathml()))
