import re


scanner = re.Scanner([
  (r'defined', lambda scanner, token: token),
  (r'[_A-Za-z][_0-9a-zA-Z]*', lambda scanner, token: token),
  (r'[0-9]+', lambda scanner, token: token),
  (r'\(', lambda scanner, token: token),
  (r'\)', lambda scanner, token: token),
  (r'\*', lambda scanner, token: token),
  (r'/', lambda scanner, token: token),
  (r'\+', lambda scanner, token: token),
  (r'-', lambda scanner, token: token),
  (r'!', lambda scanner, token: token),
  (r'>>', lambda scanner, token: token),
  (r'>', lambda scanner, token: token),
  (r'<<', lambda scanner, token: token),
  (r'<', lambda scanner, token: token),
  (r'&&', lambda scanner, token: token),
  (r'&', lambda scanner, token: token),
  (r'\|\|', lambda scanner, token: token),
  (r'\|', lambda scanner, token: token),
  (r'^\#if', None),
  (r'\s+', None),
])


operate = {
    '!': lambda x: not x,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x // y,
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '>>': lambda x, y: x >> y,
    '<<': lambda x, y: x << y,
    '>': lambda x, y: x > y,
    '<': lambda x, y: x < y,
    '&': lambda x, y: x & y,
    '^': lambda x, y: x ^ y,
    '|': lambda x, y: x | y,
    '&&': lambda x, y: x and y,
    '||': lambda x, y: x or y,
}


rank = {
    '(': 12,
    '!': 11,
    '*': 10,
    '/': 10,
    '+': 9,
    '-': 9,
    '>>': 8,
    '<<': 8,
    '>': 7,
    '<': 7,
    '&': 6,
    '^': 5,
    '|': 4,
    '&&': 2,
    '||': 2,
    ')': 1,     # XXX: I am not sure about this, but it works...
    '$': 1,
    None: 0,
}


def cpp_eval(expr, macros=None, debug=None):
    if macros is None:
        macros = {}

    if debug is None:
        debug = False

    results, remainder = scanner.scan(expr)

    # Abort if any characters are not tokenized
    if remainder:
        print('There are untokenized characters!')
        print('Expression:', repr(expr))
        print('Tokens:', results)
        print('Unscanned:', remainder)
        raise

    # Add an "end of line" character to force evaluation of the final tokens.
    results.append('$')

    # Shunting yard parser
    stack = []
    prior_op = None

    tokens = iter(results)
    for tok in tokens:
        if debug:
            print('tok:', tok)
            print('stack:', stack)
            print('prior_op:', prior_op)

        # Evaluate "defined()" statements
        # TODO: Create an "operator" for this...?
        if tok == 'defined':
            tok = next(tokens)

            parens = tok == '('
            if parens:
                tok = next(tokens)

            # "Identifiers that are not macros, which are all considered to be
            # the number zero." (CPP manual, 4.2.2)
            value = macros.get(tok, 0)

            # Negation
            # (Actually the unary prefix unary handler, I suppose.)
            while prior_op == '!':
                op = stack.pop()
                assert op == '!'
                value = operate[op](value)
                prior_op = stack[-1] if stack else None

            stack.append(value)

            if parens:
                tok = next(tokens)
                assert tok == ')'

        elif tok.isdigit():
            value = int(tok)
            stack.append(value)

        elif tok.isidentifier():
            # "Identifiers that are not macros, which are all considered to be
            # the number zero." (CPP manual, 4.2.2)
            value = macros.get(tok, 0)
            stack.append(value)

        elif tok in rank.keys():
            while rank[tok] <= rank[prior_op]:
                if debug:
                    print('  while stack:', stack)

                # Skip unary prefix operators (just ! at the moment)
                # NOTE: Maybe a sign that ! does not belong in this block.
                if tok == '!':
                    break

                second = stack.pop()
                op = stack.pop()
                first = stack.pop()

                value = operate[op](first, second)
                prior_op = stack[-1] if stack else None

                if prior_op == '(':
                    prior_op = None
                    if tok == ')':
                        stack.pop()

                stack.append(value)

                if debug:
                    print('  end while stack:', stack)
                    print('  end while prior_op:', prior_op)

            if tok == ')':
                prior_op = stack[-2] if stack and len(stack) > 1 else None
            else:
                stack.append(tok)
                prior_op = tok

                if prior_op in ('(',):
                    prior_op = None

        else:
            print("Unsupported token:", tok)
            raise

        if debug:
            print('end stack:', stack)
            print('end prior_op:', prior_op)
            print('----------------')

    # Remove the tail value
    eol = stack.pop()
    assert eol == '$'
    value = stack.pop()

    return value


# Some example expressions to evaluate

macros = {
    'a': True,
    'b': False,
    'c': True,
    'd': False,
}
print(macros)

examples = [
    '1 + 2 * 3 + 4',
    '1 + 2 * 3 - 4 / 5',
    '3 + 4 * 2 / (1 - 5)',
    '2 * (3 + 4)',
    '(3 + 4) * 2',
    '3 * (1 + 2 * 3 + 4) * 5',
    'defined(a)',
    'defined a',
    '!defined(a)',
    '!!defined(a)',
    'defined(a) && defined b',
    'defined(a) && !defined b',
    '!defined(a) && defined b',
    '!defined(a) && !defined b',
    'defined(a) || defined b',
    'defined(a) || !defined b',
    '!defined(a) || defined b',
    '!defined(a) || !defined b',
    'defined a && defined b && defined c',
    'defined a && !defined b && defined c',
    'defined a || defined b || defined c',
    '!defined a || defined b || !defined c',
    'defined a && defined b || defined c',
    'defined a || defined b && defined c',
    '!defined a || defined b && defined c',
    'defined(a) && defined(b) || !defined c && defined(d)',
    '(defined a || defined b) && defined c',
    '(defined a || defined b) && defined d',
    '2 > 3',
    '2 >> 3',
    '2 < 3',
    '2 << 3',
]

for expr in examples:
    print(expr)
    print('   ', cpp_eval(expr, macros=macros, debug=False))
