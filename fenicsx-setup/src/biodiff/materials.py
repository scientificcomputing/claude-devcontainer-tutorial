"""Tissue parameters for diffusion problems.

All values use millimetres and seconds (mm^2/s for diffusion coefficients,
1/s for reaction/clearance rates). The numbers are order-of-magnitude
estimates intended for tutorials and testing, not for clinical use.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tissue:
    """Material parameters of a tissue for a given solute.

    Parameters
    ----------
    name:
        Human readable name of the tissue.
    diffusion:
        Effective (apparent) diffusion coefficient in mm^2/s.
    clearance:
        First order clearance / decay rate in 1/s.
    """

    name: str
    diffusion: float
    clearance: float = 0.0

    def __post_init__(self) -> None:
        if self.diffusion <= 0:
            raise ValueError(f"Diffusion coefficient must be positive, got {self.diffusion}")
        if self.clearance < 0:
            raise ValueError(f"Clearance rate must be non-negative, got {self.clearance}")

    def diffusion_time(self, length: float) -> float:
        """Characteristic diffusion time scale L^2 / D (in seconds) for a length in mm."""
        return length**2 / self.diffusion


# Approximate values for the MRI contrast agent gadobutrol (~600 Da).
TISSUES: dict[str, Tissue] = {
    "free": Tissue("free", diffusion=3.8e-4),
    "gray_matter": Tissue("gray_matter", diffusion=1.2e-4),
    "white_matter": Tissue("white_matter", diffusion=1.2e-4),
    "csf": Tissue("csf", diffusion=3.8e-4),
}


def get_tissue(name: str) -> Tissue:
    """Look up a predefined tissue by name."""
    try:
        return TISSUES[name]
    except KeyError:
        raise KeyError(f"Unknown tissue '{name}'. Available: {sorted(TISSUES)}") from None
