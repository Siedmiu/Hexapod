import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline


def cubic_spline_optimization(x, y, num_points=100):
    #potrzebna własna implementacja aby stworzyć funkcje kosztu
    coeffs = np.polyfit(x, y, 3)  # Fit a cubic polynomial

    first_point_val = np.polyval(coeffs, x[0])
    offset = y[0] - first_point_val
    coeffs[-1] += offset

    x_fine = np.linspace(x[0], x[-1], num_points)
    y_smooth = np.polyval(coeffs, x_fine)
    return x_fine, y_smooth


def natural_cubic_spline(x, y, num_points=100):
    cs = CubicSpline(x, y, bc_type='natural')
    x_fine = np.linspace(x[0], x[-1], num_points)
    y_smooth = cs(x_fine)
    return x_fine, y_smooth


def catmull_rom_spline(x, y, num_points=100):
    n = len(x)

    x_extended = np.concatenate([[x[0]], x, [x[-1]]])
    y_extended = np.concatenate([[y[0]], y, [y[-1]]])

    x_out = np.linspace(x[0], x[-1], num_points)
    y_out = np.zeros_like(x_out)

    for i in range(len(x_out)):
        t = (x_out[i] - x[0]) / (x[-1] - x[0]) * (n - 1)
        segment = min(int(t), n - 2)
        t = t - segment

        p0 = np.array([x_extended[segment], y_extended[segment]])
        p1 = np.array([x_extended[segment + 1], y_extended[segment + 1]])
        p2 = np.array([x_extended[segment + 2], y_extended[segment + 2]])
        p3 = np.array([x_extended[segment + 3], y_extended[segment + 3]])

        t2 = t * t
        t3 = t2 * t

        y_out[i] = 0.5 * ((2 * p1[1]) +
                          (-p0[1] + p2[1]) * t +
                          (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                          (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)

    return x_out, y_out


x = np.array([0, 2, 4, 6, 8, 10])
y = np.array([0, 1, 3, 2, 3, 5])

opt_x, opt_y = cubic_spline_optimization(x, y)

#użycie gotowych funkcji sciPY
nc_x, nc_y = natural_cubic_spline(x, y)
cr_x, cr_y = catmull_rom_spline(x, y)

plt.figure(figsize=(10, 6))
plt.plot(x, y, 'ro-', label="Original Points")
plt.plot(nc_x, nc_y, 'm-', label="Natural Cubic Spline")
plt.plot(opt_x, opt_y, 'b-', label="Cubic Spline Optimization")
plt.plot(cr_x, cr_y, 'g-', label="Catmull-Rom Spline")
plt.plot(x[0], y[0], 'ko', markersize=8, label="First Point")

plt.legend()
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Comparison of Different Spline Methods")
plt.grid()
plt.show()