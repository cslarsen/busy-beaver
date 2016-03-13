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

Just type `python busybeaver.py`. It supports Python 2 and 3. Protip: Use pypy.

Plots
-----

![Plot of 2-state Busy Beavers](bb.png "2-state Busy Beavers")

Above I plot the number of ones and steps for all 2-state, binary Turing
Machines starting with a blank tape. Each pixel is a machine, and its color is
blue if the machine did not halt. The order stems from the way I enumerate the
transition functions, and is a bit arbitrary here. Even so, we can clearly see
clusters of machines with many ones. This shows that some configurations lead
to well performing Busy Beavers, which is self-evident, but nice to see. It
would be very cool to try to order the plottig sequence in some meaningful way.

To run the plot, run the `plot_bbs` function. It requires `matplotlib`.

Todo
----

  * Run all machines at once, one step at a time (at least in batches).
  * Multiplex batches onto processes with multiprocessing
  * Find a cheap way to suspend and resume machines (e.g., make unique
    numerical ID for each machine, save tape + ID, instead of dicts).
  * With all above, have a queue, the ones that halt are removed from queue,
    keep chugging on the ones that don't seem to finish.
  * Finally, add some heuristics for detecting non-halting machines. Try to
    cover all cases for Sigma(0..2) at least.

Author and license
------------------

Copyright (C) 2016 Christian Stigen Larsen  
Distributed under the GPL v3 or later.

[busybeaver]: https://en.wikipedia.org/wiki/Busy_beaver
