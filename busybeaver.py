"""
Calculates the Busy Beaver Sigma function, naively.
"""

import collections
import sys

class Tape(object):
    def __init__(self, position=0, default=0):
        self.tape = collections.defaultdict(lambda: default)
        self.position = position
        self.leftmost = 0
        self.rightmost = 0
        self.shifts = 0

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    def _update_extremes(self):
        self.leftmost = min(self.leftmost, self.position)
        self.rightmost = max(self.rightmost, self.position)

    def read(self):
        self._update_extremes()
        return self.tape[self.position]

    def write(self, value):
        self._update_extremes()
        self.tape[self.position] = value

    def left(self):
        self.position -= 1
        self.shifts += 1

    def right(self):
        self.position += 1
        self.shifts += 1

    def values(self):
        return self.tape.values()

    def __str__(self):
        s = ""
        for index in range(self.leftmost, self.rightmost+1):
            s += "%s " % self.tape[index]
        return s[:-1]

    def __repr__(self):
        return "<Tape: position=%d, default=%s, leftmost=%d, rightmost=%d, shifts=%d tape=%s>" % (
            self.position, self.tape.default_factory(), self.leftmost,
            self.rightmost, self.shifts, dict(self.tape))


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


def print_result(machine):
    for (state, symbol), instr in sorted(machine.transition.items()):
        state = chr(ord("A") + state)
        write, move, next = instr
        move = {-1: "L", 1: "R"}.get(move, move)
        next = chr(ord("A") + next) if next != "H" else next
        print("%s %s: %s%s%s" % (state, symbol, write, move, next))
    print("Result: %s --- %s" % (machine.tape, repr(machine.tape)))

def sigma(states):
    def instr():
        """Yields all possible transitions for an n-state machine."""
        for symbol in [0, 1]:
            for move in [-1, 1]:
                for state in ["H"] + list(range(states)):
                    yield (symbol, move, state)

    def all_transitions():
        """Generate all possible transition functions."""
        # TODO: This one is hardwired for two-state busy beaver
        for a in instr():
            for b in instr():
                for c in instr():
                    for d in instr():
                        trans = {
                            (0, 0): a,
                            (0, 1): b,
                            (1, 0): c,
                            (1, 1): d
                        }
                        yield trans

    best = 0
    bb = None
    for num, tran in enumerate(all_transitions(), 1):
        machine = BusyBeaver(transition=tran)
        try:
            #print(repr(machine))
            sys.stdout.write("\r%d" % num)
            sys.stdout.flush()
            machine.run(7) # cheating: the value of S(n)+1
            continue # Did not halt
        except KeyError:
            pass
        ones = machine.ones()
        if ones > best:
            bb = machine
            best = ones
            sys.stdout.write("\rChampion %d: %d\n" % (num, best))
            sys.stdout.flush()
            print_result(machine)
    sys.stdout.write("\n%d-state machines enumerated: %d (expected: %d)\n" %
            (states, num, (4*(states+1))**(2*states)))
    sys.stdout.flush()

    return (bb.tape.shifts, best)


if __name__ == "__main__":
    print("Sigma(2) = %s" % str(sigma(2)))
