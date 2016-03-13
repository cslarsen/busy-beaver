"""
Calculates the Busy Beaver Sigma function, naively.
"""

import bz2
import collections
import itertools
import os
import pickle
import sys


def log(string, stream=sys.stdout):
    stream.write(string)
    stream.flush()

def zero():
    # Used for pickling
    return 0

class Tape(object):
    def __init__(self, position=0, default_factory=zero):
        self.data = collections.defaultdict(default_factory)
        self._position = position
        self.leftmost = min(0, position)
        self.rightmost = max(0, position)
        self.shifts = 0

    def __eq__(self, other):
        return (self._position == other._position
                and self.leftmost == other.leftmost
                and self.rightmost == other.rightmost
                and self.shifts == other.shifts
                and self.data.items() == other.data.items())

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self.shifts += abs(self._position - value)
        self._position = value
        self._update_extremes()

    def _update_extremes(self):
        self.leftmost = min(self.leftmost, self.position)
        self.rightmost = max(self.rightmost, self.position)

    def read(self):
        return self.data[self.position]

    def write(self, value):
        self.data[self.position] = value

    def left(self):
        self.position -= 1

    def right(self):
        self.position += 1

    def values(self):
        for key in sorted(self.data.keys()):
            yield self.data[key]

    def __str__(self):
        separator = " "
        s = ""
        for index in range(self.leftmost, self.rightmost+1):
            s += "%s%s" % (self.data[index], separator)
        return s[:-1]

    def __repr__(self):
        items = 3
        extract = [v for n,v in enumerate(self.values()) if n<items]
        extra = ""
        if len(self.data) > items:
            extra = "... %d more" % len(self.data)-items
        return "<Tape: position=%d%s%s%s%s>" % (self.position,
                " values=[" if len(extract)>0 else "",
                ", ".join(map(repr, extract)), extra,
                "]" if len(extract)>0 else "")


class TuringMachine(object):
    def __init__(self, state=0, transition=None):
        """A Universal Turing machine.

        Args:
            transition: A dictionary of transitions between states. It should
                        be a dictionary with (current state, symbol read) keys
                        and (symbol to write, move left (-1) or right (1),
                        next state) values.
        """
        self.state = state
        self.tape = Tape()
        self.transition = transition

    def __eq__(self, other):
        return (self.state == other.state
                and self.tape == other.tape
                and self.transition == other.transition)

    def __repr__(self):
        return "<TuringMachine: state=%s tape=%s>" % (
                self.state, repr(self.tape))

    def __str__(self):
        return "%s %s" % (self.state, str(self.tape))

    def step(self):
        """Perform one computation step."""
        # Read symbol at current tape position
        symbol = self.tape.read()

        # Look up action based on the current state and the read symbol
        symbol, move, state = self.transition[(self.state, symbol)]

        # Perform these actions
        self.tape.write(symbol)
        self.tape.position += move
        self.state = state

    def run(self, steps=None):
        """Runs the machine an unlimited or given number of steps.

        Args:
            steps: If None, run indefinitely. If a positive number, run for
                   that number of steps.

        Raises:
            KeyError: The given state was not found. Effectively means to halt.
        """
        if steps is None:
            while True:
                self.step()
        else:
            for n in range(steps):
                self.step()


class BusyBeaver(TuringMachine):
    def __init__(self, transition):
        super(BusyBeaver, self).__init__(transition=transition)
        self.halts = None

    def ones(self):
        """Returns number of ones in the tape."""
        return sum(self.tape.values())

    def __eq__(self, other):
        return (super(BusyBeaver, self).__eq__(other)
                and self.halts == other.halts)

    def coded_ones(self):
        """Tape values as a number."""
        return int("".join(map(str, self.tape.values())), 2)


