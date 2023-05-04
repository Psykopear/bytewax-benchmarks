import random

from time import time

from bytewax.connectors.stdio import StdOutput
from bytewax.dataflow import Dataflow
from bytewax.inputs import StatefulSource, PartitionedInput, DynamicInput, StatelessSource


class RandomSink(StatelessSource):
    def __init__(self, long_input, index, partitions):
        self.last_time = time()
        self.iterator = iter(list(range(20)))
        self.long_input = long_input
        self.index = index
        self.partitions = partitions

    def next(self):
        if self.index > self.partitions:
            raise StopIteration()
        if self.long_input:
            # Return None until at least 0.25 secs
            # have passed, simulating a slow, non
            # blocking input
            if (time() - self.last_time) < 0.25:
                return None
            else:
                self.last_time = time()
        next(self.iterator)
        return random.randrange(0, 10)

    def close(self):
        pass


class RandomDynamicInput(DynamicInput):
    def __init__(self, long_input, partitions):
        self.long_input = long_input
        self.partitions = partitions

    def build(self, worker_index, worker_count):
        return RandomSink(self.long_input, worker_index, self.partitions)


def minus_one(x):
    return x - 1


def heavy_minus_one(x):
    # Heavy computation for ~0.125 seconds
    now = time()
    while (time() - now) < 0.125:
        # random cpu stuff
        p = 123123
        for i in range(p):
            p += 1
        p = 123112312321
        p = p * p * 2
    return x - 1


def stringy(x):
    return f"<dance>{x}</dance>"


def get_flow(long_input=False, heavy_map=False):
    flow = Dataflow()
    flow.input("inp", RandomDynamicInput(long_input, 16))
    if heavy_map:
        flow.map(heavy_minus_one)
    else:
        flow.map(minus_one)
    flow.map(stringy)
    flow.output("out", StdOutput())
    return flow
