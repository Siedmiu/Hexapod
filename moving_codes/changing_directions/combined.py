import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import matplotlib.animation as animation
from collections import deque

matplotlib.use('TkAgg')

class CombinedHexapodController:
    def __init__(self):
        # Movement direction constants
        self.FORWARD = 1
        self.BACKWARD = 2
        self.RIGHT = 3
        self.LEFT = 4
        self.STOP = 0
        
        # Gait mode constants
        self.TRI_GATE = 1
        self.BI_GATE = 2
        
        # State management
        self.current_direction = self.STOP
        self.requested_direction = self.STOP
        self.current_gait = self.TRI_GATE
        self.requested_gait = self.TRI_GATE
        self.current_phase = "stopped"  # "stopped", "startup", "main_loop", "shutdown"
        self.main_loop_counter = 0
        self.transition_pending = False
        self.gait_change_pending = False
        
        # Animation queue for smooth transitions
        self.animation_queue = deque()
        self.current_frame = 0
        
        # Initialize hexapod parameters
        self.setup_hexapod_parameters()
        self.generate_base_trajectories()
        
        print("Combined Hexapod Ready! Controls:")
        print("↑ - Forward")
        print("↓ - Backward") 
        print("→ - Right")
        print("← - Left")
        print("SPACE - Stop")
        print("T - Tri-Gate Mode")
        print("B - Bi-Gate Mode")
        print("Press any arrow key to start moving!")
        
    def setup_hexapod_parameters(self):
        """Initialize all hexapod physical parameters"""
        # Segment lengths
        self.h1 = -0.016854 - 0.003148
        self.l1 = 0.12886 - 0.0978
        self.l2 = 0.2188 - 0.12886
        self.h2 = -0.011804 + 0.016854
        self.l3 = 0.38709 - 0.2188
        self.staly_kat_przy_P1 = np.arctan2(self.h2, self.l2)
        
        # Rest position angles
        alfa_1 = 0
        alfa_2 = np.radians(0)
        alfa_3 = np.radians(60)
        
        # Calculate rest foot position
        P0 = np.array([0, 0, 0])
        P0_pod = P0 + np.array([0, 0, self.h1])
        P1 = P0_pod + np.array([self.l1 * np.cos(alfa_1), self.l1 * np.sin(alfa_1), 0])
        P2 = P1 + np.array([np.cos(alfa_1)*np.cos(alfa_2)*self.l2, np.sin(alfa_1)*np.cos(alfa_2)*self.l2, np.sin(alfa_2) * self.l2])
        P3 = P1 + np.array([np.cos(alfa_1)*np.cos(self.staly_kat_przy_P1 + alfa_2)*np.sqrt(self.h2**2 + self.l2**2), np.sin(alfa_1)*np.cos(self.staly_kat_przy_P1 + alfa_2)*np.sqrt(self.h2**2 + self.l2**2), np.sin(self.staly_kat_przy_P1 + alfa_2)*np.sqrt(self.h2**2 + self.l2**2)])
        P4 = P3 + np.array([np.cos(alfa_1)*np.cos(alfa_2 - alfa_3)*self.l3, np.sin(alfa_1)*np.cos(alfa_2 - alfa_3)*self.l3, np.sin(alfa_2 - alfa_3) * self.l3])
        
        self.stopa_spoczynkowa = P4
        self.wysokosc_start = -self.stopa_spoczynkowa[2]
        
        # Leg attachment points and orientations
        self.przyczepy_nog_do_tulowia = np.array([
            [0.073922, 0.055095, 0.003148],
            [0.0978, -0.00545, 0.003148],
            [0.067301, -0.063754, 0.003148],
            [-0.067301, -0.063754, 0.003148],
            [-0.0978, -0.00545, 0.003148],
            [-0.073922, 0.055095, 0.003148],
        ])
        
        self.nachylenia_nog_do_bokow_platformy_pajaka = np.array([
            np.deg2rad(37.169), 0, np.deg2rad(-37.169), 
            np.deg2rad(180 + 37.169), np.deg2rad(180), np.deg2rad(180 - 37.169)
        ])
        
        # Movement parameters
        self.h = self.l3 / 4
        self.r = self.h
        # Different point counts for different gaits
        self.tri_gate_points = 20
        self.bi_gate_points = 10

    def get_current_points(self):
        """Get current point count based on gait mode"""
        return self.bi_gate_points if self.current_gait == self.BI_GATE else self.tri_gate_points

    def katy_serw(self, P3, l1, h1, l2, h2, l3):
        """Calculate servo angles for given foot position"""
        alfa_1 = np.arctan2(P3[1], P3[0])
        P1 = np.array([l1 * np.cos(alfa_1), l1 * np.sin(alfa_1), h1])
        d = np.sqrt((P3[0] - P1[0]) ** 2 + (P3[1] - P1[1]) ** 2 + (P3[2] - P1[2]) ** 2)
        r = np.sqrt(l2 ** 2 + h2 ** 2)
        staly_kat_przy_P1 = np.arctan2(h2, l2)
        cos_fi = (r ** 2 + l3 ** 2 - d ** 2) / (2 * r * l3)
        fi = np.arccos(cos_fi)
        alfa_3 = np.deg2rad(180) - fi - staly_kat_przy_P1
        epsilon = np.arcsin(np.sin(fi) * l3 / d)
        tau = np.arctan2(P3[2] - P1[2], np.sqrt((P3[0] - P1[0]) ** 2 + (P3[1] - P1[1]) ** 2))
        alfa_2 = -(epsilon + tau - staly_kat_przy_P1)
        return [alfa_1, alfa_2, alfa_3]

    def funkcja_ruchu_nogi(self, r, h, punkt_ruchu):
        """Parabolic trajectory function"""
        return (-4 * h * (punkt_ruchu ** 2)) / (r ** 2) + (4 * h * punkt_ruchu) / r

    def dlugosc_funkcji_ruchu_nogi(self, r, h, ilosc_probek):
        """Calculate trajectory length"""
        suma = 0
        for i in range(1, ilosc_probek):
            z_0 = self.funkcja_ruchu_nogi(r, h, (i-1)/ilosc_probek * r)
            z_1 = self.funkcja_ruchu_nogi(r, h, i/ilosc_probek * r)
            dlugosc = np.sqrt((z_1 - z_0) ** 2 + (r/ilosc_probek) ** 2)
            suma += dlugosc
        return suma

    def znajdz_punkty_rowno_odlegle_na_paraboli(self, r, h, ilosc_punktow_na_krzywej, ilosc_probek, bufor, ruch_strafing):
        """Generate evenly spaced points on parabolic trajectory"""
        L = self.dlugosc_funkcji_ruchu_nogi(r, h, ilosc_probek)
        dlugosc_kroku = L/ilosc_punktow_na_krzywej
        suma = 0
        punkty = []
        for i in range(1, ilosc_probek):
            z_0 = self.funkcja_ruchu_nogi(r, h, (i-1)/ilosc_probek * r)
            z_1 = self.funkcja_ruchu_nogi(r, h, i/ilosc_probek * r)
            dlugosc = np.sqrt((z_1 - z_0) ** 2 + (r/ilosc_probek) ** 2)
            suma += dlugosc
            if suma > dlugosc_kroku:
                suma = suma - dlugosc_kroku
                if ruch_strafing:
                    punkty.append([i/ilosc_probek * r + bufor, 0, z_1])
                else:
                    punkty.append([0, i/ilosc_probek * r + bufor, z_1])
            if len(punkty) == ilosc_punktow_na_krzywej - 1:
                break
        
        if ruch_strafing:
            punkty.append([bufor + r, 0, 0])
        else:
            punkty.append([0, bufor + r, 0])
        return punkty

    def generate_base_trajectories(self):
        """Generate base trajectory segments for all directions and both gaits"""
        self.base_trajectories = {}
        
        for gait_mode in [self.TRI_GATE, self.BI_GATE]:
            self.base_trajectories[gait_mode] = {}
            points_count = self.bi_gate_points if gait_mode == self.BI_GATE else self.tri_gate_points
            
            for direction in [self.FORWARD, self.BACKWARD, self.RIGHT, self.LEFT]:
                ruch_strafing = direction in [self.RIGHT, self.LEFT]
                ruch_do_tylu = direction == self.BACKWARD
                ruch_w_lewo = direction == self.LEFT
                
                # Generate trajectory segments
                punkty_etap1_ruchu = self.znajdz_punkty_rowno_odlegle_na_paraboli(
                    self.r, self.h / 2, points_count, 10000, 0, ruch_strafing)
                
                if ruch_strafing:
                    punkty_etap2_ruchu_coord = np.linspace(
                        self.r * (points_count - 1) / points_count, 0, points_count)
                    punkty_etap2_ruchu = [[punkty_etap2_ruchu_coord[i], 0, 0] for i in range(points_count)]
                    punkty_etap3_ruchu_coord = np.linspace(-self.r / points_count, -self.r, points_count)
                    punkty_etap3_ruchu = [[punkty_etap3_ruchu_coord[i], 0, 0] for i in range(points_count)]
                else:
                    punkty_etap2_ruchu_coord = np.linspace(
                        self.r * (points_count - 1) / points_count, 0, points_count)
                    punkty_etap2_ruchu = [[0, punkty_etap2_ruchu_coord[i], 0] for i in range(points_count)]
                    punkty_etap3_ruchu_coord = np.linspace(-self.r / points_count, -self.r, points_count)
                    punkty_etap3_ruchu = [[0, punkty_etap3_ruchu_coord[i], 0] for i in range(points_count)]
                
                # Etap4 length varies between gaits
                etap4_points = 2 * points_count if gait_mode == self.TRI_GATE else points_count
                punkty_etap4_ruchu = self.znajdz_punkty_rowno_odlegle_na_paraboli(
                    2 * self.r, self.h, etap4_points, 20000, -self.r, ruch_strafing)
                punkty_etap5_ruchu = self.znajdz_punkty_rowno_odlegle_na_paraboli(
                    self.r, self.h / 2, points_count, 10000, -self.r, ruch_strafing)
                
                trajectory_data = {
                    'etap1': punkty_etap1_ruchu,
                    'etap2': punkty_etap2_ruchu,
                    'etap3': punkty_etap3_ruchu,
                    'etap4': punkty_etap4_ruchu,
                    'etap5': punkty_etap5_ruchu,
                    'ruch_strafing': ruch_strafing,
                    'ruch_do_tylu': ruch_do_tylu,
                    'ruch_w_lewo': ruch_w_lewo
                }
                
                # Add bi-gate specific trajectories
                if gait_mode == self.BI_GATE:
                    punkty_etap6_ruchu = punkty_etap5_ruchu.copy()
                    punkty_etap6_ruchu.reverse()
                    punkty_etap7_ruchu = punkty_etap1_ruchu.copy()
                    punkty_etap7_ruchu.reverse()
                    trajectory_data['etap6'] = punkty_etap6_ruchu
                    trajectory_data['etap7'] = punkty_etap7_ruchu
                
                self.base_trajectories[gait_mode][direction] = trajectory_data
        
        # Rest position
        rest_angles = np.zeros((6, 1, 3))
        for j in range(6):
            rest_position = np.array([
                self.stopa_spoczynkowa[0], self.stopa_spoczynkowa[1], self.stopa_spoczynkowa[2]
            ])
            rest_angles[j, 0] = self.katy_serw(rest_position, self.l1, self.h1, self.l2, self.h2, self.l3)
        
        self.rest_angles = rest_angles

    def generate_tri_gate_sequence(self, direction, phase_type):
        """Generate tri-gate trajectory sequence"""
        traj = self.base_trajectories[self.TRI_GATE][direction]
        
        if phase_type == "startup":
            if traj['ruch_do_tylu'] or traj['ruch_w_lewo']:
                cykl_ogolny_nog_1_3_5 = traj['etap2'] + traj['etap3'] + traj['etap5']
                cykl_ogolny_nog_2_4_6 = traj['etap4'] + traj['etap2']
            else:
                cykl_ogolny_nog_1_3_5 = traj['etap1'].copy()
                cykl_ogolny_nog_2_4_6 = traj['etap3'].copy()
                
        elif phase_type == "main_loop":
            cykl_ogolny_nog_1_3_5 = traj['etap2'] + traj['etap3'] + traj['etap4']
            cykl_ogolny_nog_2_4_6 = traj['etap4'] + traj['etap2'] + traj['etap3']
            
        elif phase_type == "shutdown":
            if traj['ruch_do_tylu'] or traj['ruch_w_lewo']:
                cykl_ogolny_nog_1_3_5 = traj['etap1'].copy()
                cykl_ogolny_nog_2_4_6 = traj['etap3'].copy()
            else:
                cykl_ogolny_nog_1_3_5 = traj['etap2'] + traj['etap3'] + traj['etap5']
                cykl_ogolny_nog_2_4_6 = traj['etap4'] + traj['etap2']
        
        return self.build_tri_gate_trajectory(cykl_ogolny_nog_1_3_5, cykl_ogolny_nog_2_4_6, traj)

    def generate_bi_gate_sequence(self, direction, phase_type):
        """Generate bi-gate trajectory sequence"""
        traj = self.base_trajectories[self.BI_GATE][direction]
        
        # Create stationary sequence for legs 2&5 during startup
        pierwszy_krok_nog_2_5 = []
        for i in range(self.bi_gate_points):
            pierwszy_krok_nog_2_5.append([0, 0, 0])
        
        if phase_type == "startup":
            if traj['ruch_do_tylu'] or traj['ruch_w_lewo']:
                cykl_nog_1_4 = traj['etap5'].copy()
                cykl_nog_2_5 = pierwszy_krok_nog_2_5.copy()
                cykl_nog_3_6 = traj['etap7'].copy()
            else:
                cykl_nog_1_4 = traj['etap6'].copy()
                cykl_nog_2_5 = pierwszy_krok_nog_2_5.copy()
                cykl_nog_3_6 = traj['etap1'].copy()
                
        elif phase_type == "main_loop":
            cykl_nog_1_4 = traj['etap4'] + traj['etap2'] + traj['etap3']
            cykl_nog_2_5 = traj['etap3'] + traj['etap4'] + traj['etap2']
            cykl_nog_3_6 = traj['etap2'] + traj['etap3'] + traj['etap4']
            
        elif phase_type == "shutdown":
            if traj['ruch_do_tylu'] or traj['ruch_w_lewo']:
                cykl_nog_1_4 = traj['etap6'].copy()
                cykl_nog_2_5 = pierwszy_krok_nog_2_5.copy()
                cykl_nog_3_6 = traj['etap1'].copy()
            else:
                cykl_nog_1_4 = traj['etap5'].copy()
                cykl_nog_2_5 = pierwszy_krok_nog_2_5.copy()
                cykl_nog_3_6 = traj['etap7'].copy()
        
        return self.build_bi_gate_trajectory(cykl_nog_1_4, cykl_nog_2_5, cykl_nog_3_6, traj)

    def build_tri_gate_trajectory(self, cykl_ogolny_nog_1_3_5, cykl_ogolny_nog_2_4_6, traj):
        """Build tri-gate trajectory from cycles"""
        cykl_ogolny_nog_1_3_5 = np.array(cykl_ogolny_nog_1_3_5)
        cykl_ogolny_nog_2_4_6 = np.array(cykl_ogolny_nog_2_4_6)
        
        # Apply reversal AFTER building the sequence
        if traj['ruch_do_tylu'] or traj['ruch_w_lewo']:
            cykl_ogolny_nog_1_3_5 = cykl_ogolny_nog_1_3_5[::-1]
            cykl_ogolny_nog_2_4_6 = cykl_ogolny_nog_2_4_6[::-1]
        
        # Transform cycles based on movement type
        if traj['ruch_strafing']:
            cykle_nog = np.array([
                [
                    [cykl_ogolny_nog_1_3_5[i][0] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]) +
                     cykl_ogolny_nog_1_3_5[i][1] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     -cykl_ogolny_nog_1_3_5[i][0] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]) +
                     cykl_ogolny_nog_1_3_5[i][1] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_ogolny_nog_1_3_5[i][2]]
                    for i in range(len(cykl_ogolny_nog_1_3_5))
                ] if j in (0, 2, 4) else
                [
                    [cykl_ogolny_nog_2_4_6[i][0] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]) +
                     cykl_ogolny_nog_2_4_6[i][1] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     -cykl_ogolny_nog_2_4_6[i][0] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]) +
                     cykl_ogolny_nog_2_4_6[i][1] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_ogolny_nog_2_4_6[i][2]]
                    for i in range(len(cykl_ogolny_nog_2_4_6))
                ]
                for j in range(6)
            ])
        else:
            cykle_nog = np.array([
                [
                    [cykl_ogolny_nog_1_3_5[i][1] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_ogolny_nog_1_3_5[i][1] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_ogolny_nog_1_3_5[i][2]]
                    for i in range(len(cykl_ogolny_nog_1_3_5))
                ] if j in (0, 2, 4) else
                [
                    [cykl_ogolny_nog_2_4_6[i][1] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_ogolny_nog_2_4_6[i][1] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_ogolny_nog_2_4_6[i][2]]
                    for i in range(len(cykl_ogolny_nog_2_4_6))
                ]
                for j in range(6)
            ])
        
        return self.calculate_servo_angles_from_cycles(cykle_nog, len(cykl_ogolny_nog_1_3_5))

    def build_bi_gate_trajectory(self, cykl_nog_1_4, cykl_nog_2_5, cykl_nog_3_6, traj):
        """Build bi-gate trajectory from cycles"""
        cykl_nog_1_4 = np.array(cykl_nog_1_4)
        cykl_nog_2_5 = np.array(cykl_nog_2_5) 
        cykl_nog_3_6 = np.array(cykl_nog_3_6)
        
        # Find the maximum length among all cycles
        max_length = max(len(cykl_nog_1_4), len(cykl_nog_2_5), len(cykl_nog_3_6))
        
        # Pad shorter cycles to match the maximum length
        def pad_cycle(cycle, target_length):
            if len(cycle) < target_length:
                last_pos = cycle[-1] if len(cycle) > 0 else [0, 0, 0]
                padding = [last_pos] * (target_length - len(cycle))
                return np.concatenate([cycle, padding])
            return cycle
        
        cykl_nog_1_4 = pad_cycle(cykl_nog_1_4, max_length)
        cykl_nog_2_5 = pad_cycle(cykl_nog_2_5, max_length)
        cykl_nog_3_6 = pad_cycle(cykl_nog_3_6, max_length)
        
        # Apply reversal AFTER building the sequence
        if traj['ruch_do_tylu'] or traj['ruch_w_lewo']:
            cykl_nog_1_4 = cykl_nog_1_4[::-1]
            cykl_nog_2_5 = cykl_nog_2_5[::-1]
            cykl_nog_3_6 = cykl_nog_3_6[::-1]
        
        # Transform cycles based on movement type
        if traj['ruch_strafing']:
            cykle_nog = np.array([
                [
                    [cykl_nog_1_4[i][0] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]) +
                     cykl_nog_1_4[i][1] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     -cykl_nog_1_4[i][0] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]) +
                     cykl_nog_1_4[i][1] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_nog_1_4[i][2]]
                    for i in range(max_length)
                ] if j in (0, 3) else
                [
                    [cykl_nog_2_5[i][0] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]) +
                     cykl_nog_2_5[i][1] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     -cykl_nog_2_5[i][0] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]) +
                     cykl_nog_2_5[i][1] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_nog_2_5[i][2]]
                    for i in range(max_length)
                ] if j in (1, 4) else
                [
                    [cykl_nog_3_6[i][0] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]) +
                     cykl_nog_3_6[i][1] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     -cykl_nog_3_6[i][0] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]) +
                     cykl_nog_3_6[i][1] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_nog_3_6[i][2]]
                    for i in range(max_length)
                ]
                for j in range(6)
            ])
        else:
            cykle_nog = np.array([
                [
                    [cykl_nog_1_4[i][1] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_nog_1_4[i][1] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_nog_1_4[i][2]]
                    for i in range(max_length)
                ] if j in (0, 3) else
                [
                    [cykl_nog_2_5[i][1] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_nog_2_5[i][1] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_nog_2_5[i][2]]
                    for i in range(max_length)
                ] if j in (1, 4) else
                [
                    [cykl_nog_3_6[i][1] * np.sin(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_nog_3_6[i][1] * np.cos(self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                     cykl_nog_3_6[i][2]]
                    for i in range(max_length)
                ]
                for j in range(6)
            ])
        
        return self.calculate_servo_angles_from_cycles(cykle_nog, max_length)

    def calculate_servo_angles_from_cycles(self, cykle_nog, max_length):
        """Calculate servo angles from leg cycles"""
        # Calculate foot positions
        polozenia_stop = np.array([
            [[
                self.stopa_spoczynkowa[0] + cykle_nog[j][i][0],
                self.stopa_spoczynkowa[1] + cykle_nog[j][i][1],
                self.stopa_spoczynkowa[2] + cykle_nog[j][i][2]
            ]
            for i in range(max_length)]
            for j in range(6)
        ])
        
        # Calculate servo angles
        wychyly_serw = np.array([
            [self.katy_serw(polozenia_stop[j][i], self.l1, self.h1, self.l2, self.h2, self.l3)
             for i in range(max_length)]
            for j in range(6)
        ])
        
        return wychyly_serw

    def generate_trajectory_sequence(self, direction, phase_type):
        """Generate trajectory sequence for given direction, phase, and current gait"""
        if self.current_gait == self.TRI_GATE:
            return self.generate_tri_gate_sequence(direction, phase_type)
        else:
            return self.generate_bi_gate_sequence(direction, phase_type)

    def calculate_positions_from_angles(self, angles):
        """Calculate 3D positions from servo angles"""
        P0_pod_tab = self.przyczepy_nog_do_tulowia + np.array([0, 0, self.h1])
        
        P1 = np.array([
            [
                self.przyczepy_nog_do_tulowia[j][0] + self.l1 * np.cos(angles[j][0] + self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                self.przyczepy_nog_do_tulowia[j][1] + self.l1 * np.sin(angles[j][0] + self.nachylenia_nog_do_bokow_platformy_pajaka[j]),
                self.przyczepy_nog_do_tulowia[j][2] + self.h1
            ] for j in range(6)
        ])
        
        P2 = P1 + np.array([
            [
                np.cos(angles[j][0] + self.nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(-angles[j][1]) * self.l2,
                np.sin(angles[j][0] + self.nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(-angles[j][1]) * self.l2,
                self.l2 * np.sin(-angles[j][1])
            ] for j in range(6)
        ])
        
        P3 = P1 + np.array([
            [
                np.cos(angles[j][0] + self.nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(self.staly_kat_przy_P1 - angles[j][1]) * np.sqrt(self.h2**2 + self.l2**2),
                np.sin(angles[j][0] + self.nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(self.staly_kat_przy_P1 - angles[j][1]) * np.sqrt(self.h2**2 + self.l2**2),
                np.sin(self.staly_kat_przy_P1 - angles[j][1]) * np.sqrt(self.h2**2 + self.l2**2)
            ] for j in range(6)
        ])
        
        foot = P3 + np.array([
            [
                np.cos(angles[j][0] + self.nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(-angles[j][1] - angles[j][2]) * self.l3,
                np.sin(angles[j][0] + self.nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(-angles[j][1] - angles[j][2]) * self.l3,
                np.sin(-angles[j][1] - angles[j][2]) * self.l3
            ] for j in range(6)
        ])
        
        return P0_pod_tab, P1, P2, P3, foot

    def on_key_press(self, event):
        """Handle keyboard input"""
        direction_map = {
            'up': self.FORWARD,
            'down': self.BACKWARD, 
            'right': self.RIGHT,
            'left': self.LEFT,
            'space': self.STOP
        }
        
        gait_map = {
            't': self.TRI_GATE,
            'b': self.BI_GATE
        }
        
        if event.key in direction_map:
            new_direction = direction_map[event.key]
            
            # Ignore if same direction is already active
            if new_direction == self.current_direction and self.current_phase in ["main_loop", "startup"]:
                return
                
            self.requested_direction = new_direction
            self.transition_pending = True
            
            direction_names = {
                self.FORWARD: "forward", 
                self.BACKWARD: "backward",
                self.RIGHT: "right", 
                self.LEFT: "left",
                self.STOP: "stop"
            }
            print(f"Direction change requested: {direction_names[new_direction]}")
            
        elif event.key in gait_map:
            new_gait = gait_map[event.key]
            
            # Ignore if same gait is already active
            if new_gait == self.current_gait:
                return
                
            self.requested_gait = new_gait
            self.gait_change_pending = True
            
            gait_names = {
                self.TRI_GATE: "tri-gate",
                self.BI_GATE: "bi-gate"
            }
            print(f"Gait change requested: {gait_names[new_gait]}")

    def update_animation_queue(self):
        """Update animation queue based on current state"""
        # Handle gait changes with priority
        if self.gait_change_pending and self.current_phase != "stopped":
            # Force stop to change gait
            self.requested_direction = self.STOP
            self.transition_pending = True
            
        if self.current_phase == "stopped":
            if self.gait_change_pending:
                # Change gait while stopped
                old_gait = self.current_gait
                self.current_gait = self.requested_gait
                self.requested_gait = old_gait  # Reset
                self.gait_change_pending = False
                
                gait_names = {
                    self.TRI_GATE: "TRI-GATE",
                    self.BI_GATE: "BI-GATE"
                }
                print(f"Gait changed to: {gait_names[self.current_gait]}")
                
            if self.requested_direction != self.STOP:
                # Start moving in requested direction
                old_direction = self.current_direction
                self.current_direction = self.requested_direction
                self.requested_direction = self.STOP
                self.transition_pending = False
                self.current_phase = "startup"
                self.animation_queue.clear()
                
                # Add startup sequence for NEW direction
                startup_traj = self.generate_trajectory_sequence(self.current_direction, "startup")
                for frame in range(startup_traj.shape[1]):
                    self.animation_queue.append(('startup', frame, startup_traj[:, frame]))
                    
                gait_name = "TRI-GATE" if self.current_gait == self.TRI_GATE else "BI-GATE"
                print(f"Starting {gait_name} movement from {old_direction} to direction: {self.current_direction}")
                
        elif self.current_phase == "startup":
            if len(self.animation_queue) == 0:
                # Startup finished, begin infinite main loop
                self.current_phase = "main_loop"
                self.main_loop_counter = 0
                # Add one main loop cycle
                main_loop_traj = self.generate_trajectory_sequence(self.current_direction, "main_loop")
                for frame in range(main_loop_traj.shape[1]):
                    self.animation_queue.append(('main_loop', frame, main_loop_traj[:, frame]))
                    
                gait_name = "TRI-GATE" if self.current_gait == self.TRI_GATE else "BI-GATE"
                print(f"Entering {gait_name} main loop for direction: {self.current_direction}")
                
        elif self.current_phase == "main_loop":
            if len(self.animation_queue) == 0:
                # Main loop cycle completed
                self.main_loop_counter += 1
                
                if self.transition_pending or self.gait_change_pending:
                    # Direction change, stop, or gait change requested - begin shutdown for CURRENT direction
                    self.current_phase = "shutdown"
                    # Use CURRENT direction for shutdown (the one that's ending)
                    shutdown_traj = self.generate_trajectory_sequence(self.current_direction, "shutdown")
                    for frame in range(shutdown_traj.shape[1]):
                        self.animation_queue.append(('shutdown', frame, shutdown_traj[:, frame]))
                        
                    gait_name = "TRI-GATE" if self.current_gait == self.TRI_GATE else "BI-GATE"
                    transition_info = f"to: {self.requested_direction}" if self.transition_pending else "for gait change"
                    print(f"{gait_name} main loop cycle {self.main_loop_counter} completed, beginning shutdown from CURRENT direction: {self.current_direction}, transitioning {transition_info}")
                else:
                    # Continue main loop - add another cycle
                    main_loop_traj = self.generate_trajectory_sequence(self.current_direction, "main_loop")
                    for frame in range(main_loop_traj.shape[1]):
                        self.animation_queue.append(('main_loop', frame, main_loop_traj[:, frame]))
                    if self.main_loop_counter % 5 == 0:  # Print every 5 cycles to avoid spam
                        gait_name = "TRI-GATE" if self.current_gait == self.TRI_GATE else "BI-GATE"
                        print(f"Continuing {gait_name} main loop, cycle: {self.main_loop_counter}")
                    
        elif self.current_phase == "shutdown":
            if len(self.animation_queue) == 0:
                if self.requested_direction == self.STOP or self.gait_change_pending:
                    # Stop requested or gait change - return to stopped state
                    old_direction = self.current_direction
                    old_gait = "TRI-GATE" if self.current_gait == self.TRI_GATE else "BI-GATE"
                    self.current_direction = self.STOP
                    self.current_phase = "stopped"
                    self.transition_pending = False
                    print(f"{old_gait} hexapod stopped (was moving: {old_direction})")
                elif self.transition_pending and self.requested_direction != self.STOP:
                    # Start new direction
                    old_direction = self.current_direction
                    self.current_direction = self.requested_direction  # CHANGE DIRECTION HERE
                    self.requested_direction = self.STOP
                    self.transition_pending = False
                    self.current_phase = "startup"
                    
                    # Add startup for NEW direction
                    startup_traj = self.generate_trajectory_sequence(self.current_direction, "startup")
                    for frame in range(startup_traj.shape[1]):
                        self.animation_queue.append(('startup', frame, startup_traj[:, frame]))
                        
                    gait_name = "TRI-GATE" if self.current_gait == self.TRI_GATE else "BI-GATE"
                    print(f"{gait_name} transition complete: shutdown({old_direction}) -> startup({self.current_direction})")
                else:
                    # Fallback to stopped state
                    old_direction = self.current_direction
                    old_gait = "TRI-GATE" if self.current_gait == self.TRI_GATE else "BI-GATE"
                    self.current_direction = self.STOP
                    self.current_phase = "stopped" 
                    self.transition_pending = False
                    print(f"{old_gait} hexapod stopped (fallback, was: {old_direction})")

    def get_current_angles(self):
        """Get current servo angles for animation"""
        if len(self.animation_queue) > 0:
            _, _, angles = self.animation_queue.popleft()
            return angles
        else:
            self.update_animation_queue()
            if len(self.animation_queue) > 0:
                _, _, angles = self.animation_queue.popleft()
                return angles
            else:
                # Return rest position
                return self.rest_angles[:, 0]

def update_animation(frame, hexapod, lines, status_text):
    """Animation update function"""
    current_angles = hexapod.get_current_angles()
    P0_pod_tab, P1, P2, P3, foot = hexapod.calculate_positions_from_angles(current_angles)
    
    # Update status text
    direction_names = {
        hexapod.FORWARD: "FORWARD", 
        hexapod.BACKWARD: "BACKWARD",
        hexapod.RIGHT: "RIGHT", 
        hexapod.LEFT: "LEFT",
        hexapod.STOP: "STOPPED"
    }
    
    gait_names = {
        hexapod.TRI_GATE: "TRI-GATE",
        hexapod.BI_GATE: "BI-GATE"
    }
    
    current_dir = direction_names.get(hexapod.current_direction, "UNKNOWN")
    requested_dir = direction_names.get(hexapod.requested_direction, "NONE") if hexapod.requested_direction != hexapod.STOP else "NONE"
    current_gait_name = gait_names.get(hexapod.current_gait, "UNKNOWN")
    requested_gait_name = gait_names.get(hexapod.requested_gait, "NONE") if hexapod.gait_change_pending else "NONE"
    
    phase_name = hexapod.current_phase.upper()
    transition_status = "TRANSITION PENDING" if hexapod.transition_pending else "STABLE"
    gait_status = "GAIT CHANGE PENDING" if hexapod.gait_change_pending else "STABLE"
    
    # Show different leg groupings for each gait
    if hexapod.current_gait == hexapod.TRI_GATE:
        leg_grouping = "Legs: (1,3,5) & (2,4,6)"
    else:
        leg_grouping = "Legs: (1,4) & (2,5) & (3,6)"
    
    status_info = f"""COMBINED HEXAPOD STATUS
Current Gait: {current_gait_name}
{leg_grouping}
Current Direction: {current_dir}
Phase: {phase_name}
Main Loop Cycle: {hexapod.main_loop_counter}
Requested Direction: {requested_dir}
Requested Gait: {requested_gait_name}
Direction Status: {transition_status}
Gait Status: {gait_status}
Queue Length: {len(hexapod.animation_queue)}"""
    
    status_text.set_text(status_info)
    
    for j in range(6):
        # 0. Attachment -> P0_pod
        lines[j][0].set_data([hexapod.przyczepy_nog_do_tulowia[j][0], P0_pod_tab[j][0]],
                             [hexapod.przyczepy_nog_do_tulowia[j][1], P0_pod_tab[j][1]])
        lines[j][0].set_3d_properties([hexapod.przyczepy_nog_do_tulowia[j][2], P0_pod_tab[j][2]])

        # 1. P0_pod -> P1
        lines[j][1].set_data([P0_pod_tab[j][0], P1[j][0]],
                             [P0_pod_tab[j][1], P1[j][1]])
        lines[j][1].set_3d_properties([P0_pod_tab[j][2], P1[j][2]])

        # 2. P1 -> P2
        lines[j][2].set_data([P1[j][0], P2[j][0]],
                             [P1[j][1], P2[j][1]])
        lines[j][2].set_3d_properties([P1[j][2], P2[j][2]])

        # 3. P2 -> P3
        lines[j][3].set_data([P2[j][0], P3[j][0]],
                             [P2[j][1], P3[j][1]])
        lines[j][3].set_3d_properties([P2[j][2], P3[j][2]])

        # 4. P3 -> foot
        lines[j][4].set_data([P3[j][0], foot[j][0]],
                             [P3[j][1], foot[j][1]])
        lines[j][4].set_3d_properties([P3[j][2], foot[j][2]])

    return [segment for leg in lines for segment in leg] + [status_text]

# Main execution
def main():
    # Create combined hexapod controller
    hexapod = CombinedHexapodController()
    
    # Setup plot
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim([-0.5, 0.5])
    ax.set_ylim([-0.5, 0.5])
    ax.set_zlim([-0.5, 0.5])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Combined Tri-Gate & Bi-Gate Hexapod Simulation\nArrows: Move | SPACE: Stop | T: Tri-Gate | B: Bi-Gate')
    
    # Add status text display
    status_text = ax.text2D(0.02, 0.98, "", transform=ax.transAxes, 
                           verticalalignment='top', fontfamily='monospace', 
                           fontsize=9, bbox=dict(boxstyle="round,pad=0.3", 
                           facecolor="lightyellow", alpha=0.9))
    
    # Setup lines for visualization
    segment_colors = ['purple', 'r', 'b', 'orange', 'g']
    lines = [[ax.plot([], [], [], color=segment_colors[i], marker='o', markersize=3)[0] for i in range(5)] for _ in range(6)]
    
    # Connect keyboard event
    fig.canvas.mpl_connect('key_press_event', hexapod.on_key_press)
    
    # Create and start animation
    ani = animation.FuncAnimation(
        fig, update_animation, 
        fargs=(hexapod, lines, status_text),
        interval=50, 
        blit=False, 
        cache_frame_data=False
    )
    
    # Show plot
    plt.tight_layout()
    plt.show()
    
    return ani

if __name__ == "__main__":
    ani = main()
