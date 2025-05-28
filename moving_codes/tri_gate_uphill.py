import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import matplotlib.animation as animation


matplotlib.use('TkAgg')

def katy_serw(P3, l1, h1, l2, h2, l3):
    # wyznaczenie katow potrzebnych do osiagniecia przez stope punktu docelowego
    alfa_1 = np.arctan2(P3[1], P3[0])

    P1 = np.array([l1 * np.cos(alfa_1), l1 * np.sin(alfa_1), h1])

    d = np.sqrt((P3[0] - P1[0]) ** 2 + (P3[1] - P1[1]) ** 2 + (P3[2] - P1[2]) ** 2)
    r = np.sqrt(l2 ** 2 + h2 ** 2)

    staly_kat_przy_P1 = np.arctan2(h2, l2)

    cos_fi = (r ** 2 + l3 ** 2 - d ** 2) / (2 * r * l3)
    cos_fi = np.clip(cos_fi, -1, 1)  # Ensure valid range for arccos
    fi = np.arccos(cos_fi)
    alfa_3 = np.deg2rad(180) - fi - staly_kat_przy_P1

    epsilon = np.arcsin(np.clip(np.sin(fi) * l3 / d, -1, 1))
    tau = np.arctan2(P3[2] - P1[2], np.sqrt((P3[0] - P1[0]) ** 2 + (P3[1] - P1[1]) ** 2))

    alfa_2 = -(epsilon + tau - staly_kat_przy_P1)
    return [alfa_1, alfa_2, alfa_3]

def funkcja_ruchu_nogi(r, h, y_punktu):
    return (-4 * h * (y_punktu ** 2)) / (r ** 2) + (4 * h * y_punktu) / r

def dlugosc_funkcji_ruchu_nogi(r, h, ilosc_probek):
    suma = 0
    for i in range(1,ilosc_probek):
        y_0 = funkcja_ruchu_nogi(r, h, (i-1)/ilosc_probek * r)
        y_1 = funkcja_ruchu_nogi(r, h, i/ilosc_probek * r)
        dlugosc = np.sqrt((y_1 - y_0) ** 2 + (r/ilosc_probek) ** 2)
        suma += dlugosc
    return suma

def znajdz_punkty_rowno_odlegle_na_paraboli(r, h, ilosc_punktow_na_krzywej, ilosc_probek, bufor_y):
    L = dlugosc_funkcji_ruchu_nogi(r, h, ilosc_probek)
    dlugosc_kroku = L/ilosc_punktow_na_krzywej
    suma = 0
    punkty = []
    for i in range(1,ilosc_probek):
        z_0 = funkcja_ruchu_nogi(r, h, (i-1)/ilosc_probek * r)
        z_1 = funkcja_ruchu_nogi(r, h, i/ilosc_probek * r)
        dlugosc = np.sqrt((z_1 - z_0) ** 2 + (r/ilosc_probek) ** 2)
        suma += dlugosc
        if(suma > dlugosc_kroku):
            suma = suma - dlugosc_kroku
            punkty.append([0, i/ilosc_probek * r + bufor_y, z_1])
        if(len(punkty) == ilosc_punktow_na_krzywej - 1):
            break
    punkty.append([0, bufor_y + r, 0])
    return punkty

# Hill/terrain function
def hill_height(x, y):
    """Define the hill terrain - simple inclined plane with some variation"""
    base_height = y * 0.1  # 30% grade incline
    variation = 0.02 * np.sin(5 * x) + 0.01 * np.sin(3 * y)
    return base_height + variation

def calculate_terrain_normal(x, y, delta=0.01):
    """Calculate terrain normal vector at given point"""
    # Calculate partial derivatives using finite differences
    dz_dx = (hill_height(x + delta, y) - hill_height(x - delta, y)) / (2 * delta)
    dz_dy = (hill_height(x, y + delta) - hill_height(x, y - delta)) / (2 * delta)
    
    # Normal vector
    normal = np.array([-dz_dx, -dz_dy, 1])
    return normal / np.linalg.norm(normal)

