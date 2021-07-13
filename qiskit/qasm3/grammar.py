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

# pylint: disable=invalid-name, abstract-method, super-init-not-called

"""QASM3 AST Nodes"""


class Class:
    """Base abstract class for AST notes"""

    def qasm(self):
        """Unparses the node"""
        raise NotImplementedError(self)


class Statement(Class):
    """
    statement
        : expressionStatement
        | assignmentStatement
        | classicalDeclarationStatement
        | branchingStatement
        | loopStatement
        | endStatement
        | aliasStatement
        | quantumStatement
    """

    pass


class Pragma(Class):
    """
    pragma
        : '#pragma' LBRACE statement* RBRACE  // match any valid openqasm statement
    """

    def __init__(self, content):
        self.content = content

    def qasm(self):
        return [f"#pragma {self.content};\n"]


class CalibrationGrammarDeclaration(Statement):
    """
    calibrationGrammarDeclaration
        : 'defcalgrammar' calibrationGrammar SEMICOLON
    """

    def __init__(self, name):
        self.name = name

    def qasm(self):
        return [f"defcalgrammar {self.name.qasm()};\n"]


class Program(Class):
    """
    program
        : header (globalStatement | statement)*
    """

    def __init__(self, header, statements=None):
        self.header = header
        self.statements = statements or []

    def qasm(self):
        ret = self.header.qasm()
        for statement in self.statements:
            if isinstance(statement, str):
                ret.append(statement)
            else:
                ret.append(statement.qasm())
        return ret


class Header(Class):
    """
    header
        : version? include*
    """

    def __init__(self, version, includes):
        self.version = version
        self.includes = includes

    def qasm(self):
        ret = [self.version.qasm()]
        for include in self.includes:
            ret.append(include.qasm())
        return ret


class Include(Class):
    """
    include
        : 'include' StringLiteral SEMICOLON
    """

    def __init__(self, filename):
        self.filename = filename

    def qasm(self):
        return [f"include {self.filename};\n"]


class Version(Class):
    """
    version
        : 'OPENQASM'(Integer | RealNumber) SEMICOLON
    """

    def __init__(self, version_number):
        self.version_number = version_number

    def qasm(self):
        return [f"OPENQASM {self.version_number};\n"]


class QuantumInstruction(Class):
    """
    quantumInstruction
        : quantumGateCall
        | quantumPhase
        | quantumMeasurement
        | quantumReset
        | quantumBarrier
    """

    def __init__(self):
        pass

    def qasm(self):
        raise NotImplementedError


class Identifier(Class):
    """
    Identifier : FirstIdCharacter GeneralIdCharacter* ;
    """

    def __init__(self, string):
        self.string = string

    def qasm(self):
        return self.string


class PhysicalQubitIdentifier(Identifier):
    """
    TOOD
    """

    def __init__(self, identifier: Identifier):
        self.identifier = identifier

    def qasm(self):
        return f"${self.identifier.qasm()}"


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

    def __init__(self, identifier: Identifier, expressionList: [Expression] = None):
        self.identifier = identifier
        self.expressionList = expressionList

    def qasm(self):
        if self.expressionList:
            return f"{self.identifier.qasm()}[{', '.join([i.qasm() for i in self.expressionList])}]"
        else:
            return f"{self.identifier.qasm()}"


class QuantumMeasurement(Class):
    """
    quantumMeasurement
        : 'measure' indexIdentifierList
    """

    def __init__(self, indexIdentifierList: [Identifier]):
        self.indexIdentifierList = indexIdentifierList

    def qasm(self):
        return f"measure {', '.join([i.qasm() for i in self.indexIdentifierList])};\n"


class QuantumMeasurementAssignment(Statement):
    """
    quantumMeasurementAssignment
        : quantumMeasurement ARROW indexIdentifierList
        | indexIdentifier EQUALS quantumMeasurement  # eg: bits = measure qubits;
    """

    def __init__(self, indexIdentifier: IndexIdentifier2, quantumMeasurement: QuantumMeasurement):
        self.indexIdentifier = indexIdentifier
        self.quantumMeasurement = quantumMeasurement

    def qasm(self):
        return [f"{self.indexIdentifier.qasm()} = {self.quantumMeasurement.qasm()}"]


