from fsquery import FSNode, FSQuery

import unittest, re



class TestFSNode(unittest.TestCase) :

    def test1(self) :
        fsq = FSQuery(".").Ext("py").FileOnly()
        self.assertEqual(len([x for x in fsq]),3)

    def test2(self) :
        fsq = FSQuery(".").Ext("md").FileOnly().Contains("consumption")
        ns = [x for x in fsq]
        self.assertEqual(len(ns),1)       


if __name__ == '__main__' :
    unittest.main()
