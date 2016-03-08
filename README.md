Busy Beaver
===========

Approximates the [Busy Beaver Σ-function][busybeaver], naïvely.

Σ(n) is the largest number of 1s a non-halting, n-state Turing machine will
print on its tape. They don't have to be consecutive, but the machine *must*
halt.

More interestingly, the Σ-function is non-computable. Let me explain.

To calculate Σ(n), enumerate all n-state Turing machines and run them. When a
machine halts, count the number of 1s on its tape, and remember the machine
with the most ones so far --- the champion.

But soon you will encounter a machine that doesn't seem to halt. If you can
conclusively *prove* that it will never halt, you ignore it --- Busy beaver
machines are, by definition, non-halting machines. But by the halting theorem,
you *cannot* prove that it will halt or not. You can create some clever
heuristics that will identify large classes of machines that are provably in a
loop. That is completely fine, and absolutely workable. But, you will *never*
cover all cases. So at that point, you have to bring in human operators to
investigate whether a given machine halts or not. That's also fine, but is
really just another version of the same problem. Are there machines that humans
won't be able to prove halts or not? Absolutely. I haven't seen one yet, but we
know from mathematics that there are statements that cannot be proven or
disproven. Statements that are true, but cannot be proven so.

That's why I made this program: I want to find some cool, but simple Turing
machines that I myself can't figure out will ever halt or not.

Status
------

The program currently only handles 2-state, 2-symbol Turing machines: So it can
only find Σ(2). Furthermore, I side-step the halting problem by cheating: I
stop programs after running more than S(2) operations.

How to run
----------

Just type `python busybeaver.py`. It supports Python 2 and 3.

Author and license
------------------

Copyright (C) 2016 Christian Stigen Larsen  
Distributed under the GPL v3 or later.

[busybeaver]: https://en.wikipedia.org/wiki/Busy_beaver
