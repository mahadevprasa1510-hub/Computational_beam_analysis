
import matplotlib.pyplot as plt


def plot_deflected_shape(results):
    """Plot the beam's deflected shape."""

    x = results["x_m"]
    deflection = results["deflection_mm"]

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(
        x,
        deflection,
        color="blue",
        linewidth=2,
        label="Deflected shape"
    )

    ax.axhline(
        y=0,
        color="black",
        linewidth=1,
        linestyle="--",
        label="Undeformed reference"
    )

    ax.set_xlabel("Position (m)")
    ax.set_ylabel("Deflection (mm)")
    ax.set_title("Beam Deflected Shape")
    ax.grid(True, linestyle=":")
    ax.legend()

    # Positive deflection is downward in our solver convention.
    ax.invert_yaxis()

    fig.tight_layout()
    return fig


def plot_bending_moment_diagram(results):
    """Plot the bending moment diagram (BMD)."""

    x = results["x_m"]
    moment = results["moment_kNm"]

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(
        x,
        moment,
        color="red",
        linewidth=2,
        label="Bending moment"
    )

    ax.fill_between(x, moment, 0, alpha=0.2, color="red")
    ax.axhline(y=0, color="black", linewidth=1)

    ax.set_xlabel("Position (m)")
    ax.set_ylabel("Bending Moment (kN·m)")
    ax.set_title("Bending Moment Diagram")
    ax.grid(True, linestyle=":")
    ax.legend()

    fig.tight_layout()
    return fig


def plot_shear_force_diagram(results):
    """Plot the shear force diagram (SFD)."""

    x = results["x_m"]
    shear = results["shear_kN"]

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(
        x,
        shear,
        color="green",
        linewidth=2,
        label="Shear force"
    )

    ax.fill_between(x, shear, 0, alpha=0.2, color="green")
    ax.axhline(y=0, color="black", linewidth=1)

    ax.set_xlabel("Position (m)")
    ax.set_ylabel("Shear Force (kN)")
    ax.set_title("Shear Force Diagram")
    ax.grid(True, linestyle=":")
    ax.legend()

    fig.tight_layout()
    return fig
