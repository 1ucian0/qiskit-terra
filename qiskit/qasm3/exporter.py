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
from qiskit.circuit import Gate, Barrier, Measure, QuantumRegister
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
    builtins = (Barrier, Measure)

    def __init__(self, quantumcircuit, includeslist):
        self.quantumcircuit = quantumcircuit
        self.includeslist = includeslist
        self._gate_in_scope = {}
        self._subroutine_in_scope = {}
        self._kernel_in_scope = {}
        self._flat_reg = False

    def _register_gate(self, gate):
        self._gate_in_scope[id(gate)] = gate

    def _register_subroutine(self, instruction):
        self._subroutine_in_scope[id(instruction)] = instruction

    def _register_kernel(self, instruction):
        self._kernel_in_scope[instruction.name] = instruction

    def build_header(self):
        version = Version('3')
        includes = self.build_includes()
        return Header(version, includes)

    def build_program(self):
        self.hoist_subroutines_and_gates(self.quantumcircuit.data)
        return Program(self.build_header(), self.build_globalstatements())

    def hoist_subroutines_and_gates(self, instructions):
        for instruction in instructions:
            if instruction[0].definition is None:
                self._register_kernel(instruction[0])
            else:
                if isinstance(instruction[0], Gate):
                    self._register_gate(instruction[0])
                else:
                    self._register_subroutine(instruction[0])
                self.hoist_subroutines_and_gates(instruction[0].definition.data)

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
        definitions = self.build_definitions()
        bitdeclarations = self.build_bitdeclarations()
        quantumdeclarations = self.build_quantumdeclarations()
        quantuminstructions = self.build_quantuminstructions(self.quantumcircuit.data)

        ret = []
        if definitions:
            ret += definitions
        if bitdeclarations:
            ret += bitdeclarations
        if quantumdeclarations:
            ret += quantumdeclarations
        if quantuminstructions:
            ret += quantuminstructions
        return ret

    def build_definitions(self):
        ret = []
        for instruction in self._subroutine_in_scope.values():
            if isinstance(instruction, self.builtins):
                continue
            ret.append(self.build_definition(instruction, self.build_subroutinedefinition))
        for instruction in self._gate_in_scope.values():
            # TODO if gate in standard library, this should be dynamic and similar to self.builtins
            if instruction.name in ['U', 'h', 'u1', 'u2', 'u3', 'x', 'p', 's', 'sdg', 'y', 'z']:
                continue
            ret.append(self.build_definition(instruction, self.build_quantumgatedefinition))
        return ret

    def build_definition(self, instruction, builder):
        same_names = [i for i in self._subroutine_in_scope.values()
                      if i.name == instruction.name]
        if len(same_names) > 1:
            subroutine_name = f"{instruction.name}_{id(instruction)}"
        else:
            subroutine_name = instruction.name
        self._flat_reg = True
        definition = builder(instruction, subroutine_name)
        self._flat_reg = False
        return definition

    def build_subroutinedefinition(self, instruction, name=None):
        if name is None:
            name = instruction.name
        quantumArgumentList = self.build_quantumArgumentList(instruction.definition.qregs)
        subroutineBlock = SubroutineBlock(self.build_quantuminstructions(
            instruction.definition.data), ReturnStatement())
        return SubroutineDefinition(Identifier(name), subroutineBlock, quantumArgumentList)

    def build_quantumgatedefinition(self, gate, name=None):
        if name is None:
            name = gate.name
        quantumGateSignature = self.build_quantumGateSignature(gate.definition.qregs, name)
        quantumBlock = QuantumBlock(self.build_quantuminstructions(gate.definition.data))
        return QuantumGateDefinition(quantumGateSignature, quantumBlock)

    def build_quantumGateSignature(self, qregs: [QuantumRegister], name):
        identifierList = []
        for qreg in qregs:
            for qubit in qreg:
                qubit_name = f"{qreg.name}_{qubit.index}"
                identifierList.append(Identifier(qubit_name))

        return QuantumGateSignature(Identifier(name), identifierList)

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
                indexIdentifierList = self.build_indexidentifier(instruction[2][0])
                ret.append(QuantumMeasurementAssignment(indexIdentifierList, quantumMeasurement))
            else:
                ret.append(self.build_subroutinecall(instruction))
        return ret

    def build_programblock(self, instructions):
        return ProgramBlock(self.build_quantuminstructions(instructions))

    def build_eqcondition(self, condition):
        """Classical Conditional condition from a instruction.condition"""
        return ComparisonExpression(Identifier(condition[0].name),
                                     EqualsOperator(),
                                     Integer(condition[1]))

    def build_quantumArgumentList(self, qregs: [QuantumRegister]):
        quantumArgumentList = []
        for qreg in qregs:
            if self._flat_reg:
                for qubit in qreg:
                    qubit_name = f"{qreg.name}_{qubit.index}"
                    quantumArgumentList.append(QuantumArgument(Identifier(qubit_name)))
            else:
                quantumArgumentList.append(QuantumArgument(Identifier(qreg.name),
                                                              Designator(Integer(qreg.size))))
        return quantumArgumentList

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
        if self._flat_reg:
            bit_name = f"{bit.register.name}_{bit.index}"
            return IndexIdentifier2(Identifier(bit_name))
        else:
            return IndexIdentifier2(Identifier(bit.register.name), [Integer(bit.index)])
