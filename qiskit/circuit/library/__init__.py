# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
===============================================
Circuit Library (:mod:`qiskit.circuit.library`)
===============================================

.. currentmodule:: qiskit.circuit.library

The circuit library is a collection of well studied circuits, directives, and gates that can be plugged
into many experiments allowing users to program at higher levels of abstraction when developing and
experimenting with circuits.


Any element of the circuit library can be attached to a circuit with the method
:meth:`.QuantumCircuit.append`. For example, to append a multi-controlled CNOT:

.. jupyter-execute::

    from qiskit.circuit.library import MCXGate
    gate = MCXGate(4)

    from qiskit import QuantumCircuit
    circuit = QuantumCircuit(5)
    circuit.append(gate, [0, 1, 4, 2, 3])
    circuit.draw('text')

The library is organized in several sections.

Standard gates
==============

These instructions are reversible unitary gates and they all subclass
:class:`~qiskit.circuit.gate.Gate`. As a consequence, they all have the methods
:meth:`~qiskit.circuit.gate.Gate.to_matrix`, :meth:`~qiskit.circuit.gate.Gate.power`,
and :meth:`~qiskit.circuit.gate.Gate.control`.

For example:

.. jupyter-execute::

    from qiskit.circuit.library import XGate
    gate = XGate()
    print(gate.to_matrix())             # X gate
    print(gate.power(1/2).to_matrix())  # √X gate
    print(gate.control(1).to_matrix())  # CX (controlled X) gate


.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   C3XGate
   C3SXGate
   C4XGate
   CCXGate
   DCXGate
   CHGate
   CPhaseGate
   CRXGate
   CRYGate
   CRZGate
   CSwapGate
   CSXGate
   CUGate
   CU1Gate
   CU3Gate
   CXGate
   CYGate
   CZGate
   HGate
   IGate
   MSGate
   PhaseGate
   RCCXGate
   RC3XGate
   RGate
   RXGate
   RXXGate
   RYGate
   RYYGate
   RZGate
   RZZGate
   RZXGate
   XXPlusYYGate
   ECRGate
   SGate
   SdgGate
   SwapGate
   iSwapGate
   SXGate
   SXdgGate
   TGate
   TdgGate
   UGate
   U1Gate
   U2Gate
   U3Gate
   XGate
   YGate
   ZGate

Standard Directives
===================

..
    This summary table deliberately does not generate toctree entries; these directives are "owned"
    by ``qiskit.circuit``.

Directives are instructions to the quantum stack that are not reversible. They are all interpreted
by the backend.

.. autosummary::

   ~qiskit.circuit.Barrier
   ~qiskit.circuit.Measure
   ~qiskit.circuit.Reset

Generalized Gates
=================

These "gates" (many are :class:`~qiskit.circuit.quantumcircuit.QuantumCircuit` subclasses) allow to
set the amount of qubits involved at instantiation time.


.. jupyter-execute::

    from qiskit.circuit.library import Diagonal

    diagonal = Diagonal([1, 1])
    print(diagonal.num_qubits)

    diagonal = Diagonal([1, 1, 1, 1])
    print(diagonal.num_qubits)


.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   Diagonal
   MCMT
   MCMTVChain
   Permutation
   GMS
   GR
   GRX
   GRY
   GRZ
   MCPhaseGate
   MCXGate
   MCXGrayCode
   MCXRecursive
   MCXVChain
   RVGate
   PauliGate
   LinearFunction

Boolean Logic Circuits
======================

These are :class:`~qiskit.circuit.quantumcircuit.QuantumCircuit` subclasses
that implement boolean logic operations.


.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   AND
   OR
   XOR
   InnerProduct

Basis Change Circuits
=====================

Basis change algorithms are :class:`~qiskit.circuit.library.blueprintcircuit.BlueprintCircuit` subclasses
that transform between bases. For example, in the case of the
Quantum Fourier Transform (QFT), it transforms between the computational basis and the Fourier basis.

.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   QFT

