import random

from time import time

from bytewax.connectors.stdio import StdOutput
from bytewax.dataflow import Dataflow
from bytewax.inputs import StatefulSource, PartitionedInput, DynamicInput, StatelessSource


class RandomSink(StatelessSource):
    def __init__(self, long_input, index):
        self.last_time = time()
        self.iterator = iter(list(range(10)))
        self.long_input = long_input
        self.index = index

    def next(self):
        if self.index != 0:
            raise StopIteration()
        if self.long_input:
            # Return None until at least 0.5 secs
            # have passed, simulating a slow, non
            # blocking input
            if (time() - self.last_time) < 0.5:
                return None
            else:
                self.last_time = time()
        next(self.iterator)
        return random.randrange(0, 10)

    def close(self):
        pass


class RandomDynamicInput(DynamicInput):
    def __init__(self, long_input):
        self.long_input = long_input

    def build(self, worker_index, worker_count):
        return RandomSink(self.long_input, worker_index)


class RandomMetricSource(StatefulSource):
    def __init__(self, long_input):
        self.last_time = time()
        self.iterator = iter(list(range(10)))
        self.long_input = long_input

    def next(self):
        if self.long_input:
            # Return None until at least 0.5 secs
            # have passed, simulating a slow, non
            # blocking input
            if (time() - self.last_time) < 0.5:
                return None
            else:
                self.last_time = time()
        next(self.iterator)
        return random.randrange(0, 10)

    def snapshot(self):
        return None

    def close(self):
        pass


class RandomMetricInput(PartitionedInput):
    def __init__(self, partitions, long_input):
        self.i = 0
        self.partitions = partitions
        self.long_input = long_input

    def list_parts(self):
        return set([f"{i}" for i in range(1, self.partitions + 1)])

    def build_part(self, for_part, resume_state):
        self.i += 1
        return RandomMetricSource(self.long_input)


def double(x):
    return x * 2


def minus_one(x):
    return x - 1


def heavy_minus_one(x):
    # Heavy computation for ~0.5 seconds
    now = time()
    while (time() - now) < 0.5:
        # random cpu stuff
        p = 123123
        for i in range(p):
            p += 1
        p = 123112312321
        p = p * p * 2
    return x - 1


def stringy(x):
    return f"<dance>{x}</dance>"


def get_flow(partitions=1, long_input=False, heavy_map=False, dynamic_input=False):
    flow = Dataflow()
    if dynamic_input:
        flow.input("inp", RandomDynamicInput(long_input))
    else:
        flow.input("inp", RandomMetricInput(partitions, long_input))
    flow.map(double)
    if heavy_map:
        flow.map(heavy_minus_one)
    else:
        flow.map(minus_one)
    flow.map(stringy)
    flow.output("out", StdOutput())
    return flow
