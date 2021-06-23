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

"""TODO A pass for choosing a Layout of a circuit onto a Coupling graph, as a
Constraint Satisfaction Problem. It tries to find a solution that fully
satisfy the circuit, i.e. no further swap is needed. If no solution is
found, no ``property_set['layout']`` is set.
"""
import random
from retworkx import PyGraph, PyDiGraph, graph_vf2_mapping
from qiskit.transpiler.layout import Layout
from qiskit.transpiler.basepasses import AnalysisPass


class VF2Layout(AnalysisPass):
    """If possible, chooses a Layout as a Subgraph Isomorphism Probrem, using VF2."""

    def __init__(self, coupling_map, strict_direction=False, seed=None):
        """If possible, chooses a Layout as a Subgraph Isomorphism Probrem, using VF2.

        If not possible, does not set the layout property. In all the cases,
        the property `VF2Layout_stop_reason` will be added with one of the
        following values:

        * solution found: If a perfect layout was found.
        * nonexistent solution: If no perfect layout was found and every combination was checked.

        Args:
            coupling_map (Coupling): Directed graph representing a coupling map.
            strict_direction (bool): If True, considers the direction of the coupling map.
                                     Default is False.
            seed (int): Sets the seed of the PRNG. -1 Means no node shuffling.
        """
        super().__init__()
        self.coupling_map = coupling_map
        self.strict_direction = strict_direction
        self.seed = seed

    def run(self, dag):
        """run the layout method"""
        qubits = dag.qubits
        qubit_indices = {qubit: index for index, qubit in enumerate(qubits)}
        interactions = [(qubit_indices[gate.qargs[0]], qubit_indices[gate.qargs[1]]) for gate in dag.two_qubit_ops()]

        if self.strict_direction:
            cm_graph = self.coupling_map.graph
        else:
            cm_graph = self.coupling_map.graph.to_undirected()
            im_graph = PyGraph()
            vf2_mapping = graph_vf2_mapping

        cm_nodes = list(cm_graph.node_indexes())
        if self.seed != -1:
            random.Random(self.seed).shuffle(cm_nodes)
            shuffled_cm_graph = type(cm_graph)()
            shuffled_cm_graph.add_nodes_from(cm_nodes)
            new_edges = [(cm_nodes[edge[0]], cm_nodes[edge[1]]) for edge in cm_graph.edge_list()]
            shuffled_cm_graph.add_edges_from_no_data(new_edges)
            cm_nodes = {n: i for i, n in enumerate(cm_nodes)}
            cm_graph = shuffled_cm_graph

        im_graph.add_nodes_from(range(len(qubits)))
        im_graph.add_edges_from_no_data(interactions)

        mapping = vf2_mapping(cm_graph, im_graph, subgraph=True, id_order=True)

        if mapping:
            stop_reason = "solution found"
            layout = Layout({qubits[im_i]: cm_nodes[cm_i] for cm_i, im_i in mapping.items()})
            self.property_set["layout"] = layout
            for reg in dag.qregs.values():
                self.property_set["layout"].add_register(reg)
        else:
            stop_reason = "nonexistent solution"

        self.property_set["VF2Layout_stop_reason"] = stop_reason