Arithmetic Circuits
===================

These :class:`~qiskit.circuit.quantumcircuit.QuantumCircuit`\\ s perform classical arithmetic,
such as addition or multiplication.

Amplitude Functions
-------------------

.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   LinearAmplitudeFunction

Functional Pauli Rotations
--------------------------

.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   FunctionalPauliRotations
   LinearPauliRotations
   PolynomialPauliRotations
   PiecewiseLinearPauliRotations
   PiecewisePolynomialPauliRotations
   PiecewiseChebyshev

Adders
------

.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   DraperQFTAdder
   CDKMRippleCarryAdder
   VBERippleCarryAdder
   WeightedAdder

Multipliers
-----------

.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   HRSCumulativeMultiplier
   RGQFTMultiplier

Comparators
-----------

.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   IntegerComparator

Functions on binary variables
-----------------------------

.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   QuadraticForm

Other arithmetic functions
--------------------------

.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   ExactReciprocal

Particular Quantum Circuits
===========================

.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   FourierChecking
   GraphState
   HiddenLinearFunction
   IQP
   QuantumVolume
   PhaseEstimation
   GroverOperator
   PhaseOracle
   EvolvedOperatorAnsatz
   PauliEvolutionGate


N-local circuits
================

These :class:`~qiskit.circuit.library.blueprintcircuit.BlueprintCircuit`
subclasses are used as initial guesses (a.k.a. ansatzes or variational forms) in chemistry.

.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   NLocal
   TwoLocal
   PauliTwoDesign
   RealAmplitudes
   EfficientSU2
   ExcitationPreserving
   QAOAAnsatz


Data encoding circuits
======================

These :class:`~qiskit.circuit.library.blueprintcircuit.BlueprintCircuit`
subclasses are used for classification and data encoding circuits (a.k.a. feature maps).

.. autosummary::
   :toctree: ../stubs/
   :template: autosummary/class_no_inherited_members.rst

   PauliFeatureMap
   ZFeatureMap
   ZZFeatureMap

Template circuits
=================

Templates are functions that return circuits that compute the identity. They are used at
circuit optimization where matching part of the template allows the compiler
to replace the match with the inverse of the remainder from the template.

In this example, the identity constant in a template is checked:

.. jupyter-execute::

    from qiskit.circuit.library.templates import template_nct_4b_1
    from qiskit.quantum_info import Operator
    import numpy as np

    template = template_nct_4b_1()

    identity = np.identity(2 ** len(template.qubits), dtype=complex)
    data = Operator(template).data
    np.allclose(data, identity)  # True, template_nct_4b_1 is the identity

NCT (Not-CNOT-Toffoli) template circuits
----------------------------------------

Template circuits for :class:`~qiskit.circuit.library.standard_gates.x.XGate`,
:class:`~qiskit.circuit.library.standard_gates.x.CXGate`,
and :class:`~qiskit.circuit.library.standard_gates.x.CCXGate` (Toffoli) gates.

**Reference:**
Maslov, D. and Dueck, G. W. and Miller, D. M.,
Techniques for the synthesis of reversible Toffoli networks, 2007
http://dx.doi.org/10.1145/1278349.1278355

