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


class QuantumDeclaration(Class):
    def __init__(self, identifier, designator=None):
        """
        quantumDeclaration
            : 'qreg' Identifier designator? |  NOT SUPPORTED
             'qubit' designator? Identifier
        """
        self.identifier = identifier
        self.designator = designator


class Identifier(Class):
    def __init__(self, string):
        """
        Identifier : FirstIdCharacter GeneralIdCharacter* ;
        """
        self.string = string