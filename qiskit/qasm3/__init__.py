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

"""
=========================
Qasm (:mod:`qiskit.qasm3`)
=========================

.. currentmodule:: qiskit.qasm3

"""

from .exporter import Exporter


def dumps(quantumcircuit):
    """Serializes a :class:`~qiskit.circuit.QuantumCircuit` object in an OpenQASM3 string.

    Args:
        quantumcircuit (QuantumCircuit): Circuit to serialize.

    Returns:
        str: The OpenQASM3 serialization
    """
    exporter = Exporter()
    return exporter.dumps(quantumcircuit)


def dump(quantumcircuit, flo):
    """Serializes a :class:`~qiskit.circuit.QuantumCircuit` object as a OpenQASM3 stream to file-like
    object (a .write()-supporting object).

    Args:
        quantumcircuit (QuantumCircuit): Circuit to serialize.
        flo (TextIOBase): file-like object to dump the OpenQASM3 serialization
    """
    Exporter().dump(quantumcircuit, flo)
