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

class Class:
    pass


class Program(Class):
    def __init__(self, header, statements=None):
        self.header = header
        self.statements = statements or []

    def qasm(self):
        ret = self.header.qasm()
        for statement in self.statements:
            ret.append(statement.qasm())
        return ret


class Header(Class):
    def __init__(self, version, includes):
        self.version = version
        self.includes = includes

    def qasm(self):
        ret = self.version.qasm()
        for include in self.includes:
            ret.append(include.qasm())
        return ret


class Include(Class):
    def __init__(self, filenames):
        """
        include
            : 'include' StringLiteral SEMICOLON
        """
        self.filenames = filenames

    def qasm(self):
        return [f'include {filename};' for filename in self.filenames]


class Version(Class):
    def __init__(self, version_number):
        """
        version
            : 'OPENQASM'(Integer | RealNumber) SEMICOLON
        """
        self.version_number = version_number

    def qasm(self):
        return [f'OPENQASM {self.version_number};']


class QuantumInstruction(Class):
    def __init__(self):
        """
        quantumInstruction
            : quantumGateCall
            | quantumPhase
            | quantumMeasurement
            | quantumReset
            | quantumBarrier
        """
        pass

    def qasm(self):
        return ""

class Identifier(Class):
    def __init__(self, string):
        """
        Identifier : FirstIdCharacter GeneralIdCharacter* ;
        """
        self.string = string

    def qasm(self):
        return self.string

class IndexIdentifier(Identifier):
    """
    indexIdentifier
        : Identifier rangeDefinition
        | Identifier ( LBRACKET expressionList RBRACKET )?
        | indexIdentifier '||' indexIdentifier
    """
    pass


class Expression(Class):
    """
    expression
        // include terminator/unary as base cases to simplify parsing
        : expressionTerminator
        | unaryExpression
        // expression hierarchy
        | xOrExpression
        | expression '|' xOrExpression
    """

    def __init__(self, something):
        self.something = something  # TODO

    def qasm(self):
        return str(self.something)


class IndexIdentifier2(IndexIdentifier):
    """
    indexIdentifier
        : Identifier rangeDefinition
        | Identifier ( LBRACKET expressionList RBRACKET )? <--
        | indexIdentifier '||' indexIdentifier
    """
    def __init__(self, identifier:Identifier, expressionList:[Expression]):
        self.identifier = identifier
        self.expressionList = expressionList

    def qasm(self):
        return f"{self.identifier.qasm()}[{', '.join([i.qasm() for i in self.expressionList])}]"

class Integer(Expression):
    pass


class Designator(Class):
    def __init__(self, expression: Expression):
        """
        designator
            : LBRACKET expression RBRACKET
        """
        self.expression = expression

    def qasm(self):
        return f"[{self.expression.qasm()}]"

class QuantumDeclaration(Class):
    def __init__(self, identifier: Identifier, designator=None):
        """
        quantumDeclaration
            : 'qreg' Identifier designator? |  NOT SUPPORTED
             'qubit' designator? Identifier
        """
        self.identifier = identifier
        self.designator = designator

    def qasm(self):
        return f"qubit{self.designator.qasm()} {self.identifier.qasm()};"

class QuantumGateCall(Class):
    """
    quantumGateCall
        : quantumGateModifier* quantumGateName ( LPAREN expressionList? RPAREN )? indexIdentifierList
    """
    def __init__(self, quantumGateName: Identifier,
                 indexIdentifierList: [Identifier],
                 expressionList=None,
                 quantumGateModifier=None):
        self.quantumGateName = quantumGateName
        self.indexIdentifierList = indexIdentifierList
        self.expressionList = expressionList
        self.quantumGateModifier = quantumGateModifier

    def qasm(self):
        return f"{self.quantumGateName.qasm()} " \
               f"{', '.join([i.qasm() for i in self.indexIdentifierList])};"

class Skip(Class):
    def qasm(self):
        return ""
