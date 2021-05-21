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
from qiskit.circuit import Gate, Barrier, Measure
from qiskit.circuit.bit import Bit


class Exporter:
    def __init__(
        self,
        quantumcircuit,  # QuantumCircuit
        includes=None,  # list[filename:str]
    ):
        self.quantumcircuit = quantumcircuit
        self.includes = includes or []

    def requiered_includes(self):
        return []  # TODO

    def dump(self):
        tree = self.qasm_tree()
        return self.flatten_tree(tree)

    def flatten_tree(self, tree):
        ret = ''
        if isinstance(tree, str):
            return tree
        for child in tree:
            ret += self.flatten_tree(child)
        return ret

    def qasm_tree(self):
        return Qasm3Builder(self.quantumcircuit, self.includes).build_program().qasm()

class Qasm3Builder:
    def __init__(self, quantumcircuit, includeslist):
        self.quantumcircuit = quantumcircuit
        self.includeslist = includeslist
        self._instruction_in_scope = []
        self._gate_in_scope = []

    def _register_gate(self, gate):
        self._gate_in_scope.append(gate)

    def _register_instruction(self, instruction):
        self._instruction_in_scope.append(instruction)

    def build_header(self):
        version = Version('3')
        includes = self.build_includes()
        return Header(version, includes)

    def build_program(self):
        return Program(self.build_header(), self.build_globalstatements())

    def build_includes(self):
        # TODO
        return [Include(filename) for filename in self.includeslist]

    def build_globalstatements(self) -> [Statement]:
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
        defintions = self.build_definitions()

        ret = []
        if defintions:
            ret += defintions
        if bitdeclarations:
            ret += bitdeclarations
        if quantumdeclarations:
            ret += quantumdeclarations
        if quantuminstructions:
            ret += quantuminstructions
        return ret

    def build_definitions(self):
        ret = []
        while self._instruction_in_scope:
            instruction = self._instruction_in_scope.pop(0)
            ret.append(self.build_subroutinedefinition(instruction))
        while self._gate_in_scope:
            gate = self._gate_in_scope.pop(0) # TODO continue from here
            # ret.append(self.build_quantumgatedefinition(gate))
        return ret

    def build_subroutinedefinition(self, instruction):
        # TODO this is broken. The signature is of a subroutine is different
        quantumArgumentList = self.build_indexIdentifierlist(instruction.definition.qubits)
        subroutineBlock = SubroutineBlock(self.build_quantuminstructions(instruction.definition.data),
                                          ReturnStatement())
        return SubroutineDefinition(Identifier(instruction.name), subroutineBlock, quantumArgumentList)

    def build_quantumgatedefinition(self, gate):
        pass  # TODO (check if standard gate. what to do there?)

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
                self._register_gate(instruction[0])
                if instruction[0].condition:
                    eqcondition = self.build_eqcondition(instruction[0].condition)
                    instruciton_without_condition = instruction[0].copy()
                    instruciton_without_condition.condition = None
                    programTrue = self.build_programblock([(instruciton_without_condition,
                                                            instruction[1],
                                                            instruction[2])])
                    ret.append(BranchingStatement(eqcondition, programTrue))
                else:
                    ret.append(self.build_quantumgatecall(instruction))
            elif isinstance(instruction[0], Barrier):
                indexIdentifierList = self.build_indexIdentifierlist(instruction[1])
                ret.append(QuantumBarrier(indexIdentifierList))
            elif isinstance(instruction[0], Measure):
                quantumMeasurement = QuantumMeasurement(self.build_indexIdentifierlist(instruction[1]))
                indexIdentifierList = self.build_indexIdentifierlist(instruction[2])
                ret.append(QuantumMeasurementAssignment(indexIdentifierList, quantumMeasurement))
            else:
                self._register_instruction(instruction[0])
                ret.append(self.build_subroutinecall(instruction))
        return ret

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

    def build_subroutinecall(self, instruction):
        identifier = Identifier(instruction[0].name)
        expressionList = [Expression(param) for param in instruction[0].params]
        indexIdentifierList = self.build_indexIdentifierlist(instruction[1])

        return SubroutineCall(identifier, indexIdentifierList, expressionList)

    def build_indexidentifier(self, bit: Bit):
        return IndexIdentifier2(Identifier(bit.register.name), [Integer(bit.index)])
