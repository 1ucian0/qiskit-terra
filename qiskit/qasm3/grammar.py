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
    def qasm(self):
        raise NotImplementedError(self)


class Statement(Class):
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
        ret = [self.version.qasm()]
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
        return [f"include {filename};\n" for filename in self.filenames]


class Version(Class):
    def __init__(self, version_number):
        """
        version
            : 'OPENQASM'(Integer | RealNumber) SEMICOLON
        """
        self.version_number = version_number

    def qasm(self):
        return [f"OPENQASM {self.version_number};\n"]


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
        raise NotImplemented


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

    def __init__(self, identifier: Identifier, expressionList: [Expression]):
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


class BitDeclaration(Class):
    def __init__(self, identifier: Identifier, designator=None, equalsExpression=None):
        """
        bitDeclaration
            : ( 'creg' Identifier designator? |   # NOT SUPPORTED
                'bit' designator? Identifier ) equalsExpression?
        """
        self.identifier = identifier
        self.designator = designator
        self.equalsExpression = equalsExpression

    def qasm(self):
        return [f"bit{self.designator.qasm()} {self.identifier.qasm()};\n"]


class QuantumDeclaration(Class):
    def __init__(self, identifier: Identifier, designator=None):
        """
        quantumDeclaration
            : 'qreg' Identifier designator? |   # NOT SUPPORTED
             'qubit' designator? Identifier
        """
        self.identifier = identifier
        self.designator = designator

    def qasm(self):
        return [f"qubit{self.designator.qasm()} {self.identifier.qasm()};\n"]


class QuantumGateCall(QuantumInstruction):
    """
    quantumGateCall
        : quantumGateModifier* quantumGateName ( LPAREN expressionList? RPAREN )? indexIdentifierList
    """

    def __init__(
        self,
        quantumGateName: Identifier,
        indexIdentifierList: [Identifier],
        expressionList=[Expression],
        quantumGateModifier=None,
    ):
        self.quantumGateName = quantumGateName
        self.indexIdentifierList = indexIdentifierList
        self.expressionList = expressionList
        self.quantumGateModifier = quantumGateModifier

    def qasm(self):
        if self.expressionList:
            return (
                f"{self.quantumGateName.qasm()}"
                f"({', '.join([e.qasm() for e in self.expressionList])}) "
                f"{', '.join([i.qasm() for i in self.indexIdentifierList])};\n"
            )

        return (
            f"{self.quantumGateName.qasm()} "
            f"{', '.join([i.qasm() for i in self.indexIdentifierList])};\n"
        )


class QuantumBarrier(QuantumInstruction):
    """
    quantumBarrier
        : 'barrier' indexIdentifierList
    """

    def __init__(self, indexIdentifierList: [Identifier]):
        self.indexIdentifierList = indexIdentifierList

    def qasm(self):
        return [f'barrier {", ".join([i.qasm() for i in self.indexIdentifierList])};']


class BooleanExpression(Class):
    pass


class ProgramBlock(Class):
    """
    programBlock
        : statement | controlDirective
        | LBRACE(statement | controlDirective) * RBRACE
    """
    def __init__(self, statements: [Statement]):
        self.statements = statements

    def qasm(self):
        return ["{\n"] + [stmt.qasm() for stmt in self.statements] + ["}"]


class BooleanExpression(Class):
    """
    programBlock
        : statement | controlDirective
        | LBRACE(statement | controlDirective) * RBRACE
    """

    pass


class RelationalOperator(Class):
    pass


class LtOperator(RelationalOperator):
    def qasm(self):
        return ">"


class EqualsOperator(RelationalOperator):
    def qasm(self):
        return "=="


class GtOperator(RelationalOperator):
    def qasm(self):
        return "<"


class ComparisonExpression(BooleanExpression):
    """
    comparisonExpression
        : expression  // if (expression)
        | expression relationalOperator expression
    """

    def __init__(
        self, left: Expression, relation: RelationalOperator = None, right: Expression = None
    ):
        self.left = left
        self.relation = relation
        self.right = right

    def qasm(self):
        return f"{self.left.qasm()} {self.relation.qasm()} {self.right.qasm()}"

class BranchingStatement(Statement):
    """
    branchingStatement
        : 'if' LPAREN booleanExpression RPAREN programBlock ( 'else' programBlock )?
    """

    def __init__(
        self, booleanExpression: BooleanExpression, programTrue: ProgramBlock, programFalse=None
    ):
        self.booleanExpression = booleanExpression
        self.programTrue = programTrue
        self.programFalse = programFalse

    def qasm(self):
        ret = [f"if ({self.booleanExpression.qasm()})"] + self.programTrue.qasm()

        if self.programFalse:
            ret += ['else'] + self.programFalse.qasm()
        return ret

