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

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit.test import QiskitTestCase
from qiskit.qasm3 import Exporter, dumps
from qiskit.qasm import pi


class TestQasm3Functions(QiskitTestCase):
    """QASM3 module - high level functions"""

    def setUp(self):
        self.circuit = QuantumCircuit(2)
        self.circuit.u(2 * pi, 3 * pi, -5 * pi, 0)
        self.expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "qubit[2] _q;",
                "let q = _q[0] || _q[1];",
                "U(2*pi, 3*pi, -5*pi) q[0];",
                "",
            ]
        )
        super().setUp()

    def test_dumps(self):
        """Test dumps."""
        result = dumps(self.circuit)
        self.assertEqual(result, self.expected_qasm)

    def test_dump(self):
        """Test dump into an IO stream."""
        circuit = QuantumCircuit(2)
        circuit.u(2 * pi, 3 * pi, -5 * pi, 0)
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "qubit[2] _q;",
                "let q = _q[0] || _q[1];",
                "U(2*pi, 3*pi, -5*pi) q[0];",
                "",
            ]
        )

        from io import StringIO

        io = StringIO()
        Exporter(circuit).dump(io)
        result = io.getvalue()
        self.assertEqual(result, expected_qasm)


class TestCircuitQasm3(QiskitTestCase):
    """QASM3 exporter."""

    def test_regs_conds_qasm(self):
        """Test with registers and conditionals."""
        qr1 = QuantumRegister(1, "qr1")
        qr2 = QuantumRegister(2, "qr2")
        cr = ClassicalRegister(3, "cr")
        qc = QuantumCircuit(qr1, qr2, cr)
        qc.measure(qr1[0], cr[0])
        qc.measure(qr2[0], cr[1])
        qc.measure(qr2[1], cr[2])
        qc.x(qr2[1]).c_if(cr, 0)
        qc.y(qr1[0]).c_if(cr, 1)
        qc.z(qr1[0]).c_if(cr, 2)
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "bit[3] cr;",
                "qubit[3] _q;",
                "let qr1 = _q[0];",
                "let qr2 = _q[1] || _q[2];",
                "cr[0] = measure qr1[0];",
                "cr[1] = measure qr2[0];",
                "cr[2] = measure qr2[1];",
                "if (cr == 0){",
                "x qr2[1];",
                "}",
                "if (cr == 1){",
                "y qr1[0];",
                "}",
                "if (cr == 2){",
                "z qr1[0];",
                "}",
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
                "qubit[2] _q;",
                "let qr = _q[0] || _q[1];",
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
                "qubit[2] _q;",
                "let qr = _q[0] || _q[1];",
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
                "qubit[2] _q;",
                "let qr = _q[0] || _q[1];",
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
                "qubit[1] _q;",
                "let qr = _q[0];",
                "my_gate qr[0];",
                f"my_gate_{my_gate_inst2_id} qr[0];",
                f"my_gate_{my_gate_inst3_id} qr[0];",
                "",
            ]
        )

        self.assertEqual(Exporter(circuit).dumps(), expected_qasm)

    def test_pi_disable_constants_false(self):
        """Test pi constant (disable_constants=False)"""
        circuit = QuantumCircuit(2)
        circuit.u(2 * pi, 3 * pi, -5 * pi, 0)
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "qubit[2] _q;",
                "let q = _q[0] || _q[1];",
                "U(2*pi, 3*pi, -5*pi) q[0];",
                "",
            ]
        )
        self.assertEqual(Exporter(circuit, disable_constants=False).dumps(), expected_qasm)

    def test_pi_disable_constants_true(self):
        """Test pi constant (disable_constants=True)"""
        circuit = QuantumCircuit(2)
        circuit.u(2 * pi, 3 * pi, -5 * pi, 0)
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "include stdgates.inc;",
                "qubit[2] _q;",
                "let q = _q[0] || _q[1];",
                "U(6.283185307179586, 9.42477796076938, -15.707963267948966) q[0];",
                "",
            ]
        )
        self.assertEqual(Exporter(circuit, disable_constants=True).dumps(), expected_qasm)

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
                "qubit[3] _q;",
                "let q = _q[0] || _q[1] || _q[2];",
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
                "rx(0.5) q_0;",
                "}",
                "qubit[1] _q;",
                "let q = _q[0];",
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
                "qubit[6] _q;",
                "let q = _q[0] || _q[1] || _q[2];",
                "let r = _q[3] || _q[4] || _q[5];",
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
                "qubit[1] _q;",
                "let q = _q[0];",
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
                "qubit[2] _q;",
                "let q = _q[0] || _q[1];",
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
                "qubit[2] _q;",
                "let q = _q[0] || _q[1];",
                f"cx_{custom_gate_id} q[0], q[1];",
                "",
            ]
        )
        self.assertEqual(Exporter(qc).dumps(), expected_qasm)

    def test_no_include(self):
        """Test explicit gate declaration (no include)"""
        qc = ClassicalRegister(2, name="qc")
        q = QuantumRegister(5, "q")
        circuit = QuantumCircuit(q, qc)
        circuit.rz(pi / 2, 0)
        circuit.sx(0)
        circuit.rz(pi / 2, 0)
        circuit.cx(0, 1)
        circuit.measure(q[0], qc[0])
        circuit.measure(q[1], qc[1])
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "gate cx c, t {ctrl @ U(pi, 0, pi) c, t}",
                "gate u3(param_0, param_1, param_2) q_0 {",
                "U(0, 0, pi/2) q_0;",
                "}",
                "gate u1(param_0) q_0 {",
                "u3(0, 0, pi/2) q_0;",
                "}",
                "gate rz(param_0) q_0 {",
                "u1(pi/2) q_0;",
                "}",
                "gate sdg q_0 {",
                "u1(-pi/2) q_0;",
                "}",
                "gate u2(param_0, param_1) q_0 {",
                "u3(pi/2, 0, pi) q_0;",
                "}",
                "gate h q_0 {",
                "u2(0, pi) q_0;",
                "}",
                "gate sx q_0 {",
                "sdg q_0;",
                "h q_0;",
                "sdg q_0;",
                "}",
                "bit[2] qc;",
                "qubit[5] _q;",
                "let q = _q[0] || _q[1] || _q[2] || _q[3] || _q[4];",
                "rz(pi/2) q[0];",
                "sx q[0];",
                "rz(pi/2) q[0];",
                "cx q[0], q[1];",
                "qc[0] = measure q[0];",
                "qc[1] = measure q[1];",
                "",
            ]
        )
        self.assertEqual(Exporter(circuit, includes=[]).dumps(), expected_qasm)

    def test_teleportation(self):
        """Teleportation with physical qubits"""
        qc = QuantumCircuit(3, 2)
        qc.h(1)
        qc.cx(1, 2)
        qc.barrier()
        qc.cx(0, 1)
        qc.h(0)
        qc.barrier()
        qc.measure([0, 1], [0, 1])
        qc.barrier()
        qc.x(2).c_if(qc.clbits[1], 1)
        qc.z(2).c_if(qc.clbits[0], 1)

        transpiled = transpile(qc, initial_layout=[0, 1, 2])
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "gate cx c, t {ctrl @ U(pi, 0, pi) c, t}",
                "gate u3(param_0, param_1, param_2) q_0 {",
                "U(pi/2, 0, pi) q_0;",
                "}",
                "gate u2(param_0, param_1) q_0 {",
                "u3(pi/2, 0, pi) q_0;",
                "}",
                "gate h q_0 {",
                "u2(0, pi) q_0;",
                "}",
                "gate x q_0 {",
                "u3(pi, 0, pi) q_0;",
                "}",
                "gate u1(param_0) q_0 {",
                "u3(0, 0, pi) q_0;",
                "}",
                "gate z q_0 {",
                "u1(pi) q_0;",
                "}",
                "bit[2] c;",
                "h $1;",
                "cx $1, $2;",
                "barrier $0, $1, $2;",
                "cx $0, $1;",
                "h $0;",
                "barrier $0, $1, $2;",
                "c[0] = measure $0;",
                "c[1] = measure $1;",
                "barrier $0, $1, $2;",
                "if (c[1] == 1){",
                "x $2;",
                "}",
                "if (c[0] == 1){",
                "z $2;",
                "}",
                "",
            ]
        )
        self.assertEqual(Exporter(transpiled, includes=[]).dumps(), expected_qasm)

    def test_basis_gates(self):
        """Teleportation with physical qubits"""
        qc = QuantumCircuit(3, 2)
        qc.h(1)
        qc.cx(1, 2)
        qc.barrier()
        qc.cx(0, 1)
        qc.h(0)
        qc.barrier()
        qc.measure([0, 1], [0, 1])
        qc.barrier()
        qc.x(2).c_if(qc.clbits[1], 1)
        qc.z(2).c_if(qc.clbits[0], 1)

        transpiled = transpile(qc, initial_layout=[0, 1, 2])
        expected_qasm = "\n".join(
            [
                "OPENQASM 3;",
                "gate u3(param_0, param_1, param_2) q_0 {",
                "U(pi/2, 0, pi) q_0;",
                "}",
                "gate u2(param_0, param_1) q_0 {",
                "u3(pi/2, 0, pi) q_0;",
                "}",
                "gate h q_0 {",
                "u2(0, pi) q_0;",
                "}",
                "gate x q_0 {",
                "u3(pi, 0, pi) q_0;",
                "}",
                "bit[2] c;",
                "h $1;",
                "cx $1, $2;",
                "barrier $0, $1, $2;",
                "cx $0, $1;",
                "h $0;",
                "barrier $0, $1, $2;",
                "c[0] = measure $0;",
                "c[1] = measure $1;",
                "barrier $0, $1, $2;",
                "if (c[1] == 1){",
                "x $2;",
                "}",
                "if (c[0] == 1){",
                "z $2;",
                "}",
                "",
            ]
        )
        self.assertEqual(
            Exporter(transpiled, includes=[], basis_gates=["cx", "z", "U"]).dumps(),
            expected_qasm,
        )
