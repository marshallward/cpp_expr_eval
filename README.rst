================================
C Preprocessor expression parser
================================

Example of how to parse a CPP (C preprocessor) expression, as might appear
inside of ``#if`` block expressions, e.g.::

   #if defined(A) || defined(B)
   #include A.h
   #else
   #include B.h
   #endif

This is only about how to parse the contents of ``#if``, not the whole block
itself.

This is not complete, nor is it written as a formal grammar, but it's pretty
close in both respects.

What is working:

* Macro substitution
* ``define`` tests
* Most operators (mainly arithmetic and logic)

This is mostly for learning, don't get too excited.  We finally broke down and
decided these need to be included in ``makedep``, and here we are.