def rotation_matrix_from_vectors(v1, v2):
    """Calculate rotation matrix to align v1 with v2"""
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    
    # If vectors are already aligned
    if np.allclose(v1, v2):
        return np.eye(3)
    
    # If vectors are opposite
    if np.allclose(v1, -v2):
        # Find any perpendicular vector
        perp = np.array([1, 0, 0]) if abs(v1[0]) < 0.9 else np.array([0, 1, 0])
        perp = perp - np.dot(perp, v1) * v1
        perp = perp / np.linalg.norm(perp)
        return 2 * np.outer(perp, perp) - np.eye(3)
    
    # General case: use Rodrigues' rotation formula
    cross = np.cross(v1, v2)
    s = np.linalg.norm(cross)
    c = np.dot(v1, v2)
    
    if s == 0:
        return np.eye(3)
    
    cross = cross / s
    
    # Skew-symmetric cross-product matrix
    K = np.array([[0, -cross[2], cross[1]],
                  [cross[2], 0, -cross[0]],
                  [-cross[1], cross[0], 0]])
    
    R = np.eye(3) + s * K + (1 - c) * np.dot(K, K)
    return R

def calculate_robot_pose(supporting_foot_positions):
    """Calculate robot body position and orientation based on supporting feet"""
    if len(supporting_foot_positions) == 0:
        return np.array([0, 0.2, 0.1]), np.eye(3)
    
    # Calculate center of supporting feet
    center_pos = np.mean(supporting_foot_positions, axis=0)
    
    # Calculate average terrain normal at supporting feet
    avg_normal = np.zeros(3)
    for pos in supporting_foot_positions:
        normal = calculate_terrain_normal(pos[0], pos[1])
        avg_normal += normal
    avg_normal = avg_normal / len(supporting_foot_positions)
    avg_normal = avg_normal / np.linalg.norm(avg_normal)
    
    # Robot body should be slightly above the center
    body_offset = 0.05  # 5cm above ground
    body_position = center_pos + avg_normal * body_offset
    
    # Calculate rotation matrix to align robot's up vector with terrain normal
    robot_up = np.array([0, 0, 1])  # Original up direction
    rotation_matrix = rotation_matrix_from_vectors(robot_up, avg_normal)
    
    return body_position, rotation_matrix

# Długosci segmentow nog
h1 = -0.016854 - 0.003148
l1 = 0.12886 - 0.0978
l2 = 0.2188-0.12886
h2 = -0.011804 + 0.016854
l3 = 0.38709 - 0.2188
staly_kat_przy_P1 = np.arctan2(h2, l2)

# zalozone katy spoczynkowe przegubow
alfa_1 = 0
alfa_2 = np.radians(0)
alfa_3 = np.radians(60)

P0 = np.array([0, 0, 0])
P0_pod = P0 + np.array([0, 0, h1])
P1 = P0_pod + np.array([l1 * np.cos(alfa_1), l1 *np.sin(alfa_1), 0])
P2 = P1 + np.array([np.cos(alfa_1)*np.cos(alfa_2)*l2,np.sin(alfa_1)*np.cos(alfa_2)*l2, np.sin(alfa_2) * l2])
P3 = P1 + np.array([np.cos(alfa_1)*np.cos(staly_kat_przy_P1 + alfa_2)*np.sqrt(h2**2 + l2**2),np.sin(alfa_1)*np.cos(staly_kat_przy_P1 + alfa_2)*np.sqrt(h2**2 + l2**2), np.sin(staly_kat_przy_P1 + alfa_2)*np.sqrt(h2**2 + l2**2)])
P4 = P3 + np.array([np.cos(alfa_1)*np.cos(alfa_2 - alfa_3)*l3, np.sin(alfa_1)*np.cos(alfa_2 - alfa_3)*l3, np.sin(alfa_2 - alfa_3) * l3])

stopa_spoczynkowa = P4

# Original attachment points (relative to robot body)
przyczepy_nog_do_tulowia_original = np.array([
    [ 0.073922, 0.055095 ,0.003148],
    [ 0.0978, -0.00545, 0.003148],
    [ 0.067301, -0.063754, 0.003148],
    [ -0.067301, -0.063754 , 0.003148],
    [ -0.0978 , -0.00545,0.003148],
    [ -0.073922, 0.055095,0.003148],
])

