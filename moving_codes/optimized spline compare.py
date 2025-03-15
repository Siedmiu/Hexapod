import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from spline_optimizer import SplineOptimizer

#
#spline_optimizer module is needed for this script
#

def catmull_rom_spline(x, y, num_points=100):
    #no direct implementation of cr spline in scypy, see youtube tutorial linked in issue
    n = len(x)
    x_extended = np.concatenate([[x[0]], x, [x[-1]]])
    y_extended = np.concatenate([[y[0]], y, [y[-1]]])
    x_out = np.linspace(x[0], x[-1], num_points)
    y_out = np.zeros_like(x_out)

    #For each output point, find the corresponding segment and interpolate
    for i in range(len(x_out)):
        # Find the segment this point belongs to
        t = (x_out[i] - x[0]) / (x[-1] - x[0]) * (n - 1)
        segment = min(int(t), n - 2)
        t = t - segment  # Normalize t to [0,1]

        p0 = np.array([x_extended[segment], y_extended[segment]])
        p1 = np.array([x_extended[segment + 1], y_extended[segment + 1]])
        p2 = np.array([x_extended[segment + 2], y_extended[segment + 2]])
        p3 = np.array([x_extended[segment + 3], y_extended[segment + 3]])

        # Catmull-Rom interpolation
        t2 = t * t
        t3 = t2 * t

        y_out[i] = 0.5 * ((2 * p1[1]) +
                          (-p0[1] + p2[1]) * t +
                          (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                          (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)

    return x_out, y_out


def calculate_spline_metrics(spline, x_orig, y_orig, x_fine):
    spline_at_orig = spline(x_orig)
    accuracy_cost = np.mean((spline_at_orig - y_orig) ** 2)

    y_prime = spline(x_fine, 1)
    energy_cost = np.mean(y_prime ** 2)

    y_prime2 = spline(x_fine, 2)
    smoothness_cost = np.mean(y_prime2 ** 2)

    return {
        "accuracy": accuracy_cost,
        "energy": energy_cost,
        "smoothness": smoothness_cost
    }


x = np.array([0, 2, 4, 6, 8, 10])
y = np.array([0, 1, 3, 2, 3, 5])

optimizer = SplineOptimizer(x, y)

weight_configs = [
    #{"name": "Balanced", "accuracy": 1.0, "energy": 1.0, "smoothness": 1.0},
    {"name": "High Accuracy", "accuracy": 10.0, "energy": 0.1, "smoothness": 0.1},
    {"name": "Energy Efficient", "accuracy": 10.0, "energy": 3.0, "smoothness": 0.5},
    {"name": "Very Smooth", "accuracy": 10.0, "energy": 0.5, "smoothness": 3.0},
    {"name": "Custom", "accuracy": 15.0, "energy": 0.3, "smoothness": 1.5}
]

#seprate evaluation of not optimized splines
x_fine = np.linspace(x[0], x[-1], 200)
natural_cs = CubicSpline(x, y, bc_type='natural')
nc_y = natural_cs(x_fine)
nc_metrics = calculate_spline_metrics(natural_cs, x, y, x_fine)

#normal splines
nc_x = np.linspace(x[0], x[-1], 200)
natural_cs = CubicSpline(x, y, bc_type='natural')
cr_x, cr_y = catmull_rom_spline(x, y, num_points=200)

#optimized splines
optimized_splines = []
for config in weight_configs:
    opt_x, opt_y, cost_components = optimizer.optimize(
        w_accuracy=config["accuracy"],
        w_energy=config["energy"],
        w_smoothness=config["smoothness"],
    )
    optimized_splines.append({
        "name": config["name"],
        "x": opt_x,
        "y": opt_y,
        "cost_components": cost_components,
        "config": config
    })

plt.figure(figsize=(14, 12))

ax1 = plt.subplot2grid((5, 1), (0, 0), rowspan=3)
ax1.plot(x, y, 'ko-', markersize=8, linewidth=1, label="Original Points")
ax1.plot(x_fine, nc_y, 'c--', linewidth=1.5,
         label=f"Natural Cubic Spline (Acc: {nc_metrics['accuracy']:.4f}, En: {nc_metrics['energy']:.4f}, Sm: {nc_metrics['smoothness']:.4f})")
ax1.plot(cr_x, cr_y, 'm--', linewidth=1.5, label="Catmull-Rom Spline")

colors = ['red', 'blue', 'green', 'orange']
for i, spline in enumerate(optimized_splines):
    ax1.plot(
        spline["x"], spline["y"],
        color=colors[i],
        linewidth=2,
        label=f"{spline['name']} (Acc: {spline['cost_components']['accuracy']:.4f}, En: {spline['cost_components']['energy']:.4f}, Sm: {spline['cost_components']['smoothness']:.4f})"
    )

ax1.legend(loc='upper left', fontsize=9)
ax1.set_xlabel("X")
ax1.set_ylabel("Y")
ax1.set_title("Cubic Spline Optimization with Different Cost Weights")
ax1.grid(True)


ax2 = plt.subplot2grid((5, 1), (3, 0), rowspan=2)
ax2.axis('off')

column_labels = [
    'Accuracy\nWeight',
    'Energy\nWeight',
    'Smoothness\nWeight',
    'Accuracy\nCost',
    'Energy\nCost',
    'Smoothness\nCost',
    'Weighted\nTotal'
]

cell_text = [
    ["N/A", "N/A", "N/A",
     f"{nc_metrics['accuracy']:.4f}",
     f"{nc_metrics['energy']:.4f}",
     f"{nc_metrics['smoothness']:.4f}",
     "N/A"]
]

for s in optimized_splines:
    row = [
        f"{s['config']['accuracy']:.1f}",
        f"{s['config']['energy']:.1f}",
        f"{s['config']['smoothness']:.1f}",
        f"{s['cost_components']['accuracy']:.4f}",
        f"{s['cost_components']['energy']:.4f}",
        f"{s['cost_components']['smoothness']:.4f}",
        f"{s['cost_components']['weighted_total']:.4f}"
    ]
    cell_text.append(row)

row_labels = ["Natural Cubic Spline"] + [s['name'] for s in optimized_splines]

table = ax2.table(cellText=cell_text,
                 rowLabels=row_labels,
                 colLabels=column_labels,
                 cellLoc='center',
                 loc='center')
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 1.5)

plt.tight_layout()
plt.subplots_adjust(hspace=0.05)
plt.show()

print("\nDetailed Cost Information for Each Spline:")
print("=" * 80)

print("\nNatural Cubic Spline:")
print(f"  Accuracy cost: {nc_metrics['accuracy']:.6f}")
print(f"  Energy cost: {nc_metrics['energy']:.6f}")
print(f"  Smoothness cost: {nc_metrics['smoothness']:.6f}")

for spline in optimized_splines:
    print(f"\n{spline['name']} Spline:")
    print(f"  Weights: Accuracy={spline['config']['accuracy']:.1f}, "
          f"Energy={spline['config']['energy']:.1f}, "
          f"Smoothness={spline['config']['smoothness']:.1f}")
    print(f"  Resulting costs:")
    print(f"    Accuracy cost: {spline['cost_components']['accuracy']:.6f}")
    print(f"    Energy cost: {spline['cost_components']['energy']:.6f}")
    print(f"    Smoothness cost: {spline['cost_components']['smoothness']:.6f}")
    print(f"    Weighted total cost: {spline['cost_components']['weighted_total']:.6f}")