class ExpressionTerminator(Expression):
    """
    expressionTerminator
        : Constant
        | Integer
        | RealNumber
        | booleanLiteral
        | Identifier
        | StringLiteral
        | builtInCall
        | kernelCall
        | subroutineCall
        | timingTerminator
        | LPAREN expression RPAREN
        | expressionTerminator LBRACKET expression RBRACKET
        | expressionTerminator incrementor
    """

    pass


class Integer(Expression):
    """Integer : Digit+ ;"""

    pass


class Designator(Class):
    """
    designator
        : LBRACKET expression RBRACKET
    """

    def __init__(self, expression: Expression):
        self.expression = expression

    def qasm(self):
        return f"[{self.expression.qasm()}]"


class BitDeclaration(Class):
    """
    bitDeclaration
        : ( 'creg' Identifier designator? |   # NOT SUPPORTED
            'bit' designator? Identifier ) equalsExpression?
    """

    def __init__(self, identifier: Identifier, designator=None, equalsExpression=None):
        self.identifier = identifier
        self.designator = designator
        self.equalsExpression = equalsExpression

    def qasm(self):
        return [f"bit{self.designator.qasm()} {self.identifier.qasm()};\n"]


class QuantumDeclaration(Class):
    """
    quantumDeclaration
        : 'qreg' Identifier designator? |   # NOT SUPPORTED
         'qubit' designator? Identifier
    """

    def __init__(self, identifier: Identifier, designator=None):
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
        expressionList: [Expression] = None,
        quantumGateModifier=None,
    ):
        self.quantumGateName = quantumGateName
        self.indexIdentifierList = indexIdentifierList
        self.expressionList = expressionList
        self.quantumGateModifier = quantumGateModifier

    def qasm(self):
        name = self.quantumGateName.qasm()
        if self.expressionList:
            return (
                f"{name}"
                f"({', '.join([e.qasm() for e in self.expressionList])}) "
                f"{', '.join([i.qasm() for i in self.indexIdentifierList])};\n"
            )

        return f"{name} " f"{', '.join([i.qasm() for i in self.indexIdentifierList])};\n"


