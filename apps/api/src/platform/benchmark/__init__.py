"""Comparative benchmark: does Kollio's memory and contradiction beat a bare model?

See #77. The pure pieces (data, arms, blinding, scoring) are importable and
testable offline; the CLI in ``__main__`` drives them and keeps the live provider
calls opt-in and budgeted.
"""
