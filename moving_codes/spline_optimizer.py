import numpy as np
from scipy.optimize import minimize
from scipy.interpolate import CubicSpline

#
#this sctipt is needed for Optimized Spline Compare
#

class SplineOptimizer:
    def __init__(self, x_points, y_points):
        self.x_points = np.array(x_points)
        self.y_points = np.array(y_points)
        self.num_points = len(x_points)
        self.x_fine = np.linspace(x_points[0], x_points[-1], 200)

    def _create_spline(self, control_points):
        #keeps the begining and the end fixed
        y_control = np.zeros(self.num_points)
        y_control[0] = self.y_points[0]
        y_control[-1] = self.y_points[-1]
        y_control[1:-1] = control_points

        cs = CubicSpline(self.x_points, y_control)
        y_spline = cs(self.x_fine)
        y_prime = cs(self.x_fine, 1)  #calculate the first derivative for acceleration and smoothness
        y_prime2 = cs(self.x_fine, 2)  #second derivative is used in calculation and can visualze jerk (change in acceleration)

        return y_spline, y_prime, y_prime2, cs

    def _evaluate_cost(self, control_points, w_accuracy, w_energy, w_smoothness):

            #control_points: y-values for interior control points (begining and end is fixed)
            #w_accuracy: weight for point accuracy
            #w_energy: weight for energy efficiency
            #w_smoothness: weight for smoothness

        y_spline, y_prime, y_prime2, cs = self._create_spline(control_points)
        spline_at_orig = cs(self.x_points)

        accuracy_errors = spline_at_orig - self.y_points
        accuracy_cost = np.mean(accuracy_errors ** 2)

        #energy efficiency cost: mean squared first derivative (change in acceleration)
        energy_cost = np.mean(y_prime ** 2)

        #smoothness cost: mean squared second derivative (jerk)
        smoothness_cost = np.mean(y_prime2 ** 2)

        total_cost = (w_accuracy * accuracy_cost +
                      w_energy * energy_cost +
                      w_smoothness * smoothness_cost)

        return total_cost

    def optimize(self, w_accuracy=1.0, w_energy=1.0, w_smoothness=1.0, verbose=False):
        initial_controls = self.y_points[1:-1].copy()

        def cost_func(controls):
            return self._evaluate_cost(controls, w_accuracy, w_energy, w_smoothness)

        result = minimize(
            cost_func,
            initial_controls,
            method='BFGS',
            options={'disp': verbose, 'maxiter': 1000}
        )

        optimized_controls = result.x
        _, _, _, cs = self._create_spline(optimized_controls)
        y_optimized = cs(self.x_fine)

        component_costs = {}
        y_control = np.zeros(self.num_points)
        y_control[0] = self.y_points[0]
        y_control[-1] = self.y_points[-1]
        y_control[1:-1] = optimized_controls

        spline = CubicSpline(self.x_points, y_control)
        y_vals = spline(self.x_fine)
        y_prime = spline(self.x_fine, 1)
        y_prime2 = spline(self.x_fine, 2)

        # Calculate each component of the cost
        spline_at_orig = spline(self.x_points)
        accuracy_cost = np.mean((spline_at_orig - self.y_points) ** 2)
        energy_cost = np.mean(y_prime ** 2)
        smoothness_cost = np.mean(y_prime2 ** 2)

        component_costs = {
            "accuracy": accuracy_cost,
            "energy": energy_cost,
            "smoothness": smoothness_cost,
            "weighted_total": result.fun
        }

        return self.x_fine, y_optimized, component_costs