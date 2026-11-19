"""Lab 2 tools: a safe calculator and a Wikipedia lookup."""
import ast
import operator as op

import requests

OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.USub: op.neg,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    """Evaluate arithmetic safely with ast (never eval)."""
    try:
        expr = expression.replace(",", "")
        result = _eval(ast.parse(expr, mode="eval").body)
        # show 1025 instead of 1025.0 when the result is a whole number
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def wiki_lookup(title: str) -> str:
    """Return the first 800 characters of a Wikipedia page summary."""
    try:
        url = ("https://en.wikipedia.org/api/rest_v1/page/summary/"
               + title.strip().replace(" ", "_"))
        r = requests.get(url, timeout=10, headers={"User-Agent": "DCIT403-lab"})
        if r.status_code != 200:
            return f"No Wikipedia page found for '{title}'."
        return r.json().get("extract", "")[:800]
    except Exception as e:  # network down, timeout, bad JSON
        return f"Error: could not reach Wikipedia ({e})."


TOOLS = {"calculator": calculator, "wiki_lookup": wiki_lookup}

if __name__ == "__main__":
    print(calculator("4*185 + 3*95"))             # 1025
    print(calculator("1200 - 1025"))              # 175
    print(calculator("1,200 - 1,025"))            # 175 (commas stripped)
    print(calculator("__import__('os')"))         # Error: Unsupported expression
    print(calculator("2 ** 10"))                  # Error (Pow not allowed)
    print(wiki_lookup("Bono East Region"))
    print(wiki_lookup("Zzzz not a real page 12345"))
