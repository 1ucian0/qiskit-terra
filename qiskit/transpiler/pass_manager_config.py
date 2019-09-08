# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Models for PassManagerConfig and its related components."""

from qiskit.transpiler.models import PassManagerConfigSchema
from qiskit.validation import BaseModel, bind_schema


@bind_schema(PassManagerConfigSchema)
class PassManagerConfig(BaseModel):
    """Model for PassManagerConfig.

    Please note that this class only describes the required fields. For the
    full description of the model, please check ``PassManagerConfigSchema``.

    Attributes:
        optimization_level (int): a non-negative integer indicating the
            optimization level. 0 means no transformation on the circuit. Higher
            levels may produce more optimized circuits, but may take longer.
    """

    def __init__(self,
                 initial_layout=None,
                 basis_gates=None,
                 coupling_map=None,
                 backend_properties=None,
                 seed_transpiler=None,
                 callback=None):
        super().__init__(initial_layout=initial_layout,
                         basis_gates=basis_gates,
                         coupling_map=coupling_map,
                         backend_properties=backend_properties,
                         seed_transpiler=seed_transpiler,
                         callback=callback)
