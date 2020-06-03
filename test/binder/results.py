# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import os

CWD = os.path.dirname(os.path.abspath(__file__))


class Results:
    def __init__(self, namelist):
        self.namelist = namelist

    def _repr_html_(self):
        ret = "<table>"
        ret += '<tr><td>Filename</td><td>Result</td><td>Reference</td></tr>'
        for name in self.namelist:
            ret += '<tr>'
            ret += '<td>' + name + '</td>'
            ret += '<td><img src="' + name + '"</td>'
            reference = os.path.join('mpl', 'references', name)
            if os.path.exists(os.path.join(CWD, reference)):
                ret += '<td><img src="' + reference + '"</td>'
            else:
                ret += '<td style="text-align:center">' \
                       'Add <a download="%s" href="%s">this image</a> ' \
                       'to %s and push</td>' % (name, reference, reference)
            ret += '</tr>'
        ret += "</table>"
        return ret


namelist = []
for file in os.listdir(CWD):
    if file.endswith(".png"):
        namelist.append(file)
results = Results(namelist)
