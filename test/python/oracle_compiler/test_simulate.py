# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Tests LogicNetwork.simulate method."""

from ddt import ddt, data
from qiskit.circuit.oracle.compile_oracle import compile_oracle
from qiskit.test import QiskitTestCase
from .utils import get_truthtable_from_function, example_list
from .examples import identity, bit_and
example_list = [identity, bit_and]

@ddt
class TestSimulate(QiskitTestCase):
    """Tests LogicNetwork.simulate method"""
    # @data(*example_list())
    @data(*example_list)
    def test_(self, a_callable):
        """Tests LogicSimulate.simulate() on all the examples"""
        network = compile_oracle(a_callable)
        truth_table = network.simulate()
        self.assertEqual(truth_table, get_truthtable_from_function(a_callable))
