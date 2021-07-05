# This code is part of Qiskit.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""TODO
"""

from typing import Optional, List, Callable, Union, Dict, Tuple
import logging
import warnings
from time import time
import numpy as np

from qiskit.circuit import QuantumCircuit, Parameter
from qiskit.circuit.library import RealAmplitudes
from qiskit.providers import BaseBackend
from qiskit.providers import Backend
from qiskit.opflow import (
    OperatorBase,
    ExpectationBase,
    ExpectationFactory,
    StateFn,
    CircuitStateFn,
    ListOp,
    I,
    CircuitSampler,
)
from qiskit.opflow.gradients import GradientBase
from qiskit.utils.validation import validate_min
from qiskit.utils.backend_utils import is_aer_provider
from qiskit.utils.deprecation import deprecate_function
from qiskit.utils import QuantumInstance, algorithm_globals
from qiskit.opflow import PauliSumOp
from ..optimizers import Optimizer, SLSQP
from ..variational_algorithm import VariationalAlgorithm, VariationalResult
from .minimum_eigen_solver import MinimumEigensolver, MinimumEigensolverResult
from ..exceptions import AlgorithmError


class System:
    def __init__(
        self,
        bit_strings: List[str],
        ansatz: QuantumCircuit,
        initial_parameter: float,  # TODO should it be a list? or a dict?
    ):
        self.bit_strings = bit_strings
        self.ansatz = ansatz
        self.initial_parameter = initial_parameter


class EntanglementForgingExpVal:
    def __init__(
        self,
        system1: System,
        system2: System,
        operator: PauliSumOp,
        quantum_instance: QuantumInstance or BaseBackend,
        symmetry=False,
    ):
        """

        Args:
            system1:
            system2:
            operator:
            quantum_instance:
            symmetry: Maybe, if system2 is None use system1 with same parameters.
        """
        # self._n = n   # TODO remove same as check len(bit_strings_1) + len(bit_strings_2)
        # self._k = k   # TODO remove size of bitstrings
        # self._bit_strings_1 = system1.bit_strings
        # self._bit_strings_2 = system2.bit_strings
        # self._ansatz_1 = self.ansatz_1
        # self._ansatz_2 = ansatz_2
        self.system1 = system1
        self.system2 = system2
        self._operator = operator
        self._quantum_instance = quantum_instance
        self.symmetry = symmetry

        # TODO: maybe also lazy evaluation on first evaluate instead of starting compilation here?
        self._operator_table = None

    @property
    def operator_table(self):
        if self._operator_table is None:
            self._calculate_operator_table()
        return self._operator_table

    def _calculate_operator_table(self):
        self._operator_table = []
        for h in self._operator:
            pauli_string = h.primitive.table.to_labels()[0]

            s1 = pauli_string[:len(self.system1.bit_strings)]
            s2 = pauli_string[len(self.system1.bit_strings):]

            O1 = PauliSumOp.from_list([(s1, 1)])
            O2 = PauliSumOp.from_list([(s2, 1)])
            self._operator_table.append((h.coeffs[0], O1, O2))

    def evaluate(self, params):
        start = 0
        end = self._ansatz_1.num_parameters
        theta_1 = params[start:end]

        start = end
        end += self._ansatz_2.num_parameters
        theta_2 = params[start:end]

        start = end
        end += self._k

        schmidt_coeffs = params[: self._]

        # initialize value
        value = 0.0

        # construct circuits
        ansatz_1 = self._ansatz_1.bind_parameters(theta_1)
        ansatz_2 = self._ansatz_2.bind_parameters(theta_2)
        for i in range(self._k):

            # <b_i|U^dag O_1 U|b_i>
            qc_1 = QuantumCircuit(self._n)
            qc_1.initialize(self._bit_strings_1[i])
            qc_1.append(ansatz_1)
            o_1_b_i = 0.0  # TODO

            # <b_i|V^dag O_2 V|b_i>
            qc_2 = QuantumCircuit(self._n)
            qc_2.initialize(self._bit_strings_2[i])
            qc_2.append(ansatz_2)
            o_2_b_i = 0.0  # TODO

            # add to value
            value += schmidt_coeffs[i] ** 2 * o_1_b_i * o_2_b_i

            for j in range(i):
                value_ij = 0.0
                for p in range(4):
                    qc_ijp = self._prepare_phi_n_m_p(
                        self.bit_strings_1[i], self.bit_strings_2[j], p
                    )
                    qc_ijp_1 = qc_ijp.compose(ansatz_1)
                    qc_ijp_2 = qc_ijp.compose(ansatz_2)
                    o_1_phi_ij_p = 0.0  # TODO
                    o_2_phi_ij_p = 0.0  # TODO
                    value_ij += (-1) ** p * o_1_phi_ij_p * o_2_phi_ij_p
                value += schmidt_coeffs[i] * schmidt_coeffs[j] * value_ij

        # return estimated value
        return value
