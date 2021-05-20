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
from qiskit.circuit import Gate, Barrier
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

    def build_statements(self) -> [Statement]:
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
        bitdeclarations = self.build_bitdeclarations()
        quantumdeclarations = self.build_quantumdeclarations()
        quantuminstructions = self.build_quantuminstructions(self.quantumcircuit.data)
        ret = []
        if bitdeclarations:
            ret += [Skip()] + bitdeclarations
        if quantumdeclarations:
            ret += [Skip()] + quantumdeclarations
        if quantuminstructions:
            ret += [Skip()] + quantuminstructions
        return ret

    def build_bitdeclarations(self):
        ret = []
        for creg in self.quantumcircuit.cregs:
            ret.append(BitDeclaration(Identifier(creg.name), Designator(Integer(creg.size))))
        return ret

    def build_quantumdeclarations(self):
        ret = []
        for qreg in self.quantumcircuit.qregs:
            ret.append(QuantumDeclaration(Identifier(qreg.name), Designator(Integer(qreg.size))))
        return ret

    def build_quantuminstructions(self, instructions):
        ret = []
        for instruction in instructions:
            if isinstance(instruction[0], Gate):
                if instruction[0].condition:
                    ret.append(self.build_branchingstatement(instruction))
                else:
                    ret.append(self.build_quantumgatecall(instruction))
            elif isinstance(instruction[0], Barrier):
                indexIdentifierList = self.build_indexIdentifierlist(instruction[1])
                ret.append(QuantumBarrier(indexIdentifierList))
            else:
                raise NotImplementedError(f'{instruction[0]} is not implemented in the QASM3 exporter')
        return ret

    def build_branchingstatement(self, instruction):
        eqcondition = self.build_eqcondition(instruction[0].condition)
        programTrue = self.build_programblock([instruction])
        return BranchingStatement(eqcondition, programTrue)

    def build_programblock(self, instructions):
        return ProgramBlock(self.build_quantuminstructions(instructions))

    def build_eqcondition(self, condition):
        """Classical Conditional condition from a instruction.condition"""
        return ComparisonExpression(Identifier(condition[0].name),
                                     EqualsOperator(),
                                     Integer(condition[1]))


    def build_indexIdentifierlist(self, bitlist: [Bit]):
        indexIdentifierList = []
        for bit in bitlist:
            indexIdentifierList.append(self.build_indexidentifier(bit))
        return indexIdentifierList

    def build_quantumgatecall(self, instruction):
        quantumGateName = Identifier(instruction[0].name)
        indexIdentifierList = self.build_indexIdentifierlist(instruction[1])
        expressionList = [Expression(param) for param in instruction[0].params]

        return QuantumGateCall(quantumGateName, indexIdentifierList, expressionList)

    def build_indexidentifier(self, bit: Bit):
        return IndexIdentifier2(Identifier(bit.register.name), [Integer(bit.index)])
