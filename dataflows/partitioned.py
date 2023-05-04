import random

from time import time

from bytewax.connectors.stdio import StdOutput
from bytewax.dataflow import Dataflow
from bytewax.inputs import StatefulSource, PartitionedInput, DynamicInput, StatelessSource


class RandomMetricSource(StatefulSource):
    def __init__(self, long_input):
        self.last_time = time()
        self.iterator = iter(list(range(20)))
        self.long_input = long_input

    def next(self):
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


def minus_one(x):
    return x - 1


def heavy_minus_one(x):
    # This will eat up a significant amount of both cpu and ram
    res = sum(list(range(1000000)))
    return x - 1


def stringy(x):
    return f"<dance>{x}</dance>"


def get_flow(long_input=False, heavy_map=False):
    flow = Dataflow()
    flow.input("inp", RandomMetricInput(16, long_input))
    if heavy_map:
        flow.map(heavy_minus_one)
    else:
        flow.map(minus_one)
    flow.map(stringy)
    flow.output("out", StdOutput())
    return flow
