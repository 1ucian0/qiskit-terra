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

"""Tests oracle_ compiler type checker."""

from qiskit.test import QiskitTestCase
from qiskit.circuit.oracle import OracleCompilerTypeError
from qiskit.circuit.oracle.compile_oracle import compile_oracle
from . import examples, bad_examples


class TestTypeCheck(QiskitTestCase):
    """Tests oracle_ compiler type checker (good examples)."""

    def test_id(self):
        """Tests examples.identity type checking"""
        network = compile_oracle(examples.identity)
        self.assertEqual(network.args, ['a'])
        self.assertEqual(network.types, [{'Int1': 'type', 'a': 'Int1', 'return': 'Int1'}])

    def test_bool_not(self):
        """Tests examples.bool_not type checking"""
        network = compile_oracle(examples.bool_not)
        self.assertEqual(network.args, ['a'])
        self.assertEqual(network.types, [{'Int1': 'type', 'a': 'Int1', 'return': 'Int1'}])

    def test_id_assign(self):
        """Tests examples.id_assing type checking"""
        network = compile_oracle(examples.id_assing)
        self.assertEqual(network.args, ['a'])
        self.assertEqual(network.types, [{'Int1': 'type', 'a': 'Int1',
                                          'b': 'Int1', 'return': 'Int1'}])

    def test_bit_and(self):
        """Tests examples.bit_and type checking"""
        network = compile_oracle(examples.bit_and)
        self.assertEqual(network.args, ['a', 'b'])
        self.assertEqual(network.types, [{'Int1': 'type', 'a': 'Int1',
                                          'b': 'Int1', 'return': 'Int1'}])

    def test_bit_or(self):
        """Tests examples.bit_or type checking"""
        network = compile_oracle(examples.bit_or)
        self.assertEqual(network.args, ['a', 'b'])
        self.assertEqual(network.types, [{'Int1': 'type', 'a': 'Int1',
                                          'b': 'Int1', 'return': 'Int1'}])

    def test_bool_or(self):
        """Tests examples.bool_or type checking"""
        network = compile_oracle(examples.bool_or)
        self.assertEqual(network.args, ['a', 'b'])
        self.assertEqual(network.types, [{'Int1': 'type', 'a': 'Int1',
                                          'b': 'Int1', 'return': 'Int1'}])


class TestTypeCheckFail(QiskitTestCase):
    """Tests oracle_ compiler type checker (bad examples)."""

    def assertExceptionMessage(self, context, message):
        """Asserts the message of an exception context"""
        self.assertTrue(message in context.exception.args[0])

    def test_bit_not(self):
        """Int1wise not does not work on bit (aka bool)
          ~True   # -2
          ~False  # -1
        """
        with self.assertRaises(OracleCompilerTypeError) as context:
            compile_oracle(bad_examples.bit_not)
        self.assertExceptionMessage(context, 'does not operate with Int1 type')