def show(machine):
    log("\n")
    log("  ones:  %d\n" % machine.ones())
    log("  steps: %d\n" % machine.tape.shifts)
    log("  tape:  %s\n" % machine.tape)

    format_state = lambda s: chr(ord("A") + s)
    format_move = lambda n: "L" if n==-1 else "R"
    format_next = lambda n: format_state(n) if n!="Z" else n

    def fmt(n,w,m):
        return "%s%s%s" % (format_next(n), w, format_move(m))

    it = iter(sorted(machine.transition.items()))
    try:
        while True:
            (state, symbol), (write, move, next) = it.next()
            a = fmt(next, write, move)
            (state2, symbol), (write, move, next) = it.next()
            assert state==state2, "Not a binary Busy Beaver?"
            b = fmt(next, write, move)
            log("  %s: %s %s\n" % (format_state(state), a, b))
    except StopIteration:
        pass

def format_trans(machine):
    s = ""
    format_state = lambda s: chr(ord("A") + s)
    format_move = lambda n: "L" if n==-1 else "R"
    format_next = lambda n: format_state(n) if n!="Z" else n

    def fmt(n,w,m):
        return "%s%s%s" % (format_next(n), w, format_move(m))

    it = iter(sorted(machine.transition.items()))
    try:
        while True:
            (state, symbol), (write, move, next) = it.next()
            a = fmt(next, write, move)
            (state2, symbol), (write, move, next) = it.next()
            assert state==state2, "Not a binary Busy Beaver?"
            b = fmt(next, write, move)
            s += "  %s: %s %s\n" % (format_state(state), a, b)
    except StopIteration:
        pass
    return s

def binary_machines(n):
    """The number of possible n-state, binary Turing machines."""
    return (4*(n+1))**(2*n)

def enum_instructions(states):
    """Yields all possible transitions for an n-state machine."""
    for state in reversed(["Z"] + list(range(states))):
        for symbol in [0, 1]:
            for move in [-1, 1]:
                yield (symbol, move, state)

def enum_transitions(states):
    """Generate all possible transition functions."""
    for i in itertools.product(enum_instructions(states), repeat=states*2):
        trans = {}
        n=0
        if len(i)>states:
            for state in range(states):
                for symbol in [0, 1]:
                    trans[(state, symbol)] = i[n]
                    n += 1
        yield trans

def plot_bbs(states, maxsteps):
    import matplotlib.pyplot as plt

    class Data(object):
        def __init__(self, width):
            self.data = []
            self.line = []
            self.width = width

        def add(self, result):
            self.line.append(result)
            if len(self.line) == self.width:
                self.data.append(self.line)
                self.line = []

    ones = Data((4*(states+1))**states)
    steps = Data((4*(states+1))**states)

    generator = Generator(states, maxsteps, "%d-state.pickled.bz2" % states)
    generator.run()
    log("Plotting ...")
    for (halts, shifts, tape) in generator.results:
        if halts:
            ones.add(generator.popcount(tape))
            steps.add(shifts)
        else:
            ones.add(0)
            steps.add(0)

    class Formatter(object):
        def __init__(self, im, label):
            self.im = im
            self.label = label

        def __call__(self, x, y):
            x = int(x)
            y = int(y)
            z = self.im.get_array()[y, x]
            s = "(%d,%d) %s=%d" % (x, y, self.label, z)
            return s

    doubleplot = False

    # Side-by-side plots
    if doubleplot:
        fig, (ax1, ax2) = plt.subplots(ncols=2)
        im1 = ax1.imshow(ones.data, interpolation="none", origin="upper")
        ax1.set_title("Ones")
        ax1.format_coord = Formatter(im1, "ones")
        im2 = ax2.imshow(steps.data, interpolation="none", origin="upper")
        ax2.set_title("Steps")
        ax2.format_coord = Formatter(im2, "steps")
    else:
        # Single plot
        fig, ax1 = plt.subplots()
        im1 = ax1.imshow(ones.data, interpolation="none", origin="upper")
        ax1.set_title("Ones")
        ax1.format_coord = Formatter(im1, "ones")
    plt.show()