class SubroutineCall(ExpressionTerminator):
    """
    subroutineCall
        : Identifier ( LPAREN expressionList? RPAREN )? indexIdentifierList
    """

    def __init__(
        self,
        identifier: Identifier,
        indexIdentifierList: [Identifier],
        expressionList: [Expression] = None,
    ):
        self.identifier = identifier
        self.indexIdentifierList = indexIdentifierList
        self.expressionList = expressionList or []

    def qasm(self):
        if self.expressionList:
            return (
                f"{self.identifier.qasm()} "
                f"({', '.join([e.qasm() for e in self.expressionList])}) "
                f"{', '.join([i.qasm() for i in self.indexIdentifierList])};\n"
            )

        return (
            f"{self.identifier.qasm()} "
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
        return [f'barrier {", ".join([i.qasm() for i in self.indexIdentifierList])};\n']


class ProgramBlock(Class):
    """
    programBlock
        : statement | controlDirective
        | LBRACE(statement | controlDirective) * RBRACE
    """

    def __init__(self, statements: [Statement]):
        self.statements = statements

    def qasm(self):
        return ["{\n"] + [stmt.qasm() for stmt in self.statements] + ["}\n"]


class ReturnStatement(Class):  # TODO probably should be a subclass of ControlDirective
    """
    returnStatement
        : 'return' ( expression | quantumMeasurement )? SEMICOLON;
    """

    def __init__(self, expression=None):
        self.expression = expression

    def qasm(self):
        if self.expression:
            return [f"return {self.expression.qasm()};\n"]
        return ["return;\n"]


class QuantumBlock(ProgramBlock):
    """
    quantumBlock
        : LBRACE ( quantumStatement | quantumLoop )* RBRACE
    """

    pass


class SubroutineBlock(ProgramBlock):
    """
    subroutineBlock
        : LBRACE statement* returnStatement? RBRACE
    """

    def __init__(self, statements: [Statement], returnStatement: ReturnStatement = None):
        super().__init__(statements + [returnStatement])


class QuantumArgument(QuantumDeclaration):
    """
    quantumArgument
        : 'qreg' Identifier designator? | 'qubit' designator? Identifier
    """

    def qasm(self):
        if self.designator:
            return f"qubit{self.designator.qasm()} {self.identifier.qasm()}"
        else:
            return f"qubit {self.identifier.qasm()}"


class QuantumGateSignature(Class):
    """
    quantumGateSignature
        : quantumGateName ( LPAREN identifierList? RPAREN )? identifierList
    """

    def __init__(self, name: Identifier, qargList: [Identifier], params: [Identifier] = None):
        self.name = name
        self.qargList = qargList
        self.params = params

    def qasm(self):
        qargList = ", ".join([i.qasm() for i in self.qargList])
        name = self.name.qasm()
        if self.params:
            params = ", ".join([i.qasm() for i in self.params])
            return f"{name}({params}) {qargList}"
        return f"{name} {qargList}"


class QuantumGateDefinition(Statement):
    """
    quantumGateDefinition
        : 'gate' quantumGateSignature quantumBlock
    """

    def __init__(self, quantumGateSignature: QuantumGateSignature, quantumBlock: QuantumBlock):
        self.quantumGateSignature = quantumGateSignature
        self.quantumBlock = quantumBlock

    def qasm(self):
        return [f"gate {self.quantumGateSignature.qasm()} "] + self.quantumBlock.qasm()


class SubroutineDefinition(Statement):
    """
    subroutineDefinition
        : 'def' Identifier ( LPAREN classicalArgumentList? RPAREN )? quantumArgumentList?
        returnSignature? subroutineBlock
    """

    def __init__(
        self,
        identifier: Identifier,
        subroutineBlock: SubroutineBlock,
        quantumArgumentList: [QuantumArgument] = None,
        classicalArgumentList=None,  # [ClassicalArgument]
    ):
        self.identifier = identifier
        self.subroutineBlock = subroutineBlock
        self.quantumArgumentList = quantumArgumentList or []
        self.classicalArgumentList = classicalArgumentList or []

    def qasm(self):
        if self.quantumArgumentList:
            return [
                f"def {self.identifier.qasm()} "
                f"{', '.join([i.qasm() for i in self.quantumArgumentList])} "
            ] + self.subroutineBlock.qasm()
        return [f"def {self.identifier.qasm()} "] + self.subroutineBlock.qasm()


class CalibrationArgument(Class):
    """
    calibrationArgumentList
        : classicalArgumentList | expressionList
    """

    pass


class CalibrationDefinition(Statement):
    """
    calibrationDefinition
        : 'defcal' Identifier
        ( LPAREN calibrationArgumentList? RPAREN )? identifierList
        returnSignature? LBRACE .*? RBRACE  // for now, match anything inside body
        ;
    """

    def __init__(
        self,
        name: Identifier,
        identifierList: [Identifier],
        calibrationArgumentList: [CalibrationArgument] = None,
        block: SubroutineBlock = None,
    ):
        self.name = name
        self.identifierList = identifierList
        self.calibrationArgumentList = calibrationArgumentList or []
        self.block = block or []

    def qasm(self):
        name = self.name.qasm()
        identifierList = f"{', '.join([i.qasm() for i in self.identifierList])} "
        calibrationArgumentList = (
            f"{', '.join([i.qasm() for i in self.calibrationArgumentList])} "
            if self.calibrationArgumentList
            else ""
        )
        block = self.block.qasm() if self.block else ["{}"]

        return [f"defcal {name} {identifierList}{calibrationArgumentList}"] + block + ["\n"]


class BooleanExpression(Class):
    """
    programBlock
        : statement | controlDirective
        | LBRACE(statement | controlDirective) * RBRACE
    """

    def qasm(self):
        pass


class RelationalOperator(Class):
    """Relational operator"""

    def qasm(self):
        raise NotImplementedError


class LtOperator(RelationalOperator):
    """Less than relational operator"""

    def qasm(self):
        return ">"


class EqualsOperator(RelationalOperator):
    """Greater than relational operator"""

    def qasm(self):
        return "=="


class GtOperator(RelationalOperator):
    """Greater than relational operator"""

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
            ret += ["else"] + self.programFalse.qasm()
        return ret


class Input(Class):
    """UNDEFINED in the grammar yet"""

    def __init__(self, input_type, input_variable):
        self.type = input_type
        self.variable = input_variable

    def qasm(self):
        return [f"input {self.type.qasm()} {self.variable.qasm()};\n"]
