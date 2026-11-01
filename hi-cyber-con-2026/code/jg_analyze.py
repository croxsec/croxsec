#!/usr/bin/env python3
# JGMTFM - checkerboard 5x10 decoder attempts
tokens = "53 74 u3 17 35 x3 x2 76 24 33 93 u3 16 v4 36 v4 93 32 64 22 z3 x2 42 w4 54 05 v2 v5 63 v6 26 23 26 33 86 u3 33 x3 74 x2 06 54 62 x5 22 74 44 04 45 v5 93 x2".split()
print("n tokens:", len(tokens))
letter_toks = [t for t in tokens if not t[0].isdigit()]
digit_toks  = [t for t in tokens if t[0].isdigit()]
print("letter-led:", len(letter_toks), letter_toks)
print("digit-led:", len(digit_toks), digit_toks)

# Checkerboard hypothesis: 5 letters {u,v,w,z,x} map to rows 0..4 (or 1..5)
# digits 0-9 map to columns. Alphabet 5x10 = 50 cells -> covers a..z (26) + digits (10) + extras
# Standard: cell (r,c) -> char
import itertools

def board_to_text(order_letters, mapping='row', start=0):
    # letter-led token "L d" -> row=order_letters.index(L), col=int(d)
    # digit-led token "d1 d2" -> ? maybe row=d1, col=d2 directly
    out = []
    for t in tokens:
        if t[0].isdigit():
            out.append(('?', int(t[0]), int(t[1])))
        else:
            r = order_letters.index(t[0])
            c = int(t[1])
            out.append((r, c, None))
    return out

for perm in itertools.permutations('uvwxz'):
    res = board_to_text(perm)
    # printable summary for a couple of orders
    pass

# print token structure positions
for i, t in enumerate(tokens):
    print(i, t, end='   ')
    if (i+1) % 8 == 0: print()
print()
