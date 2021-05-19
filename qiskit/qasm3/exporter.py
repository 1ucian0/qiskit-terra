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

from .grammar import *
from qiskit.circuit import Gate
from qiskit.circuit.bit import Bit

class Exporter:
    def __init__(
        self,
        quantumcircuit,  # QuantumCircuit
        includes=None,  # list[filename:str]
    ):
        self.quantumcircuit = quantumcircuit
        self.includes = includes or self.requiered_includes()

    def requiered_includes(self):
        return []  # TODO

    def dump_lines(self):
        program = self.build_program()
        return program.qasm()

    def build_header(self):
        version = Version('3')
        includes = [Include(filename) for filename in self.includes]
        return Header(version, includes)

    def build_program(self):
        return Program(self.build_header(), self.build_statements())

    def build_statements(self):
        """
        globalStatement
            : subroutineDefinition
            | kernelDeclaration
            | quantumGateDefinition
            | calibration
            | quantumDeclarationStatement  # build_quantumdeclaration
            | pragma
            ;

        statement
            : expressionStatement
            | assignmentStatement
            | classicalDeclarationStatement
            | branchingStatement
            | loopStatement
            | endStatement
            | aliasStatement
            | quantumStatement  # build_quantuminstruction
            ;
        """
        # self.build_bigdeclarations()
        quantumdeclarations = self.build_quantumdeclarations()
        quantuminstructions = self.build_quantuminstructions()
        ret = []
        if quantumdeclarations:
            ret += [Skip()] + quantumdeclarations
        if quantuminstructions:
            ret += [Skip()] + quantuminstructions
        return ret

    def build_quantumdeclarations(self):
        ret = []
        for qreg in self.quantumcircuit.qregs:
            ret.append(QuantumDeclaration(Identifier(qreg.name), Designator(Integer(qreg.size))))
        return ret

    def build_quantuminstructions(self):
        ret = []
        for instruction in self.quantumcircuit.data:
            if isinstance(instruction[0], Gate):
                quantumGateName = Identifier(instruction[0].name)
                indexIdentifierList = []
                for qubit in instruction[1]:
                    indexIdentifierList.append(self.build_indexidentifier(qubit))
                ret.append(QuantumGateCall(quantumGateName, indexIdentifierList))
        return ret

    def build_indexidentifier(self, bit: Bit):
        return IndexIdentifier2(Identifier(bit.register.name), [Integer(bit.index)])
