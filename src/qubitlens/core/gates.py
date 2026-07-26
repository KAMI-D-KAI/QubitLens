"""Common single-qubit gate matrices used by QubitLens."""

import numpy as np
from numpy.typing import NDArray


ComplexMatrix = NDArray[np.complex128]


I: ComplexMatrix = np.array(
    [
        [1, 0],
        [0, 1],
    ],
    dtype=np.complex128,
)

X: ComplexMatrix = np.array(
    [
        [0, 1],
        [1, 0],
    ],
    dtype=np.complex128,
)

Y: ComplexMatrix = np.array(
    [
        [0, -1j],
        [1j, 0],
    ],
    dtype=np.complex128,
)

Z: ComplexMatrix = np.array(
    [
        [1, 0],
        [0, -1],
    ],
    dtype=np.complex128,
)

H: ComplexMatrix = (1 / np.sqrt(2)) * np.array(
    [
        [1, 1],
        [1, -1],
    ],
    dtype=np.complex128,
)

S: ComplexMatrix = np.array(
    [
        [1, 0],
        [0, 1j],
    ],
    dtype=np.complex128,
)

T: ComplexMatrix = np.array(
    [
        [1, 0],
        [0, np.exp(1j * np.pi / 4)],
    ],
    dtype=np.complex128,
)