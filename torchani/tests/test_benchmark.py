import torch
import torchani
import unittest
import copy


class TestBenchmark(unittest.TestCase):

    def setUp(self):
        self.conformations = 100
        self.species = list('CHNO')
        self.coordinates = torch.randn(self.conformations, 4, 3)
        self.count = 100

    def _testModule(self, module, asserts):
        keys = []
        for i in asserts:
            if '>=' in i:
                i = i.split('>=')
                keys.append(i[0].strip(), i[1].strip())
            elif '<=' in i:
                i = i.split('<=')
                keys.append(i[0].strip(), i[1].strip())
            elif '>' in i:
                i = i.split('>')
                keys.append(i[0].strip(), i[1].strip())
            elif '<' in i:
                i = i.split('<')
                keys.append(i[0].strip(), i[1].strip())
            elif '=' in i:
                i = i.split('=')
                keys.append(i[0].strip(), i[1].strip())
            else:
                keys.append(i.strip())
        self.assertEqual(set(module.timers.keys()), set(keys))
        for i in keys:
            self.assertEqual(module.timers[i], 0)
        old_timers = copy.copy(module.timers)
        for _ in range(self.count):
            module(self.coordinates, self.species)
            for i in keys:
                self.assertLess(old_timers[i], module.timers[i])
            for i in asserts:
                if '>=' in i:
                    i = i.split('>=')
                    key0 = i[0].strip()
                    key1 = i[1].strip()
                    self.assertGreaterEqual(
                        module.timers[key0], module.timers[key1])
                elif '<=' in i:
                    i = i.split('<=')
                    key0 = i[0].strip()
                    key1 = i[1].strip()
                    self.assertLessEqual(
                        module.timers[key0], module.timers[key1])
                elif '>' in i:
                    i = i.split('>')
                    key0 = i[0].strip()
                    key1 = i[1].strip()
                    self.assertGreater(
                        module.timers[key0], module.timers[key1])
                elif '<' in i:
                    i = i.split('<')
                    key0 = i[0].strip()
                    key1 = i[1].strip()
                    self.assertLess(module.timers[key0], module.timers[key1])
                elif '=' in i:
                    i = i.split('=')
                    key0 = i[0].strip()
                    key1 = i[1].strip()
                    self.assertEqual(module.timers[key0], module.timers[key1])
        module.reset_timers()
        self.assertEqual(set(module.timers.keys()), set(keys))
        for i in keys:
            self.assertEqual(module.timers[i], 0)

    def testNeighborAEV(self):
        aev_computer = torchani.NeighborAEV()
        self._testModule(aev_computer, ['total>neighborlist', 'total>aev'])

    def testAEV(self):
        aev_computer = torchani.AEV()
        self._testModule(aev_computer, ['aev'])

    def testModelOnAEV(self):
        aev_computer = torchani.NeighborAEV()
        model = torchani.ModelOnAEV(aev_computer)
        self._testModule(model, ['forward>aev', 'forward>nn'])