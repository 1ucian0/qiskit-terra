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

from .grammar import Version, Include, Header, Program


class Exporter:
    def __init__(
        self,
        quantumcircuit,  # QuantumCircuit
        includes=None,  # list[filename:str]
    ):
        self.quantumcircuit = quantumcircuit
        self.includes = includes or self.requiered_includes()

    def requiered_includes(self):
        return []

    def dump(self):
        program = self.build_program()
        return program.qasm()

    def build_header(self):
        version = Version('3')
        includes = [Include(filename) for filename in self.includes]
        return Header(version, includes)

    def build_program(self):
        return Program(self.build_header(), self.build_statements())

    def build_statements(self):
        quantumdeclaration = QuantumDeclaration(identifier)