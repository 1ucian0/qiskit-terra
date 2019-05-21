# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from copy import deepcopy
from qiskit.execute import execute
from qiskit.providers.basicaer import BasicAer

from qiskit.test import QiskitTestCase

from qiskit.circuit import ClassicalRegister, QuantumRegister, QuantumCircuit

def random_circuit(Data):
    qr = QuantumRegister(3, 'q')
    cr = ClassicalRegister(3, 'c')
    circuit = QuantumCircuit(qr, cr)
    circuit.h(qr[1])
    circuit.cx(qr[1], qr[2])
    circuit.measure(qr, cr)
    return circuit

class FuzzOptmizationLevels(QiskitTestCase):

    def __init__(self, Data):
        self.circuit = random_circuit(Data)
        self.seed_simulator = int.from_bytes(Data.read(1), byteorder='little')
        self.random_bool = self.seed_simulator < 42

    def assertEqualCounts(self, *counts):
        average = {}
        for value in set(counts[0]).intersection(*counts[1:]):
            average[value] = sum([count[value] for count in counts])/len(counts)

        for count in counts:
            for value in count.keys():
                self.assertEqual(count[value], average[value])

    def optmization_levels(self):
        backend = BasicAer.get_backend('qasm_simulator')

        circuit = self.circuit
        seed_simulator = self.seed_simulator
        seed_transpiler = seed_simulator

        counts_0 = execute(deepcopy(circuit),
                           backend, optimization_level=0,
                           seed_simulator=seed_simulator,
                           seed_transpiler=seed_transpiler).result().get_counts()
        counts_1 = execute(deepcopy(circuit),
                           backend, optimization_level=1,
                           seed_simulator=seed_simulator,
                           seed_transpiler=seed_transpiler,
                           ).result().get_counts()
        counts_2 = execute(deepcopy(circuit),
                           backend, optimization_level=2,
                           seed_simulator=seed_simulator,
                           seed_transpiler=seed_transpiler,
                           ).result().get_counts()

        if self.random_bool:
            counts_3 = execute(deepcopy(circuit),
                           backend, optimization_level=3,
                           seed_simulator=seed_simulator,
                           seed_transpiler=seed_transpiler,
                           ).result().get_counts()
        else:
            counts_3 = deepcopy(counts_2)

        self.assertEqualCounts(counts_0, counts_1, counts_2, counts_3)

def optmization_levels(Data):
    test = FuzzOptmizationLevels(Data)
    test.optmization_levels()

if __name__ == '__main__':
    import io
    data = io.BytesIO(b"abcdef")
    optmization_levels(data)