def sigma(states, verbose=True):
    champion = BusyBeaver({})
    champion_ones = champion.ones()
    count = binary_machines(states)

    for num, tran in enumerate(enum_transitions(states), 1):
        candidate = BusyBeaver(transition=tran)
        try:
            if verbose and (num % 1111) == 0:
                log("%.2f%% %d / %d\r" % (100.0*num/count, num, count))
            candidate.run(107+1) # cheating: op>S(3) => op = 1+S(3)
            # above S from http://www.drb.insel.de/~heiner/BB/
            candidate.halts = False
            continue # Did not halt
        except KeyError:
            # By definition, halts
            candidate.halts = True
            pass

        if candidate.ones() > champion_ones:
            champion = candidate
            champion_ones = champion.ones()
            if verbose:
                log("%.2f%% %d / %d\r" % (100.0*num/count, num, count))
                show(champion)

    if verbose:
        log("%d-state machines enumerated: %d of %d\n" % (states, num, count))

    return champion_ones

class Generator(object):
    """Generates Busy Beavers with a file backing store, so that it can be
    resumed."""
    def __init__(self, states, maxsteps, filename):
        if os.path.exists(filename):
            log("Loading %s ... " % filename)
            g = Generator.load(filename)
            log("OK\n")
            self.states = g.states
            self.maxsteps = g.maxsteps
            self.filename = g.filename
            self.generator = g.generator
            self.results = g.results
        else:
            self.states = states
            self.maxsteps = maxsteps
            self.filename = filename
            self.generator = enum_transitions
            self.results = []

    @property
    def count(self):
        return len(self.results)

    @staticmethod
    def load(filename):
        with open(filename, "rb") as f:
            log("\n")
            data = f.read()
            log("\nDecompressing ...")
            data = bz2.decompress(data)
            log("\nUnpickling ...")
            data = pickle.loads(data)
            log("\nDone\n")
            return data

    def _save(self):
        tmp = "%s.tmp.%d" % (self.filename, os.getpid())
        with open(tmp, "wb") as f:
            log("Pickling ...")
            data = pickle.dumps(self)
            log("\nCompressing ...")
            data = bz2.compress(data)
            log("\nWriting ...")
            f.write(data)
            log("\nDone\n")
        os.rename(tmp, self.filename)

    def popcount(self, n):
        return bin(n).count("1")

    def champion(self):
        best = 0
        for (halts, shifts, tape) in self.results:
            best = max(best, self.popcount(tape))
        return best

    def run(self, save_every=3000000):
        printed = False
        made = 0
        total = binary_machines(self.states)

        for no, transition in enumerate(self.generator(self.states), 1):
            if no < self.count:
                continue

            if (no % 101) == 0:
                log("s=%d %d / %d          \r" % (self.states, no, total))
                printed = True

            try:
                candidate = BusyBeaver(transition=transition)
                candidate.run(1+self.maxsteps)
                candidate.halts = False
            except KeyError:
                candidate.halts = True

            self.results.append((candidate.halts, candidate.tape.shifts,
                candidate.coded_ones()))
            made += 1

            if (made % save_every) == 0:
                log("s=%d Saving %d / %d (%d) ...         \r" % (self.states,
                    self.count, total, made))
                self._save()

        if printed:
            log("\n")

        if made > 0:
            log("s=%d Saving %d ...              \r" % (self.states, self.count))
            self._save()
            log("\n")

def generate():
    try:
        for states in range(0, 5):
            generator = Generator(states, 107, "%d-state.pickled.bz2" % states)
            generator.run()
            log("Sigma(%d) = %d\n" % (generator.states, generator.champion()))
    except KeyboardInterrupt:
        pass

def main():
    if "-p" in sys.argv[1:]:
        # Plot
        plot_bbs(3, 107)
    elif "-g" in sys.argv[1:]:
        # Calc and pickle files
        generate()
    else:
        # Calc and show sigma... should use pickled files above
        for n in range(0,5):
            log("Sigma(%d) = %s\n" % (n, str(sigma(n))))

if __name__ == "__main__":
    main()
