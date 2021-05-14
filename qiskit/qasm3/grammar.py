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
        self.statements = statements

    def qasm_lines(self):
        ret = [self.header.qasm()]
        for statement in self.statements:
            ret.append(statement.qasm())
        return ret


class Header(Class):
    def __init__(self, version, includes):
        self.version = version
        self.includes = includes


class Include(Class):
    def __init__(self, filenames):
        """
        include
            : 'include' StringLiteral SEMICOLON
        """
        self.filenames = filenames


class Version(Class):
    def __init__(self, version_number):
        """
        version
            : 'OPENQASM'(Integer | RealNumber) SEMICOLON
        """
        self.version_number = version_number