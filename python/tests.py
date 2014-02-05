"""
* Copyright (c) 2014, Franklin W. Olin College of Engineering

* All rights reserved.
*

* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*

* - Redistributions of source code must retain the above copyright notice,
* this list of conditions and the following disclaimer.
* - Redistributions in binary form must reproduce the above copyright notice,

* this list of conditions and the following disclaimer in the documentation
* and/or other materials provided with the distribution.
* - Neither the name of Franklin W. Olin College of Engineering nor the names

* of its contributors may be used to endorse or promote products derived
* from this software without specific prior written permission.
*

* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE

* ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
* LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
* CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF

* SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
* INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
* CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)

* ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
* POSSIBILITY OF SUCH DAMAGE.
*
*
"""
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

if __name__ == "__main__":
    unittest.main()
