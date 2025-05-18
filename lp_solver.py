"""
lp_solver.py - Linear programming solver for Hide & Seek game

This module formulates and solves the linear programming problem
to find optimal strategies for the computer player.
"""

import numpy as np
from scipy.optimize import linprog
from player import PlayerType

class LPSolver:
    """Linear programming solver for game theory problems."""

    def solve_game(self, payoff_matrix, player_type, view=PlayerType.HIDER):
        """
        Solve the game for optimal mixed strategy.

        Args:
            payoff_matrix (list): 2D list representing the payoff matrix
            player_type (PlayerType): Type of player (HIDER or SEEKER)
            view (PlayerType): Perspective of the payoff matrix

        Returns:
            list: Probability distribution over positions
        """
        matrix = np.array(payoff_matrix)
        if player_type == PlayerType.HIDER and view == PlayerType.HIDER:
            return self._solve_hider(matrix)
        elif player_type == PlayerType.SEEKER and view == PlayerType.SEEKER:
            return self._solve_hider(matrix)
        elif player_type == PlayerType.HIDER and view == PlayerType.SEEKER:
            return self._solve_seeker(matrix.T)
        elif player_type == PlayerType.SEEKER and view == PlayerType.HIDER:
            return self._solve_seeker(matrix.T)
        else:
            raise ValueError("Invalid player type or view")

    def _solve_hider(self, matrix):
        # Maximize v, subject to: sum(p_i) = 1, p_i >= 0, and for all j: sum_i p_i * A[i][j] >= v
        m, n = matrix.shape
        c = np.zeros(m + 1)
        c[-1] = -1  # maximize v <=> minimize -v

        # Constraints: sum_i p_i * A[i][j] - v >= 0  for all j
        A_ub = []
        b_ub = []
        for j in range(n):
            constraint = np.zeros(m + 1)
            constraint[:m] = -matrix[:, j]
            constraint[-1] = 1
            A_ub.append(constraint)
            b_ub.append(0)
        # sum_i p_i = 1
        A_eq = [np.append(np.ones(m), 0)]
        b_eq = [1]
        bounds = [(0, 1)] * m + [(None, None)]
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        if res.success:
            return res.x[:m]
        else:
            # fallback: uniform
            return np.ones(m) / m

    def _solve_seeker(self, matrix):
        # Minimize v, subject to: sum(q_j) = 1, q_j >= 0, and for all i: sum_j q_j * A[i][j] <= v
        m, n = matrix.shape
        c = np.zeros(n + 1)
        c[-1] = 1  # minimize v

        # Constraints: sum_j q_j * A[i][j] - v <= 0  for all i
        A_ub = []
        b_ub = []
        for i in range(m):
            constraint = np.zeros(n + 1)
            constraint[:n] = matrix[i, :]
            constraint[-1] = -1
            A_ub.append(constraint)
            b_ub.append(0)
        # sum_j q_j = 1
        A_eq = [np.append(np.ones(n), 0)]
        b_eq = [1]
        bounds = [(0, 1)] * n + [(None, None)]
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        if res.success:
            return res.x[:n]
        else:
            # fallback: uniform
            return np.ones(n) / n