import unittest
import optitrack

data_dir = "testData"

class BackwardsCompatibilityV1(unittest.TestCase):
    def test(self):
        run = optitrack.Run()
        run.ReadFile(data_dir, "v1.csv")
        self.assertEqual(run.version, 1)
        self.assertEqual(len(run.frames), 1668)
        self.assertEqual(run.trackablecount, 4)

        #TODO order should not matter here
        self.assertEqual(run.trackables[0].name, 'r')
        self.assertEqual(run.trackables[0].num_markers, 3)
        self.assertEqual(run.trackables[1].name, 'l')
        self.assertEqual(run.trackables[1].num_markers, 3)
        self.assertEqual(run.trackables[2].name, 'slider')
        self.assertEqual(run.trackables[2].num_markers, 6)
        self.assertEqual(run.trackables[3].name, 'rbt')
        self.assertEqual(run.trackables[3].num_markers, 5)
        t, d = run.trk("rbt")
        self.assertEqual(len(t), 1668)
        self.assertEqual(d.shape[0], 1668)
        self.assertEqual(d.shape[1], 5)
        self.assertEqual(d.shape[2], 3)

        #random spot check for data accuracy
        self.assertEqual(d[100, 1, 0], 1.25528145)
        self.assertEqual(d[100, 1, 1], -0.01398276)


class BackwardsCompatibilityV1_1(unittest.TestCase):
    def test(self):
        run = optitrack.Run()
        run.ReadFile(data_dir, "v1.1.csv")
        self.assertEqual(run.version, 1.1)

        self.assertEqual(len(run.frames), 548)
        self.assertEqual(run.trackablecount, 1)

        #TODO order should not matter here
        self.assertEqual(run.trackables[0].name, 'Rigid Body 1')
        self.assertEqual(run.trackables[0].num_markers, 5)

        t, d = run.trk("Rigid Body 1")
        self.assertEqual(len(t), 548)
        self.assertEqual(d.shape[0], 548)
        self.assertEqual(d.shape[1], 5)
        self.assertEqual(d.shape[2], 3)

        #random spot check for data accuracy
        self.assertEqual(d[100, 1, 0], 0.71552318)
        self.assertEqual(d[100, 1, 1], 10.0)

class BackwardsCompatibilityV1Nat(unittest.TestCase):
    def test(self):
        run = optitrack.Run()
        run.ReadFile(data_dir, "nat.csv") #Nat generated from natnethelper
        self.assertEqual(run.version, 1.0)

        self.assertEqual(run.trackablecount, 2)

        #TODO order should not matter here
        self.assertEqual(run.trackables[0].name, 'rbt')
        self.assertEqual(run.trackables[0].num_markers, 5)

        t, d = run.trk("rbt")
        self.assertEqual(len(t), 105)
        self.assertEqual(d.shape[0], 105)
        self.assertEqual(d.shape[1], 5)
        self.assertEqual(d.shape[2], 3)
if __name__ == "__main__":
    unittest.main()
