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

"""Test QASM3 exporter."""

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.test import QiskitTestCase
from qiskit.qasm3 import Exporter
from qiskit.qasm import pi


class TestCircuitQasm3(QiskitTestCase):
    """QASM3 exporter."""

    def test_regs_conds_qasm(self):
        """Test with registers and conditionals."""
        qr1 = QuantumRegister(1, "qr1")
        qr2 = QuantumRegister(2, "qr2")
        cr = ClassicalRegister(3, "cr")
        qc = QuantumCircuit(qr1, qr2, cr)
        qc.p(0.3, qr1[0])
        qc.u(0.3, 0.2, 0.1, qr2[1])
        qc.s(qr2[1])
        qc.sdg(qr2[1])
        qc.cx(qr1[0], qr2[1])
        qc.barrier(qr2)
        qc.cx(qr2[1], qr1[0])
        qc.h(qr2[1])
        qc.x(qr2[1]).c_if(cr, 0)
        qc.y(qr1[0]).c_if(cr, 1)
        qc.z(qr1[0]).c_if(cr, 2)
        qc.barrier(qr1, qr2)
        qc.measure(qr1[0], cr[0])
        qc.measure(qr2[0], cr[1])
        qc.measure(qr2[1], cr[2])
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "bit[3] cr;",
                "qubit[1] qr1;",
                "qubit[2] qr2;",
                "p(0.3) qr1[0];",
                "U(0.3, 0.2, 0.1) qr2[1];",
                "s qr2[1];",
                "sdg qr2[1];",
                "cx qr1[0], qr2[1];",
                "barrier qr2[0], qr2[1];",
                "cx qr2[1], qr1[0];",
                "h qr2[1];",
                "if (cr == 0){",
                "x qr2[1];",
                "}",
                "if (cr == 1){",
                "y qr1[0];",
                "}",
                "if (cr == 2){",
                "z qr1[0];",
                "}",
                "barrier qr1[0], qr2[0], qr2[1];",
                "cr[0] = measure qr1[0];",
                "cr[1] = measure qr2[0];",
                "cr[2] = measure qr2[1];",
                "",
            ]
        )
        self.assertEqual(Exporter(qc).dumps(), expected_qasm)

    def test_composite_circuit(self):
        """Test with a composite circuit instruction and barriers"""
        composite_circ_qreg = QuantumRegister(2)
        composite_circ = QuantumCircuit(composite_circ_qreg, name="composite_circ")
        composite_circ.h(0)
        composite_circ.x(1)
        composite_circ.cx(0, 1)
        composite_circ_instr = composite_circ.to_instruction()

        qr = QuantumRegister(2, "qr")
        cr = ClassicalRegister(2, "cr")
        qc = QuantumCircuit(qr, cr)
        qc.h(0)
        qc.cx(0, 1)
        qc.barrier()
        qc.append(composite_circ_instr, [0, 1])
        qc.measure([0, 1], [0, 1])

        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "def composite_circ qubit q_0, qubit q_1 {",
                "h q_0;",
                "x q_1;",
                "cx q_0, q_1;",
                "return;",
                "}",
                "bit[2] cr;",
                "qubit[2] qr;",
                "h qr[0];",
                "cx qr[0], qr[1];",
                "barrier qr[0], qr[1];",
                "composite_circ qr[0], qr[1];",
                "cr[0] = measure qr[0];",
                "cr[1] = measure qr[1];",
                "",
            ]
        )
        self.assertEqual(Exporter(qc).dumps(), expected_qasm)

    def test_custom_gate(self):
        """Test custom gates (via to_gate)."""
        composite_circ_qreg = QuantumRegister(2)
        composite_circ = QuantumCircuit(composite_circ_qreg, name="composite_circ")
        composite_circ.h(0)
        composite_circ.x(1)
        composite_circ.cx(0, 1)
        composite_circ_instr = composite_circ.to_gate()

        qr = QuantumRegister(2, "qr")
        cr = ClassicalRegister(2, "cr")
        qc = QuantumCircuit(qr, cr)
        qc.h(0)
        qc.cx(0, 1)
        qc.barrier()
        qc.append(composite_circ_instr, [0, 1])
        qc.measure([0, 1], [0, 1])

        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "gate composite_circ q_0, q_1 {",
                "h q_0;",
                "x q_1;",
                "cx q_0, q_1;",
                "}",
                "bit[2] cr;",
                "qubit[2] qr;",
                "h qr[0];",
                "cx qr[0], qr[1];",
                "barrier qr[0], qr[1];",
                "composite_circ qr[0], qr[1];",
                "cr[0] = measure qr[0];",
                "cr[1] = measure qr[1];",
                "",
            ]
        )
        self.assertEqual(Exporter(qc).dumps(), expected_qasm)

    def test_same_composite_circuits(self):
        """Test when a composite circuit is added to the circuit multiple times."""
        composite_circ_qreg = QuantumRegister(2)
        composite_circ = QuantumCircuit(composite_circ_qreg, name="composite_circ")
        composite_circ.h(0)
        composite_circ.x(1)
        composite_circ.cx(0, 1)
        composite_circ_instr = composite_circ.to_instruction()

        qr = QuantumRegister(2, "qr")
        cr = ClassicalRegister(2, "cr")
        qc = QuantumCircuit(qr, cr)
        qc.h(0)
        qc.cx(0, 1)
        qc.barrier()
        qc.append(composite_circ_instr, [0, 1])
        qc.append(composite_circ_instr, [0, 1])
        qc.measure([0, 1], [0, 1])

        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "def composite_circ qubit q_0, qubit q_1 {",
                "h q_0;",
                "x q_1;",
                "cx q_0, q_1;",
                "return;",
                "}",
                "bit[2] cr;",
                "qubit[2] qr;",
                "h qr[0];",
                "cx qr[0], qr[1];",
                "barrier qr[0], qr[1];",
                "composite_circ qr[0], qr[1];",
                "composite_circ qr[0], qr[1];",
                "cr[0] = measure qr[0];",
                "cr[1] = measure qr[1];",
                "",
            ]
        )
        self.assertEqual(Exporter(qc).dumps(), expected_qasm)

    def test_composite_circuits_with_same_name(self):
        """Test when multiple composite circuit instructions same name and different implementation"""
        my_gate = QuantumCircuit(1, name="my_gate")
        my_gate.h(0)
        my_gate_inst1 = my_gate.to_instruction()

        my_gate = QuantumCircuit(1, name="my_gate")
        my_gate.x(0)
        my_gate_inst2 = my_gate.to_instruction()

        my_gate = QuantumCircuit(1, name="my_gate")
        my_gate.x(0)
        my_gate_inst3 = my_gate.to_instruction()

        qr = QuantumRegister(1, name="qr")
        circuit = QuantumCircuit(qr, name="circuit")
        circuit.append(my_gate_inst1, [qr[0]])
        circuit.append(my_gate_inst2, [qr[0]])
        my_gate_inst2_id = id(circuit.data[-1][0])
        circuit.append(my_gate_inst3, [qr[0]])
        my_gate_inst3_id = id(circuit.data[-1][0])
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "def my_gate qubit q_0 {",
                "h q_0;",
                "return;",
                "}",
                f"def my_gate_{my_gate_inst2_id} qubit q_0 {{",
                "x q_0;",
                "return;",
                "}",
                f"def my_gate_{my_gate_inst3_id} qubit q_0 {{",
                "x q_0;",
                "return;",
                "}",
                "qubit[1] qr;",
                "my_gate qr[0];",
                f"my_gate_{my_gate_inst2_id} qr[0];",
                f"my_gate_{my_gate_inst3_id} qr[0];",
                "",
            ]
        )

        self.assertEqual(Exporter(circuit).dumps(), expected_qasm)

    def test_pi(self):
        """Test pi constant."""
        circuit = QuantumCircuit(2)
        circuit.u(2 * pi, 3 * pi, -5 * pi, 0)
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "qubit[2] q;",
                "U(2*pi, 3*pi, -5*pi) q[0];",
                "",
            ]
        )
        self.assertEqual(Exporter(circuit).dumps(), expected_qasm)

    def test_from_qasm2_with_composite_circuit_with_one_param(self):
        """Test circuit from QASM2 with a parametrized custom gate."""
        qasm2 = "\n".join(
            [
                "OPENQASM 2.0;",
                'include "qelib1.inc";',
                "gate nG0(param0) q0 { h q0; }",
                "qreg q[3];",
                "creg c[3];",
                "nG0(pi) q[0];",
                "",
            ]
        )
        circuit = QuantumCircuit.from_qasm_str(qasm2)
        definition_qubit_name = circuit.data[0][0].definition.qregs[0].name
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                f"gate nG0(param_0) {definition_qubit_name}_0 {{",
                f"h {definition_qubit_name}_0;",
                "}",
                "bit[3] c;",
                "qubit[3] q;",
                "nG0(pi) q[0];",
                "",
            ]
        )
        self.assertEqual(Exporter(circuit).dumps(), expected_qasm)

    def test_from_qasm2_with_composite_circuit_with_three_param(self):
        """Test circuit from QASM2 with three parametrized custom gate."""
        parameter_a = Parameter("a")

        custom = QuantumCircuit(1)
        custom.rx(parameter_a, 0)
        custom_gate = custom.bind_parameters({parameter_a: 0.5}).to_gate()
        custom_gate.name = "custom"

        circuit = QuantumCircuit(1)
        circuit.append(custom_gate, [0])

        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "gate custom q_0 {",
                "rx(0.500000000000000) q_0;",
                "}",
                "qubit[1] q;",
                "custom q[0];",
                "",
            ]
        )
        self.assertEqual(Exporter(circuit).dumps(), expected_qasm)

    def test_from_qasm2_many_params_and_qubits(self):
        """Test circuit from QASM2 with many parameters and qubits."""

        qasm2 = "\n".join(
            [
                "OPENQASM 2.0;",
                'include "qelib1.inc";',
                "gate nG0(param0,param1) q0,q1 { h q0; h q1; }",
                "qreg q[3];",
                "qreg r[3];",
                "creg c[3];",
                "creg d[3];",
                "nG0(pi,pi/2) q[0],r[0];",
                "",
            ]
        )

        circuit = QuantumCircuit.from_qasm_str(qasm2)
        qubit_name = circuit.data[0][0].definition.qregs[0].name
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                f"gate nG0(param_0, param_1) {qubit_name}_0, {qubit_name}_1 {{",
                f"h {qubit_name}_0;",
                f"h {qubit_name}_1;",
                "}",
                "bit[3] c;",
                "bit[3] d;",
                "qubit[3] q;",
                "qubit[3] r;",
                "nG0(pi, pi/2) q[0], r[0];",
                "",
            ]
        )
        self.assertEqual(Exporter(circuit).dumps(), expected_qasm)

    def test_unbound_circuit(self):
        """Test with unbound parameters (turning them into inputs)."""
        qc = QuantumCircuit(1)
        theta = Parameter("θ")
        qc.rz(theta, 0)
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "input float[32] θ;",
                "qubit[1] q;",
                "rz(θ) q[0];",
                "",
            ]
        )
        self.assertEqual(Exporter(qc).dumps(), expected_qasm)

    def test_gate_qasm_with_ctrl_state(self):
        """Test with open controlled gate that has ctrl_state"""
        qc = QuantumCircuit(2)
        qc.ch(0, 1, ctrl_state=0)

        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "gate ch_o0 q_0, q_1 {",
                "x q_0;",
                "ch q_0, q_1;",
                "x q_0;",
                "}",
                "qubit[2] q;",
                "ch_o0 q[0], q[1];",
                "",
            ]
        )

        self.assertEqual(Exporter(qc).dumps(), expected_qasm)

    def test_custom_gate_collision_with_stdlib(self):
        """Test a custom gate with name collision with the standard library."""
        custom = QuantumCircuit(2, name="cx")
        custom.cx(0, 1)
        custom_gate = custom.to_gate()

        qc = QuantumCircuit(2)
        qc.append(custom_gate, [0, 1])
        custom_gate_id = id(qc.data[-1][0])
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                f"gate cx_{custom_gate_id} q_0, q_1 {{",
                "cx q_0, q_1;",
                "}",
                "qubit[2] q;",
                f"cx_{custom_gate_id} q[0], q[1];",
                "",
            ]
        )
        self.assertEqual(Exporter(qc).dumps(), expected_qasm)
