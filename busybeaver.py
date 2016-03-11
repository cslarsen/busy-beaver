"""
Calculates the Busy Beaver Sigma function, naively.
"""

import collections
import itertools
import sys

def binary_machines(n):
    """The number of possible n-state, binary Turing machines."""
    return (4*(n+1))**(2*n)

def log(string, stream=sys.stdout):
    stream.write(string)
    stream.flush()

class Tape(object):
    def __init__(self, position=0, default=0):
        self.data = collections.defaultdict(lambda: default)
        self._position = position
        self.leftmost = 0
        self.rightmost = 0
        self.shifts = 0

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self.shifts += abs(value)
        self._position = value

    def _update_extremes(self):
        self.leftmost = min(self.leftmost, self.position)
        self.rightmost = max(self.rightmost, self.position)

    def read(self):
        self._update_extremes()
        return self.data[self.position]

    def write(self, value):
        self._update_extremes()
        self.data[self.position] = value

    def left(self):
        self.shifts += 1
        self.position -= 1

    def right(self):
        self.shifts += 1
        self.position += 1

    def values(self):
        return self.data.values()

    def __str__(self):
        s = ""
        for index in range(self.leftmost, self.rightmost+1):
            s += "%s " % self.data[index]
        return s[:-1]

    def __repr__(self):
        return "<Tape: position=%d, default=%s, leftmost=%d, rightmost=%d, shifts=%d data=%s>" % (
            self.position, self.data.default_factory(), self.leftmost,
            self.rightmost, self.shifts, dict(self.data))


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

    def __repr__(self):
        return "Machine(state=%s, position=%s, tape=%s, transition=%s, shifts=%s)" % (
                self.state, self.position, self.tape, self.transition,
                self.shifts)

    def __str__(self):
        return "Machine(state=%s, position=%s, symbol=%s, shifts=%s)" % (self.state,
                self.position, self.tape[self.position], self.shifts)

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

    def ones(self):
        """Returns number of ones in the tape."""
        return sum(self.tape.values())


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

def sigma(states):
    def instr():
        """Yields all possible transitions for an n-state machine."""
        for symbol in [0, 1]:
            for move in [-1, 1]:
                for state in ["Z"] + list(range(states)):
                    yield (symbol, move, state)

    def all_transitions():
        """Generate all possible transition functions."""
        for i in itertools.product(instr(), repeat=states*2):
            trans = {}
            n=0
            if len(i)>states:
                for state in range(states):
                    for symbol in [0, 1]:
                        trans[(state, symbol)] = i[n]
                        n += 1
            yield trans

    champion = BusyBeaver({})

    count = binary_machines(states)
    for num, tran in enumerate(all_transitions(), 1):
        candidate = BusyBeaver(transition=tran)
        try:
            if num % 101 == 0:
                log("%.2f%% %d / %d\r" % (100.0*num/count, num, count))
            candidate.run(107+1) # cheating: op>S(3) => op = 1+S(3)
            # above S from http://www.drb.insel.de/~heiner/BB/
            continue # Did not halt
        except KeyError:
            # By definition, halts
            pass
        log("%.2f%% %d / %d\r" % (100.0*num/count, num, count))
        if candidate.ones() > champion.ones():
            champion = candidate
            show(champion)

    log("%d-state machines enumerated: %d of %d\n" % (states, num, count))
    return champion.ones()


if __name__ == "__main__":
    for n in range(0,5):
        log("Sigma(%d) = %s\n" % (n, str(sigma(n))))
