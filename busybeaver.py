"""
Calculates the Busy Beaver Sigma function, naively.

Run with Python3.
"""

import collections
import sys

class TuringMachine:
    def __init__(self, state=0, position=0, tape=None, transition=None):
        """A Universal Turing machine.

        Args:
            transition: A dictionary of transitions between states. It should
                        be a dictionary with (current state, symbol read) keys
                        and (symbol to write, move left (-1) or right (1),
                        next state) values.
        """
        self.state = state
        self.position = position
        self.tape = tape
        self.transition = transition

        if self.tape is None:
            self.tape = collections.defaultdict(lambda: 0)

        self.leftmost = 0
        self.rightmost = 0

    def __repr__(self):
        return "Machine(state=%s, position=%s, tape=%s, transition=%s)" % (
                self.state, self.position, self.tape, self.transition)

    def __str__(self):
        return "Machine(state=%s, position=%s, symbol=%s)" % (self.state,
                self.position, self.tape[self.position])

    def step(self):
        """Perform one computation step."""
        # Read symbol at current tape position
        symbol = self.tape[self.position]

        # Look up action based on the current state and the read symbol
        write, move, state = self.transition[(self.state, symbol)]

        # Perform these actions
        self.tape[self.position] = write
        self.position += move
        self.state = state

        if self.position < self.leftmost:
            self.leftmost = self.position
        if self.position > self.rightmost:
            self.rightmost = self.position

    def run(self, steps=None):
        """Runs the machine an unlimited or given number of steps.

        Args:
            steps: If None, run indefinitely. If a positive number, run for
                   that number of steps.
        """
        if steps is None:
            while True:
                self.step()
        else:
            for n in range(steps):
                self.step()


class BusyBeaver(TuringMachine):
    def __init__(self, transition):
        super().__init__(transition=transition)

    def ones(self):
        """Returns number of ones in the tape."""
        return sum(self.tape.values())



def print_result(machine):
    for (state, symbol), instr in sorted(machine.transition.items()):
        state = chr(ord("A") + state)
        write, move, next = instr
        if move == -1:
            move = "L"
        elif move == 1:
            move = "R"
        if next != "H":
            next = chr(ord("A") + next)
        print("%s %s: %s%s%s" % (state, symbol, write, move, next))
    print("Result: <%d> %s <%s>" % (machine.leftmost, " ".join(map(str,
        machine.tape.values())), machine.rightmost))

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

    best = -1
    for num, tran in enumerate(all_transitions()):
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
            best = ones
            sys.stdout.write("\rChampion %d: %d\n" % (num, best))
            sys.stdout.flush()
            print_result(machine)
    sys.stdout.write("\n")
    sys.stdout.flush()

    return best


if __name__ == "__main__":
    print("Sigma(2) = %d" % sigma(2))