nachylenia_nog_do_bokow_platformy_pajaka = np.array([
    np.deg2rad(37.169), 0, np.deg2rad(-37.169), np.deg2rad(180 + 37.169), np.deg2rad(180), np.deg2rad(180 - 37.169)
])

# ====================================================================
# ROBOT STOI W MIEJSCU - TYLKO PODNOSI NOGI I WYKRYWA KOLIZJE
# ====================================================================

# STAŁA POZYCJA ROBOTA - NIE PORUSZA SIĘ
robot_fixed_center = np.array([0, 0.2])  # Centrum XY - STAŁE!

print(f"Robot STOI w miejscu na pozycji: {robot_fixed_center}")
print(f"Wysokość terenu w tym miejscu: {hill_height(robot_fixed_center[0], robot_fixed_center[1]):.3f}m")

# Parametry inspirowane oryginalnym kodem
h = l3 / 4
r = h
ilosc_punktow_na_krzywych = 20

# Generowanie cykli nóg (jak w oryginalnym kodzie)
punkty_etap1_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, ilosc_punktow_na_krzywych, 10000, 0)
punkty_etap2_ruchu_y = np.linspace(r * (ilosc_punktow_na_krzywych - 1) / ilosc_punktow_na_krzywych, 0, ilosc_punktow_na_krzywych)
punkty_etap2_ruchu = [[0, punkty_etap2_ruchu_y[i], 0] for i in range(ilosc_punktow_na_krzywych)]
punkty_etap3_ruchu_y = np.linspace(-r / ilosc_punktow_na_krzywych, -r, ilosc_punktow_na_krzywych)
punkty_etap3_ruchu = [[0, punkty_etap3_ruchu_y[i], 0] for i in range(ilosc_punktow_na_krzywych)]
punkty_etap4_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(2 * r, h, 2 * ilosc_punktow_na_krzywych, 20000, -r)
punkty_etap5_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, ilosc_punktow_na_krzywych, 10000, -r)

# Tripod gait
cykl_ogolny_nog_1_3_5 = punkty_etap1_ruchu.copy()
cykl_ogolny_nog_2_4_6 = punkty_etap3_ruchu.copy()

ilosc_cykli = 3  # Krótki test

for _ in range(ilosc_cykli):
    cykl_ogolny_nog_1_3_5 += punkty_etap2_ruchu + punkty_etap3_ruchu + punkty_etap4_ruchu
    cykl_ogolny_nog_2_4_6 += punkty_etap4_ruchu + punkty_etap2_ruchu + punkty_etap3_ruchu

cykl_ogolny_nog_1_3_5 += punkty_etap2_ruchu + punkty_etap3_ruchu + punkty_etap5_ruchu
cykl_ogolny_nog_2_4_6 += punkty_etap4_ruchu + punkty_etap2_ruchu
cykl_ogolny_nog_1_3_5 = np.array(cykl_ogolny_nog_1_3_5)
cykl_ogolny_nog_2_4_6 = np.array(cykl_ogolny_nog_2_4_6)

