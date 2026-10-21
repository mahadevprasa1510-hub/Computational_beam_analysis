
import math
import numpy as np


def _validate_number(name, value, positive=False, nonnegative=False):
    """Validate one numerical engineering input."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric.")

    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite.")

    if positive and value <= 0:
        raise ValueError(f"{name} must be greater than zero.")

    if nonnegative and value < 0:
        raise ValueError(f"{name} cannot be negative.")
    return value


def solve_simply_supported_beam(
    length,
    youngs_modulus,
    moment_of_inertia,
    load_type,
    load_magnitude,
    load_position=None,
    num_points=501,
):
    """
    Simply supported beam with a point load or full-span UDL.

    Inputs:
        length                 : m
        youngs_modulus         : MPa = N/mm^2
        moment_of_inertia      : mm^4
        load_type              : "Point load" or "UDL"
        load_magnitude         : kN or kN/m
        load_position          : m, required for point load
        num_points             : number of plotting points

    Outputs:
        Reactions and shear    : kN
        Moment                 : kN.m
        Deflection             : mm, downward positive
        x coordinates          : m
    """

    # 1. Validate common inputs
    _validate_number("Beam length", length, positive=True)
    _validate_number("Young's modulus", youngs_modulus, positive=True)
    _validate_number(
        "Second moment of area", moment_of_inertia, positive=True
    )
    _validate_number("Load magnitude", load_magnitude, nonnegative=True)

    if load_type not in ("Point load", "UDL"):
        raise ValueError(
            "This solver supports Point load and UDL only."
        )

    if isinstance(num_points, bool) or not isinstance(num_points, int):
        raise ValueError("Number of plotting points must be an integer.")

    if num_points < 2:
        raise ValueError("Number of plotting points must be at least 2.")

    # 2. Convert to N, mm, N/mm^2
    L = length * 1000.0
    E = youngs_modulus
    I = moment_of_inertia

    x = np.linspace(0.0, L, num_points)

    # Arrays use downward load as positive.
    shear = np.zeros(num_points)
    moment = np.zeros(num_points)
    deflection = np.zeros(num_points)

    # 3. Point load
    if load_type == "Point load":

        if load_position is None:
            raise ValueError("Point-load position is required.")

        _validate_number("Point-load position", load_position)

        if not 0.0 <= load_position <= length:
            raise ValueError(
                "Point-load position must be strictly inside the beam span."
            )

        P = load_magnitude * 1000.0
        a = load_position * 1000.0
        b = L - a

        # Reactions in N
        RA = P * b / L
        RB = P * a / L

        # Shear force immediately to the left of the point load
        left = x < a
        shear[left] = RA

        # Shear force at and to the right of the point load
        # At x = a, use the right-hand value: RA - P
        shear[~left] = RA - P

        # Bending moment in N.mm
        moment = RA * x - P * np.maximum(x - a, 0.0)

        # Elastic curve: downward deflection is positive
        left = x <= a
        right = ~left

        xl = x[left]
        xr = x[right]

        deflection[left] = (
            P * b * xl
            * (L**2 - b**2 - xl**2)
            / (6.0 * L * E * I)
        )

        deflection[right] = (
            P * a * (L - xr)
            * (L**2 - a**2 - (L - xr)**2)
            / (6.0 * L * E * I)
        )

        # Exact maximum magnitudes
        max_shear = max(RA, RB)
        max_moment = P * a * b / L
        max_moment_x = a

        # Exact maximum deflection and its location
        c = min(a, b)

        max_deflection = (
            P * c * (L**2 - c**2)**1.5
            / (9.0 * math.sqrt(3.0) * L * E * I)
        )

        if a <= b:
            max_deflection_x = (
                L - math.sqrt((L**2 - a**2) / 3.0)
            )
        else:
            max_deflection_x = math.sqrt(
                (L**2 - b**2) / 3.0
            )

    # 4. Full-span uniformly distributed load
    else:
        # 1 kN/m = 1 N/mm numerically
        w = load_magnitude

        RA = w * L / 2.0
        RB = RA

        shear = RA - w * x
        moment = RA * x - w * x**2 / 2.0

        deflection = (
            w * x * (L**3 - 2.0 * L * x**2 + x**3)
            / (24.0 * E * I)
        )

        max_shear = RA
        max_moment = w * L**2 / 8.0
        max_moment_x = L / 2.0

        max_deflection = (
            5.0 * w * L**4 / (384.0 * E * I)
        )
        max_deflection_x = L / 2.0

    # 5. Return results in the GUI's preferred units
    return {
        "reaction_A_kN": RA / 1000.0,
        "reaction_B_kN": RB / 1000.0,

        "max_shear_kN": max_shear / 1000.0,
        "max_moment_kNm": max_moment / 1e6,
        "max_moment_position_m": max_moment_x / 1000.0,

        "max_deflection_mm": max_deflection,
        "max_deflection_position_m": max_deflection_x / 1000.0,

        "x_m": x / 1000.0,
        "shear_kN": shear / 1000.0,
        "moment_kNm": moment / 1e6,
        "deflection_mm": deflection,
    }


def solve_cantilever_beam(
    length,
    youngs_modulus,
    moment_of_inertia,
    load_type,
    load_magnitude,
    load_position=None,
    num_points=501,
):
    """
    Analyse a cantilever beam with a downward point load
    or a full-span downward UDL.

    Units:
        length          : m
        load_magnitude  : kN for point load, kN/m for UDL
        load_position   : m from fixed support A
        youngs_modulus  : MPa = N/mm^2
        moment_of_inertia: mm^4

    Returned:
        reactions and shear : kN
        moment              : kN.m
        deflection          : mm, downward positive
        coordinates         : m

    Moment convention:
        Hogging moment is negative.
    """

    # --------------------------------------------------
    # 1. Validate inputs
    # --------------------------------------------------
    # 1. Validate common inputs
    _validate_number("Beam length", length, positive=True)
    _validate_number("Young's modulus", youngs_modulus, positive=True)
    _validate_number(
        "Second moment of area", moment_of_inertia, positive=True
    )
    _validate_number("Load magnitude", load_magnitude, nonnegative=True)

    if load_type not in ("Point load", "UDL"):
        raise ValueError(
            "This solver supports Point load and UDL only."
        )

    if isinstance(num_points, bool) or not isinstance(num_points, int):
        raise ValueError("Number of plotting points must be an integer.")

    if num_points < 2:
        raise ValueError("Number of plotting points must be at least 2.")

    # --------------------------------------------------
    # 2. Convert to consistent internal units
    # --------------------------------------------------

    L = length * 1000.0       # m -> mm
    E = youngs_modulus        # MPa = N/mm^2
    I = moment_of_inertia     # mm^4

    # x is measured from the fixed support A.
    x = np.linspace(0.0, L, num_points)

    # --------------------------------------------------
    # 3. Point-load case
    # --------------------------------------------------

    if load_type == "Point load":

        if load_position is None:
            raise ValueError(
                "Load position is required for a point load."
            )

        a = _validate_number(
             "Load position",load_position, positive=True
        ) * 1000.0

        if a > L:
            raise ValueError(
                "Point load position must be strictly "
                "between the fixed support and free end."
            )

        P = load_magnitude * 1000.0  # kN -> N

        # Fixed-support reactions.
        reaction_A = P
        reaction_B = 0.0
        fixed_end_moment = P * a

        # Internal shear and bending moment.
        # The shear jumps to zero at the point load.
        shear_N = np.where(x < a, P, 0.0)
        moment_Nmm = -P * np.maximum(a - x, 0.0)

        # Downward-positive elastic curve.
        deflection_mm = np.where(
            x <= a,
            P * x**2 * (3.0 * a - x) / (6.0 * E * I),
            P * a**2 * (3.0 * x - a) / (6.0 * E * I),
        )

        max_shear_N = P
        max_moment_Nmm = P * a
        max_moment_position_m = 0.0

    # --------------------------------------------------
    # 4. Full-span UDL case
    # --------------------------------------------------

    else:

        w = load_magnitude  # kN/m = N/mm numerically

        # Fixed-support reactions.
        reaction_A = w * L
        reaction_B = 0.0
        fixed_end_moment = w * L**2 / 2.0

        # Internal shear and bending moment.
        shear_N = w * (L - x)
        moment_Nmm = -w * (L - x)**2 / 2.0

        # Downward-positive elastic curve.
        deflection_mm = (
            w * x**2
            * (6.0 * L**2 - 4.0 * L * x + x**2)
            / (24.0 * E * I)
        )

        max_shear_N = w * L
        max_moment_Nmm = w * L**2 / 2.0
        max_moment_position_m = 0.0

    # --------------------------------------------------
    # 5. Convert outputs to GUI/display units
    # --------------------------------------------------

    shear_kN = shear_N / 1000.0
    moment_kNm = moment_Nmm / 1e6
    x_m = x / 1000.0

    max_deflection_mm = float(np.max(deflection_mm))
    max_deflection_index = int(np.argmax(deflection_mm))

    return {
        "reaction_A_kN": reaction_A / 1000.0,
        "reaction_B_kN": reaction_B / 1000.0,
        "fixed_end_moment_kNm": fixed_end_moment / 1e6,

        "max_shear_kN": max_shear_N / 1000.0,
        "max_shear_position_m": 0.0,

        "max_moment_kNm": max_moment_Nmm / 1e6,
        "max_moment_position_m": max_moment_position_m,

        "max_deflection_mm": max_deflection_mm,
        "max_deflection_position_m": float(
            x_m[max_deflection_index]
        ),

        "x_m": x_m,
        "shear_kN": shear_kN,
        "moment_kNm": moment_kNm,
        "deflection_mm": deflection_mm,
    }