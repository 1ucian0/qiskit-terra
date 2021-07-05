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

""" Test Entanglement Forging Expected Value"""

import unittest
from qiskit.test import QiskitTestCase

from qiskit.algorithms.minimum_eigen_solvers.ef_exp_val import EntanglementForgingExpVal, System
from qiskit.opflow.primitive_ops import PauliSumOp


class TestEntanglementForgingExpVal(QiskitTestCase):
    """Test Test Entanglement Forging Expected Value"""

    def test_operator_table_simple(self):
        """Test operator_table property."""
        hamiltonian = PauliSumOp.from_list([("IXYZ", 0.1), ("XIIZ", 0.2)])
        system1 = System("01", ansatz=None, initial_parameter=None)
        system2 = System("10", ansatz=None, initial_parameter=None)

        ef_expval = EntanglementForgingExpVal(
            system1, system2, operator=hamiltonian, quantum_instance=None
        )

        operator_table = ef_expval.operator_table

        self.assertEqual(len(operator_table), 2)

        self.assertEqual(len(operator_table[0]), 3)
        self.assertEqual(operator_table[0][0], 0.1)
        self.assertEqual(operator_table[0][1], PauliSumOp.from_list([("IX", 1)]))
        self.assertEqual(operator_table[0][2], PauliSumOp.from_list([("YZ", 1)]))

        self.assertEqual(len(operator_table[1]), 3)
        self.assertEqual(operator_table[1][0], 0.2)
        self.assertEqual(operator_table[1][1], PauliSumOp.from_list([("XI", 1)]))
        self.assertEqual(operator_table[1][2], PauliSumOp.from_list([("IZ", 1)]))


if __name__ == "__main__":
    unittest.main()
