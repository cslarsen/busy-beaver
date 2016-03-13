import unittest
import busybeaver as bb

class Tape(unittest.TestCase):
    def test_initial_conditions(self):
        t = bb.Tape()
        self.assertEqual(t.position, 0)
        self.assertEqual(t.leftmost, 0)
        self.assertEqual(t.rightmost, 0)
        self.assertEqual(t.shifts, 0)
        self.assertEqual(t.read(), 0)

        t = bb.Tape(position=10, default=3)
        self.assertEqual(t.position, 10)
        self.assertEqual(t.leftmost, 0)
        self.assertEqual(t.rightmost, 10)
        self.assertEqual(t.shifts, 0)
        self.assertEqual(t.read(), 3)

        t = bb.Tape(position=-10, default=-4)
        self.assertEqual(t.position, -10)
        self.assertEqual(t.leftmost, -10)
        self.assertEqual(t.rightmost, 0)
        self.assertEqual(t.shifts, 0)
        self.assertEqual(t.read(), -4)

    def test_read_write(self):
        t = bb.Tape(default="default")
        t.write("one")
        self.assertEqual(t.read(), "one")
        t.left()
        self.assertEqual(t.position, -1)
        self.assertEqual(t.shifts, 1)
        self.assertEqual(t.leftmost, -1)
        self.assertEqual(t.rightmost, 0)
        self.assertEqual(t.read(), "default")
        t.write("minus1")
        self.assertEqual(t.read(), "minus1")

        t.left()
        t.write("minus2")
        self.assertEqual(t.read(), "minus2")
        t.right()
        self.assertEqual(t.read(), "minus1")
        t.right()
        self.assertEqual(t.read(), "one")
        t.right()
        self.assertEqual(t.read(), "default")
        t.position -= 3
        self.assertEqual(t.position, -2)
        self.assertEqual(t.read(), "minus2")
        self.assertEqual(t.leftmost, -2)
        self.assertEqual(t.rightmost, 1)
        self.assertEqual(t.shifts, 8)

        self.assertEqual(list(t.values()),
                ["minus2", "minus1", "one", "default"])
        self.assertEqual(str(t), "minus2 minus1 one default")

    def test_shifts(self):
        t = bb.Tape(position=-2)
        self.assertEqual(t.shifts, 0)
        t.position -= 3
        self.assertEqual(t.shifts, 3)

        t = bb.Tape(position=1)
        self.assertEqual(t.shifts, 0)
        t.position = 10
        self.assertEqual(t.shifts, 9)
        self.assertEqual(t.leftmost, 0)
        self.assertEqual(t.rightmost, 10)

        t = bb.Tape(position=-3)
        self.assertEqual(t.shifts, 0)
        t.position = 4
        self.assertEqual(t.shifts, 7)
        self.assertEqual(t.leftmost, -3)
        self.assertEqual(t.rightmost, 4)


class TuringMachine(unittest.TestCase):
    pass

class BusyBeaver(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