.. autosummary::
   :toctree: ../stubs/

   templates.nct.template_nct_2a_1
   templates.nct.template_nct_2a_2
   templates.nct.template_nct_2a_3
   templates.nct.template_nct_4a_1
   templates.nct.template_nct_4a_2
   templates.nct.template_nct_4a_3
   templates.nct.template_nct_4b_1
   templates.nct.template_nct_4b_2
   templates.nct.template_nct_5a_1
   templates.nct.template_nct_5a_2
   templates.nct.template_nct_5a_3
   templates.nct.template_nct_5a_4
   templates.nct.template_nct_6a_1
   templates.nct.template_nct_6a_2
   templates.nct.template_nct_6a_3
   templates.nct.template_nct_6a_4
   templates.nct.template_nct_6b_1
   templates.nct.template_nct_6b_2
   templates.nct.template_nct_6c_1
   templates.nct.template_nct_7a_1
   templates.nct.template_nct_7b_1
   templates.nct.template_nct_7c_1
   templates.nct.template_nct_7d_1
   templates.nct.template_nct_7e_1
   templates.nct.template_nct_9a_1
   templates.nct.template_nct_9c_1
   templates.nct.template_nct_9c_2
   templates.nct.template_nct_9c_3
   templates.nct.template_nct_9c_4
   templates.nct.template_nct_9c_5
   templates.nct.template_nct_9c_6
   templates.nct.template_nct_9c_7
   templates.nct.template_nct_9c_8
   templates.nct.template_nct_9c_9
   templates.nct.template_nct_9c_10
   templates.nct.template_nct_9c_11
   templates.nct.template_nct_9c_12
   templates.nct.template_nct_9d_1
   templates.nct.template_nct_9d_2
   templates.nct.template_nct_9d_3
   templates.nct.template_nct_9d_4
   templates.nct.template_nct_9d_5
   templates.nct.template_nct_9d_6
   templates.nct.template_nct_9d_7
   templates.nct.template_nct_9d_8
   templates.nct.template_nct_9d_9
   templates.nct.template_nct_9d_10

Clifford template circuits
--------------------------

Template circuits over Clifford gates.

.. autosummary::
   :toctree: ../stubs/

   clifford_2_1
   clifford_2_2
   clifford_2_3
   clifford_2_4
   clifford_3_1
   clifford_4_1
   clifford_4_2
   clifford_4_3
   clifford_4_4
   clifford_5_1
   clifford_6_1
   clifford_6_2
   clifford_6_3
   clifford_6_4
   clifford_6_5
   clifford_8_1
   clifford_8_2
   clifford_8_3

RZXGate template circuits
-------------------------

Template circuits with :class:`~qiskit.circuit.library.RZXGate`.

.. autosummary::
   :toctree: ../stubs/

   rzx_yz
   rzx_xz
   rzx_cy
   rzx_zz1
   rzx_zz2
   rzx_zz3

"""

from .standard_gates import *
from .templates import *
from ..barrier import Barrier
from ..measure import Measure
from ..reset import Reset


from .blueprintcircuit import BlueprintCircuit
from .generalized_gates import (
    Diagonal,
    MCMT,
    MCMTVChain,
    Permutation,
    GMS,
    MSGate,
    GR,
    GRX,
    GRY,
    GRZ,
    RVGate,
    PauliGate,
    LinearFunction,
)
from .pauli_evolution import PauliEvolutionGate
from .boolean_logic import (
    AND,
    OR,
    XOR,
    InnerProduct,
)
from .basis_change import QFT
from .arithmetic import (
    FunctionalPauliRotations,
    LinearPauliRotations,
    PiecewiseLinearPauliRotations,
    PiecewisePolynomialPauliRotations,
    PolynomialPauliRotations,
    IntegerComparator,
    WeightedAdder,
    QuadraticForm,
    LinearAmplitudeFunction,
    VBERippleCarryAdder,
    CDKMRippleCarryAdder,
    DraperQFTAdder,
    PiecewiseChebyshev,
    HRSCumulativeMultiplier,
    RGQFTMultiplier,
    ExactReciprocal,
)

from .n_local import (
    NLocal,
    TwoLocal,
    PauliTwoDesign,
    RealAmplitudes,
    EfficientSU2,
    ExcitationPreserving,
    QAOAAnsatz,
)
from .data_preparation import PauliFeatureMap, ZFeatureMap, ZZFeatureMap
from .quantum_volume import QuantumVolume
from .fourier_checking import FourierChecking
from .graph_state import GraphState
from .hidden_linear_function import HiddenLinearFunction
from .iqp import IQP
from .phase_estimation import PhaseEstimation
from .grover_operator import GroverOperator
from .phase_oracle import PhaseOracle
from .evolved_operator_ansatz import EvolvedOperatorAnsatz
