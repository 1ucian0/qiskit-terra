# This code is part of Qiskit.
#
# (C) Copyright IBM 2023.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""TODO"""
from qiskit.circuit import ForLoopOp, ContinueLoopOp, BreakLoopOp
from qiskit.transpiler.basepasses import TransformationPass
from qiskit.transpiler.passes.utils import control_flow
from qiskit.converters import circuit_to_dag


class UnrollForLoops(TransformationPass):
    """TODO"""

    @control_flow.trivial_recurse
    def run(self, dag):
        """Run the UnrollForLoops pass on `dag`.

        Args:
            dag (DAGCircuit): the directed acyclic graph to run on.

        Returns:
            DAGCircuit: Transformed DAG.
        """
        for forloop_op in dag.op_nodes(ForLoopOp):
            (indexset, loop_parameter, body) = forloop_op.op.params

            # do not unroll when break_loop or continue_loop inside body
            if UnrollForLoops.body_contains(
                body,
                [ContinueLoopOp, BreakLoopOp],
            ):
                continue

            unrolled_dag = circuit_to_dag(body).copy_empty_like()
            for index_value in indexset:
                bound_body_dag = circuit_to_dag(body.bind_parameters({loop_parameter: index_value}))
                unrolled_dag.compose(bound_body_dag, inplace=True)
            dag.substitute_node_with_dag(forloop_op, unrolled_dag)

        return dag

    @classmethod
    def body_contains(cls, body, contains_types):
        """TODO"""
        for inst in body.data:
            operation = inst.operation
            for type_ in contains_types:
                if isinstance(operation, type_):
                    return True
                # TODO run body_contains in the bodies of if statements
        return False