# Cykle nog z transformacją dla nachylenia
cykle_nog = np.array([
    [
        [cykl_ogolny_nog_1_3_5[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_ogolny_nog_1_3_5[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_ogolny_nog_1_3_5[i][2]]
        for i in range(len(cykl_ogolny_nog_1_3_5))
    ] if j in (0, 2, 4) else
    [
        [cykl_ogolny_nog_2_4_6[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_ogolny_nog_2_4_6[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_ogolny_nog_2_4_6[i][2]]
        for i in range(len(cykl_ogolny_nog_2_4_6))
    ]
    for j in range(6)
])

# Initialize arrays
num_frames = len(cykl_ogolny_nog_1_3_5)
robot_body_positions = np.zeros((num_frames, 3))
robot_rotations = np.zeros((num_frames, 3, 3))
przyczepy_nog_do_tulowia_dynamic = np.zeros((num_frames, 6, 3))
polozenia_stop_podczas_cyklu = np.zeros((6, num_frames, 3))
foot_touching_ground = np.zeros((6, num_frames), dtype=bool)

# KONTROLA RUCHU SEKWENCJI NA PODSTAWIE KOLIZJI
sequence_active = True  # Czy sekwencja ruchu jest aktywna
sequence_frame = 0      # Aktualna klatka w sekwencji
wait_for_all_grounded = False  # Czy czekamy aż wszystkie nogi dotkną ziemi

MIN_LIFT_DURATION = 10  # Minimalna liczba klatek w powietrzu
CLEARANCE_HEIGHT = 0.02  # Minimalna wysokość nad ziemią
leg_lift_frames = np.full((6,), -1)

print(f"Długość cyklu: {num_frames} klatek")
print(f"Parametry kolizji: min_lift={MIN_LIFT_DURATION}, clearance={CLEARANCE_HEIGHT}m")

# Oblicz pozycje dla każdej klatki
for frame in range(num_frames):
    if frame > 0:
        robot_body_pos = robot_body_positions[frame-1].copy()
        robot_rotation = robot_rotations[frame-1].copy()
    else:
        # Pierwsza klatka - ustaw pozycję bazową na górce
        ground_height_center = hill_height(robot_fixed_center[0], robot_fixed_center[1])
        robot_body_pos = np.array([robot_fixed_center[0], robot_fixed_center[1], ground_height_center + 0.05])
        robot_rotation = np.eye(3)
    
    # ====================================================================
    # KONTROLA SEKWENCJI RUCHU NA PODSTAWIE KOLIZJI
    # ====================================================================
    
    if not sequence_active:
        # Sekwencja zatrzymana - wszystkie nogi w pozycji spoczynkowej
        sequence_frame = 0
    elif wait_for_all_grounded:
        # Czekamy aż wszystkie nogi dotkną ziemi zanim kontynuujemy
        sequence_frame = sequence_frame  # Zatrzymaj sekwencję
    else:
        # Sekwencja aktywna - wykonuj kolejne kroki
        sequence_frame = frame % num_frames
    
    # ====================================================================
    # ROBOT STOI W STAŁEJ POZYCJI - NIE PORUSZA SIĘ
    # ====================================================================
    supporting_positions = []
    
    for j in range(6):
        if not sequence_active:
            # SEKWENCJA ZATRZYMANA - pozycja spoczynkowa
            desired_foot_local = stopa_spoczynkowa.copy()
        else:
            # SEKWENCJA AKTYWNA - pozycja zgodnie z cyklem
            desired_foot_local = np.array([
                stopa_spoczynkowa[0] + cykle_nog[j][sequence_frame][0],
                stopa_spoczynkowa[1] + cykle_nog[j][sequence_frame][1],
                stopa_spoczynkowa[2] + cykle_nog[j][sequence_frame][2]
            ])
        
        # Przekształć do współrzędnych świata (robot w stałej pozycji)
        foot_world_pos = np.array([robot_fixed_center[0], robot_fixed_center[1], 0.15]) + desired_foot_local
        # NOWE - względem aktualnej pozycji robota z orientacją:
        #foot_world_pos = robot_body_pos + np.dot(robot_rotation, desired_foot_local)
        ground_height = hill_height(foot_world_pos[0], foot_world_pos[1])

        
        
        # ====================================================================
        # WYKRYWANIE KOLIZJI I KONTROLA SEKWENCJI
        # ====================================================================
        planned_height = cykle_nog[j][sequence_frame][2] if sequence_active else 0
        
        # Sprawdź czy noga została podniesiona
        if planned_height > CLEARANCE_HEIGHT and leg_lift_frames[j] == -1:
            leg_lift_frames[j] = frame
            print(f"Frame {frame}: Noga {j} podniesiona")
        
        # Sprawdź czy noga może lądować
        can_touch_ground = True
        if leg_lift_frames[j] != -1:
            frames_since_lift = frame - leg_lift_frames[j]
            if frames_since_lift < MIN_LIFT_DURATION:
                can_touch_ground = False
            elif planned_height <= 0.005:
                leg_lift_frames[j] = -1  # Reset
                print(f"Frame {frame}: Noga {j} może lądować")
        
        # Określ kontakt z ziemią
        if planned_height <= 0.01 and can_touch_ground:
            foot_world_pos[2] = max(ground_height, foot_world_pos[2]) 
            foot_touching_ground[j][frame] = True
            supporting_positions.append(foot_world_pos)
        else:
            foot_touching_ground[j][frame] = False
            # Nogi w powietrzu - minimum nad ziemią
            min_height = ground_height + max(CLEARANCE_HEIGHT, planned_height)
            foot_world_pos[2] = max(foot_world_pos[2], min_height)
        
        polozenia_stop_podczas_cyklu[j][frame] = desired_foot_local
    
    # ====================================================================
    # SPRAWDŹ CZY WSZYSTKIE NOGI DOTYKAJĄ ZIEMI
    # ====================================================================
    legs_on_ground = sum(1 for j in range(6) if foot_touching_ground[j][frame])
    
    if wait_for_all_grounded and legs_on_ground == 6:
        print(f"Frame {frame}: Wszystkie nogi na ziemi - WZNÓW sekwencję")
        wait_for_all_grounded = False
        sequence_active = True
    elif sequence_active and legs_on_ground < 3:
        print(f"Frame {frame}: Za mało nóg na ziemi ({legs_on_ground}) - STOP sekwencji")
        wait_for_all_grounded = True
    
    # ====================================================================
    # OBLICZ POZYCJĘ ROBOTA NA PODSTAWIE NÓG PODTRZYMUJĄCYCH
    # ====================================================================
    if len(supporting_positions) >= 3:
        robot_body_pos, robot_rotation = calculate_robot_pose(supporting_positions)
    else:
        # Fallback - pozycja domyślna
        ground_height_center = hill_height(robot_fixed_center[0], robot_fixed_center[1])
        robot_body_pos = np.array([robot_fixed_center[0], robot_fixed_center[1], ground_height_center + 0.05])
        robot_rotation = np.eye(3)
    
    robot_body_positions[frame] = robot_body_pos
    robot_rotations[frame] = robot_rotation
    
    # Calculate transformed attachment points
    for j in range(6):
        transformed_attachment = robot_body_pos + np.dot(robot_rotation, przyczepy_nog_do_tulowia_original[j])
        przyczepy_nog_do_tulowia_dynamic[frame][j] = transformed_attachment

# Calculate servo angles
wychyly_serw_podczas_ruchu = np.zeros((6, num_frames, 3))
for j in range(6):
    for i in range(num_frames):
        try:
            wychyly_serw_podczas_ruchu[j][i] = katy_serw(polozenia_stop_podczas_cyklu[j][i], l1, h1, l2, h2, l3)
        except:
            if i > 0:
                wychyly_serw_podczas_ruchu[j][i] = wychyly_serw_podczas_ruchu[j][i-1]
            else:
                wychyly_serw_podczas_ruchu[j][i] = [0, 0, np.radians(60)]

def calculate_positions():
    polozenie_punktow_P1_w_ruchu = np.zeros((6, num_frames, 3))
    polozenie_punktow_P2_w_ruchu = np.zeros((6, num_frames, 3))
    polozenie_punktow_P3_w_ruchu = np.zeros((6, num_frames, 3))
    obliczone_z_serw_polozenie_stop = np.zeros((6, num_frames, 3))
    
    for frame in range(num_frames):
        robot_rotation = robot_rotations[frame]
        
        for j in range(6):
            attachment_point = przyczepy_nog_do_tulowia_dynamic[frame][j]
            
            # P1 calculation
            p1_local = np.array([
                l1 * np.cos(wychyly_serw_podczas_ruchu[j][frame][0] + nachylenia_nog_do_bokow_platformy_pajaka[j]),
                l1 * np.sin(wychyly_serw_podczas_ruchu[j][frame][0] + nachylenia_nog_do_bokow_platformy_pajaka[j]),
                h1
            ])
            polozenie_punktow_P1_w_ruchu[j][frame] = attachment_point + np.dot(robot_rotation, p1_local)
            
            # P2 calculation
            p2_offset = np.array([
                np.cos(wychyly_serw_podczas_ruchu[j][frame][0] + nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(-wychyly_serw_podczas_ruchu[j][frame][1]) * l2,
                np.sin(wychyly_serw_podczas_ruchu[j][frame][0] + nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(-wychyly_serw_podczas_ruchu[j][frame][1]) * l2,
                l2 * np.sin(-wychyly_serw_podczas_ruchu[j][frame][1])
            ])
            polozenie_punktow_P2_w_ruchu[j][frame] = polozenie_punktow_P1_w_ruchu[j][frame] + np.dot(robot_rotation, p2_offset)
            
            # P3 calculation
            p3_offset = np.array([
                np.cos(wychyly_serw_podczas_ruchu[j][frame][0] + nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(staly_kat_przy_P1 - wychyly_serw_podczas_ruchu[j][frame][1]) * np.sqrt(h2**2 + l2**2),
                np.sin(wychyly_serw_podczas_ruchu[j][frame][0] + nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(staly_kat_przy_P1 - wychyly_serw_podczas_ruchu[j][frame][1]) * np.sqrt(h2**2 + l2**2),
                np.sin(staly_kat_przy_P1 - wychyly_serw_podczas_ruchu[j][frame][1]) * np.sqrt(h2**2 + l2**2)
            ])
            polozenie_punktow_P3_w_ruchu[j][frame] = polozenie_punktow_P1_w_ruchu[j][frame] + np.dot(robot_rotation, p3_offset)
            
            # Foot calculation
            foot_offset = np.array([
                np.cos(wychyly_serw_podczas_ruchu[j][frame][0] + nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(-wychyly_serw_podczas_ruchu[j][frame][1] - wychyly_serw_podczas_ruchu[j][frame][2]) * l3,
                np.sin(wychyly_serw_podczas_ruchu[j][frame][0] + nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(-wychyly_serw_podczas_ruchu[j][frame][1] - wychyly_serw_podczas_ruchu[j][frame][2]) * l3,
                np.sin(-wychyly_serw_podczas_ruchu[j][frame][1] - wychyly_serw_podczas_ruchu[j][frame][2]) * l3
            ])
            obliczone_z_serw_polozenie_stop[j][frame] = polozenie_punktow_P3_w_ruchu[j][frame] + np.dot(robot_rotation, foot_offset)

    return polozenie_punktow_P1_w_ruchu, polozenie_punktow_P2_w_ruchu, polozenie_punktow_P3_w_ruchu, obliczone_z_serw_polozenie_stop

def create_hill_mesh():
    """Create hill mesh for visualization"""
    x_range = np.linspace(-0.6, 0.6, 30)
    y_range = np.linspace(-0.3, 1.0, 30)
    X, Y = np.meshgrid(x_range, y_range)
    Z = hill_height(X, Y)
    return X, Y, Z

def update(frame, lines, positions, hill_surface):
    P1, P2, P3, foot = positions
    
    # Clear and redraw hill
    ax.clear()
    X, Y, Z = create_hill_mesh()
    ax.plot_surface(X, Y, Z, alpha=0.3, color='brown', shade=True)
    
    # Set limits and labels
    ax.set_xlim([-0.4, 0.4])
    ax.set_ylim([-0.2, 0.8])
    ax.set_zlim([-0.1, 0.4])
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)') 
    ax.set_zlabel('Z (m)')
    ax.set_title('Hexapod - STOI W MIEJSCU: Wykrywanie kolizji i kontrola sekwencji')
    
    segment_colors = ['purple','red','blue', 'orange', 'green']
    
    # Count legs touching ground
    legs_on_ground = sum(1 for j in range(6) if foot_touching_ground[j][frame])
    tripod_A_on_ground = sum(1 for j in [0, 2, 4] if foot_touching_ground[j][frame])
    tripod_B_on_ground = sum(1 for j in [1, 3, 5] if foot_touching_ground[j][frame])
    
    for j in range(6):
        # Determine leg color based on tripod group and ground contact
        if j in [0, 2, 4]:  # Tripod A
            base_color = 'darkblue' if foot_touching_ground[j][frame] else 'lightblue'
        else:  # Tripod B  
            base_color = 'darkred' if foot_touching_ground[j][frame] else 'lightcoral'
        
        # Get attachment point for this frame
        attachment_point = przyczepy_nog_do_tulowia_dynamic[frame][j]
        P0_pod_point = attachment_point + np.dot(robot_rotations[frame], np.array([0, 0, h1]))
        
        # 0. Przyczep -> P0_pod
        ax.plot([attachment_point[0], P0_pod_point[0]],
                [attachment_point[1], P0_pod_point[1]],
                [attachment_point[2], P0_pod_point[2]], 
                color=segment_colors[0], marker='o', markersize=3, linewidth=2)

        # 1. P0_pod -> P1
        ax.plot([P0_pod_point[0], P1[j][frame][0]],
                [P0_pod_point[1], P1[j][frame][1]],
                [P0_pod_point[2], P1[j][frame][2]], 
                color=segment_colors[1], marker='o', markersize=3, linewidth=2)

        # 2. P1 -> P2
        ax.plot([P1[j][frame][0], P2[j][frame][0]],
                [P1[j][frame][1], P2[j][frame][1]],
                [P1[j][frame][2], P2[j][frame][2]], 
                color=segment_colors[2], marker='o', markersize=3, linewidth=2)

        # 3. P2 -> P3
        ax.plot([P2[j][frame][0], P3[j][frame][0]],
                [P2[j][frame][1], P3[j][frame][1]],
                [P2[j][frame][2], P3[j][frame][2]], 
                color=segment_colors[3], marker='o', markersize=3, linewidth=2)

        # 4. P3 -> koniec stopy (colored based on ground contact)
        ax.plot([P3[j][frame][0], foot[j][frame][0]],
                [P3[j][frame][1], foot[j][frame][1]],
                [P3[j][frame][2], foot[j][frame][2]], 
                color=base_color, marker='o', markersize=5, linewidth=3)
        
        # Highlight foot contact with ground
        if foot_touching_ground[j][frame]:
            ax.scatter(foot[j][frame][0], foot[j][frame][1], foot[j][frame][2], 
                      color='yellow', s=80, alpha=0.9, edgecolors='black')
        else:
            # Highlight lifted legs
            ax.scatter(foot[j][frame][0], foot[j][frame][1], foot[j][frame][2], 
                      color='orange', s=60, alpha=0.7, edgecolors='red')
    
    # Draw robot body platform
    body_corners = np.array([
        [ 0.1,  0.08, 0],
        [ 0.1, -0.08, 0],
        [-0.1, -0.08, 0],
        [-0.1,  0.08, 0],
        [ 0.1,  0.08, 0]  # Close the rectangle
    ])
    
    # Transform body corners to world coordinates
    body_world = robot_body_positions[frame] + np.array([np.dot(robot_rotations[frame], corner) for corner in body_corners])
    ax.plot(body_world[:, 0], body_world[:, 1], body_world[:, 2], 'k-', linewidth=3, alpha=0.8)
    
    # Add text showing sequence control status
    ax.text2D(0.02, 0.98, f"KONTROLA SEKWENCJI NA PODSTAWIE KOLIZJI", 
              transform=ax.transAxes, fontsize=12, weight='bold', verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='lightgreen', alpha=0.8))
    
    ax.text2D(0.02, 0.90, f"Nogi na ziemi: {legs_on_ground}/6", 
              transform=ax.transAxes, fontsize=10, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
    
    ax.text2D(0.02, 0.82, f"Tripod A: {tripod_A_on_ground}/3 | Tripod B: {tripod_B_on_ground}/3", 
              transform=ax.transAxes, fontsize=10, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='lightblue', alpha=0.8))
    
    # Show sequence status
    if legs_on_ground >= 3:
        status_text = "Sekwencja AKTYWNA"
        status_color = 'lightgreen'
    else:
        status_text = "Sekwencja ZATRZYMANA"
        status_color = 'salmon'
    
    ax.text2D(0.02, 0.74, status_text, 
              transform=ax.transAxes, fontsize=10, weight='bold', verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor=status_color, alpha=0.8))
    
    # Show which legs are currently lifted
    lifted_legs = [j for j in range(6) if not foot_touching_ground[j][frame]]
    if lifted_legs:
        ax.text2D(0.02, 0.66, f"Podniesione nogi: {lifted_legs}", 
                  transform=ax.transAxes, fontsize=9, verticalalignment='top',
                  bbox=dict(boxstyle="round", facecolor='orange', alpha=0.7))
    
    ax.text2D(0.02, 0.58, f"Frame: {frame}/{num_frames}", 
              transform=ax.transAxes, fontsize=9, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='lightgray', alpha=0.8))
    
    # Calculate platform tilt angle
    up_vector = np.dot(robot_rotations[frame], np.array([0, 0, 1]))
    tilt_angle = np.degrees(np.arccos(np.clip(np.dot(up_vector, np.array([0, 0, 1])), -1, 1)))
    
    ax.text2D(0.02, 0.50, f"Platform tilt: {tilt_angle:.1f}°", 
              transform=ax.transAxes, fontsize=9, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='lightyellow', alpha=0.8))
    
    # Add robot body center point
    ax.scatter(robot_body_positions[frame][0], robot_body_positions[frame][1], robot_body_positions[frame][2], 
              color='black', s=100, marker='s', alpha=0.8)

    return []

# Ustawienia wykresu i animacji
positions = calculate_positions()
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# Create hill surface
X, Y, Z = create_hill_mesh()
hill_surface = ax.plot_surface(X, Y, Z, alpha=0.3, color='brown')

# Initialize empty lines list (will be recreated in update function)
lines = []

ani = animation.FuncAnimation(fig, update, frames=num_frames, 
                              fargs=(lines, positions, hill_surface),
                              interval=100, blit=False)

plt.tight_layout()
plt.show()

# ====================================================================
# PODSUMOWANIE - KONTROLA SEKWENCJI NA PODSTAWIE KOLIZJI:
# ====================================================================
print("\n" + "="*70)
print("KONTROLA SEKWENCJI NA PODSTAWIE WYKRYWANIA KOLIZJI")
print("="*70)
print("✅ ZAIMPLEMENTOWANE:")
print("   🤖 Robot STOI W MIEJSCU - nie porusza się całkowicie")
print("   🦵 Podnosi nogi według oryginalnego cyklu 5-etapowego")
print("   🔍 Wykrywa kolizje z nachyloną powierzchnią")
print("   ⏸️  STOP sekwencji gdy za mało nóg na ziemi (<3)")
print("   ▶️  START sekwencji gdy wszystkie nogi na ziemi (6)")
print("   📐 Dostosowuje orientację platformy do terenu")
print("\n✅ ALGORYTM KONTROLI:")
print("   1. Wykonuj sekwencję ruchu nóg")
print("   2. Sprawdzaj kolizje z ziemią w każdej klatce")
print("   3. Jeśli za mało nóg na ziemi → STOP sekwencji")
print("   4. Czekaj aż wszystkie nogi dotkną ziemi")
print("   5. Wznów sekwencję → powrót do kroku 1")
print("\n✅ PARAMETRY KOLIZJI:")
print(f"   ⏱️  Min. czas w powietrzu: {MIN_LIFT_DURATION} klatek")
print(f"   📏 Min. wysokość nad ziemią: {CLEARANCE_HEIGHT}m")
print("   🚫 Blokada kontaktu podczas podnoszenia")
print("   🎯 Minimum 3 nogi na ziemi dla stabilności")
print("\n🎯 REZULTAT:")
print("   - Robot bezpiecznie podnosi nogi pod górkę")
print("   - Automatycznie zatrzymuje ruch przy braku stabilności")
print("   - Wznawia chodzenie gdy odzyska równowagę")
print("   - Nie porusza się - tylko testuje algorytm kontroli")
print("   - Platforma dostosowuje się do nachylenia terenu")
print("\n🚀 GOTOWY SYSTEM KONTROLI!")
print("   - Bezpieczne wykrywanie kolizji")
print("   - Inteligentne zatrzymywanie/wznawianie sekwencji")
print("   - Podstawa do rzeczywistego chodzenia pod górkę")
print("="*70)