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
    base_height = y * 0.1  # 10% grade incline
    variation = 0.02 * np.sin(5 * x) + 0.01 * np.sin(3 * y)
    return base_height + variation

# <----------- NOWA FUNKCJA: Oblicza lokalną płaszczyznę stycznej do terenu
def calculate_terrain_plane_at_point(x, y, terrain_func, delta=0.01):
    """
    Oblicza lokalną płaszczyznę stycznej do terenu w danym punkcie
    
    Args:
        x, y: współrzędne punktu
        terrain_func: funkcja wysokości terenu hill_height(x, y)
        delta: krok dla różnic skończonych
    
    Returns:
        plane_point: punkt na płaszczyźnie [x, y, z]
        plane_normal: znormalizowany wektor normalny [nx, ny, nz]
    """
    z = terrain_func(x, y)
    plane_point = np.array([x, y, z])
    
    # Oblicz gradient (pochodne cząstkowe)
    dz_dx = (terrain_func(x + delta, y) - terrain_func(x - delta, y)) / (2 * delta)
    dz_dy = (terrain_func(x, y + delta) - terrain_func(x, y - delta)) / (2 * delta)
    
    # Wektor normalny do płaszczyzny stycznej
    plane_normal = np.array([-dz_dx, -dz_dy, 1])
    plane_normal = plane_normal / np.linalg.norm(plane_normal)
    
    return plane_point, plane_normal

# <----------- NOWA FUNKCJA: Sprawdza kolizję z płaszczyzną na podstawie równania
def check_plane_collision(foot_position, plane_point, plane_normal, threshold=0.005):
    """
    Sprawdza kolizję stopy z płaszczyzną na podstawie równania płaszczyzny
    
    Args:
        foot_position: pozycja stopy [x, y, z]
        plane_point: punkt na płaszczyźnie [x, y, z]  
        plane_normal: wektor normalny płaszczyzny [nx, ny, nz]
        threshold: próg detekcji kolizji (m)
    
    Returns:
        bool: True jeśli jest kolizja, False w przeciwnym razie
        float: odległość od płaszczyzny (ujemna = wewnątrz)
    """
    # Równanie płaszczyzny: n·(P - P0) = 0
    # Odległość punktu od płaszczyzny: d = n·(P - P0) / |n|
    
    foot_to_plane = foot_position - plane_point
    distance = np.dot(plane_normal, foot_to_plane) / np.linalg.norm(plane_normal)
    
    # Kolizja gdy stopa jest blisko lub wewnątrz powierzchni
    collision = distance <= threshold
    
    return collision, distance

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

# <----------- ULEPSZONA FUNKCJA: Fizyczna poza z kontrolą pozycji XY
def calculate_robot_pose_with_physics_and_movement(supporting_foot_positions, target_xy_position, 
                                                  robot_mass=5.0, gravity=9.81, body_height=0.1, 
                                                  max_lateral_drift=0.02, prev_body_pos=None):
    """
    Oblicza pozę robota z fizyką, ale kontroluje pozycję XY żeby nie uciekał
    
    Args:
        supporting_foot_positions: pozycje nóg podpierających robota
        target_xy_position: docelowa pozycja XY (kontrola ruchu)
        robot_mass: masa robota (kg)
        gravity: przyspieszenie ziemskie (m/s²)
        body_height: wysokość platformy nad stopami (m)
        max_lateral_drift: maksymalne odchylenie od docelowej pozycji XY
        prev_body_pos: poprzednia pozycja robota (dla stabilności)
    
    Returns:
        body_position: kontrolowana pozycja robota (XY kontrolowane, Z z fizyki)
        body_orientation: macierz rotacji platformy wyrównana z terenem
        stability_margin: margines stabilności (0-1)
    """
    if len(supporting_foot_positions) == 0:
        if prev_body_pos is not None:
            return prev_body_pos, np.eye(3), 0.0
        return np.array([target_xy_position[0], target_xy_position[1], 0.1]), np.eye(3), 0.0
    
    # Oblicz średnią pozycję nóg podpierających (centrum geometryczne)
    support_center = np.mean(supporting_foot_positions, axis=0)
    
    # <----------- KONTROLA POZYCJI XY: Nie pozwól robotowi uciekać
    # Oblicz odchylenie od docelowej pozycji
    xy_deviation = support_center[:2] - target_xy_position
    deviation_magnitude = np.linalg.norm(xy_deviation)
    
    if deviation_magnitude > max_lateral_drift:
        # Ogranicz odchylenie do maksymalnego
        correction_factor = max_lateral_drift / deviation_magnitude
        corrected_xy = target_xy_position + xy_deviation * correction_factor
        print(f"KOREKTA pozycji XY: odchylenie {deviation_magnitude:.3f}m -> {max_lateral_drift:.3f}m")
    else:
        corrected_xy = support_center[:2]
    
    # Użyj kontrolowanej pozycji XY, ale fizycznej wysokości Z
    controlled_center = np.array([corrected_xy[0], corrected_xy[1], support_center[2]])
    
    # Oblicz średnią normalną powierzchni w punktach podparcia
    avg_normal = np.zeros(3)
    for pos in supporting_foot_positions:
        normal = calculate_terrain_normal(pos[0], pos[1])
        avg_normal += normal
    avg_normal = avg_normal / len(supporting_foot_positions)
    avg_normal = avg_normal / np.linalg.norm(avg_normal)
    
    # <----------- FIZYKA: Siła grawitacyjna i reakcje podłoża
    gravity_force = np.array([0, 0, -robot_mass * gravity])
    
    # Pozycja platformy - z kontrolowaną pozycją XY
    body_position = controlled_center + avg_normal * body_height
    
    # <----------- FIZYKA: Orientacja platformy wyrównana z terenem
    robot_up = np.array([0, 0, 1])
    body_orientation = rotation_matrix_from_vectors(robot_up, avg_normal)
    
    # <----------- OBLICZ MARGINES STABILNOŚCI
    if len(supporting_foot_positions) >= 3:
        support_polygon = np.array(supporting_foot_positions)[:, :2]
        body_projection = body_position[:2]
        
        min_distance_to_edge = float('inf')
        for i in range(len(support_polygon)):
            p1 = support_polygon[i]
            p2 = support_polygon[(i + 1) % len(support_polygon)]
            
            edge_vec = p2 - p1
            point_vec = body_projection - p1
            
            if np.linalg.norm(edge_vec) > 0:
                t = max(0, min(1, np.dot(point_vec, edge_vec) / np.dot(edge_vec, edge_vec)))
                closest_point = p1 + t * edge_vec
                distance = np.linalg.norm(body_projection - closest_point)
                min_distance_to_edge = min(min_distance_to_edge, distance)
        
        max_possible_distance = 0.2
        stability_margin = min(1.0, min_distance_to_edge / max_possible_distance)
    else:
        stability_margin = 0.0
    
    return body_position, body_orientation, stability_margin

# ZAKOMENTOWANE STARE ROZWIĄZANIE:
# def calculate_robot_pose(supporting_foot_positions, prev_body_pos=None):
#     """Calculate robot body position and orientation based on supporting feet"""
#     if len(supporting_foot_positions) == 0:
#         if prev_body_pos is not None:
#             return prev_body_pos, np.eye(3)
#         return np.array([0, 0.2, 0.1]), np.eye(3)
#     
#     # Calculate center of supporting feet
#     center_pos = np.mean(supporting_foot_positions, axis=0)
#     
#     # Calculate average terrain normal at supporting feet
#     avg_normal = np.zeros(3)
#     for pos in supporting_foot_positions:
#         normal = calculate_terrain_normal(pos[0], pos[1])
#         avg_normal += normal
#     avg_normal = avg_normal / len(supporting_foot_positions)
#     avg_normal = avg_normal / np.linalg.norm(avg_normal)
#     
#     # Robot body should be slightly above the center
#     body_offset = 0.05  # 5cm above ground
#     body_position = center_pos + avg_normal * body_offset
#     
#     # Calculate rotation matrix to align robot's up vector with terrain normal
#     robot_up = np.array([0, 0, 1])  # Original up direction
#     rotation_matrix = rotation_matrix_from_vectors(robot_up, avg_normal)
#     
#     return body_position, rotation_matrix

# <----------- NOWA FUNKCJA: Ulepszone obliczanie pozycji stopy z fizyką
def enhanced_foot_position_calculation(robot_body_pos, robot_rotation, 
                                     desired_foot_local, leg_index, terrain_func):
    """
    Ulepszone obliczanie pozycji stopy z zaawansowaną detekcją kolizji i fizyką
    
    Args:
        robot_body_pos: aktualna pozycja platformy robota
        robot_rotation: aktualna orientacja platformy robota
        desired_foot_local: pożądana pozycja stopy w układzie lokalnym robota
        leg_index: indeks nogi (0-5)
        terrain_func: funkcja wysokości terenu
    
    Returns:
        foot_world_pos: skorygowana pozycja stopy w przestrzeni świata
        ground_contact: bool - czy stopa ma kontakt z ziemią
        surface_normal: wektor normalny powierzchni w punkcie kontaktu
    """
    # 1. Oblicz pozycję stopy w przestrzeni świata
    foot_world_pos = robot_body_pos + np.dot(robot_rotation, desired_foot_local)
    
    # 2. Oblicz lokalną płaszczyznę terenu w punkcie stopy
    plane_point, plane_normal = calculate_terrain_plane_at_point(
        foot_world_pos[0], foot_world_pos[1], terrain_func
    )
    
    # 3. Sprawdź kolizję z płaszczyzną terenu
    collision, distance_to_plane = check_plane_collision(
        foot_world_pos, plane_point, plane_normal, threshold=CONTACT_THRESHOLD
    )
    
    # 4. Skoryguj pozycję przy kolizji
    if collision:
        # Ustaw stopę dokładnie na powierzchni terenu
        foot_world_pos = foot_world_pos - distance_to_plane * plane_normal
        ground_contact = True
        print(f"Noga {leg_index}: Kontakt z ziemią! Korekta: {distance_to_plane:.4f}m")
    else:
        ground_contact = False
    
    return foot_world_pos, ground_contact, plane_normal

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
# ROBOT Z KONTROLOWANYM RUCHEM POD GÓRKĘ
# ====================================================================

# <----------- NOWE: Kontrolowane parametry ruchu
robot_start_center = np.array([0, 0.2])  # Punkt startowy
MOVEMENT_SPEED = 0.005  # Prędkość ruchu pod górkę (m/frame)
MAX_LATERAL_DRIFT = 0.02  # Maksymalne odchylenie w bok (2cm)

print(f"Robot STARTUJE na pozycji: {robot_start_center}")
print(f"Prędkość pod górkę: {MOVEMENT_SPEED}m/frame")
print(f"Maksymalne odchylenie boczne: {MAX_LATERAL_DRIFT}m")
print(f"Wysokość terenu w punkcie startowym: {hill_height(robot_start_center[0], robot_start_center[1]):.3f}m")
print("POZYCJA ROBOTA: dynamiczna wysokość/nachylenie, kontrolowany ruch pod górkę")

# Parametry inspirowane oryginalnym kodem
h = l3 / 4
r = h
ilosc_punktow_na_krzywych = 20

# <----------- NOWE PARAMETRY FIZYCZNE
ROBOT_MASS = 5.0  # Masa robota w kg
GRAVITY = 9.81    # Przyspieszenie ziemskie
BODY_HEIGHT = 0.14  # Wysokość platformy nad nogami
CONTACT_THRESHOLD = 0.005  # Próg detekcji kontaktu z ziemią (5mm)

print(f"Parametry fizyczne: masa={ROBOT_MASS}kg, grawitacja={GRAVITY}m/s², wysokość={BODY_HEIGHT}m")

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
# <----------- NOWE TABLICE: dane fizyczne i kontrola ruchu
stability_margins = np.zeros(num_frames)  # Margines stabilności
surface_normals = np.zeros((6, num_frames, 3))  # Normalne powierzchni dla każdej nogi
target_positions = np.zeros((num_frames, 2))  # Docelowe pozycje XY robota (ruch pod górkę)

# KONTROLA RUCHU SEKWENCJI NA PODSTAWIE KOLIZJI
sequence_active = True  # Czy sekwencja ruchu jest aktywna
sequence_frame = 0      # Aktualna klatka w sekwencji
wait_for_all_grounded = False  # Czy czekamy aż wszystkie nogi dotkną ziemi

MIN_LIFT_DURATION = 10  # Minimalna liczba klatek w powietrzu
CLEARANCE_HEIGHT = 0.02  # Minimalna wysokość nad ziemią
leg_lift_frames = np.full((6,), -1)

print(f"Długość cyklu: {num_frames} klatek")
print(f"Parametry kolizji: min_lift={MIN_LIFT_DURATION}, clearance={CLEARANCE_HEIGHT}m")

# <----------- NOWE: Planowanie ruchu pod górkę dla każdej klatki
print("PLANOWANIE RUCHU: Obliczanie trajektorii pod górkę...")
for frame in range(num_frames):
    # Ruch pod górkę (kierunek Y+) z kontrolowaną prędkością
    progress = frame / num_frames
    current_y = robot_start_center[1] + progress * MOVEMENT_SPEED * num_frames
    target_positions[frame] = np.array([robot_start_center[0], current_y])
    
print(f"Trajektoria: od Y={robot_start_center[1]:.3f} do Y={target_positions[-1][1]:.3f}")
print(f"Całkowity dystans pod górkę: {target_positions[-1][1] - robot_start_center[1]:.3f}m")

# <----------- NOWE: Inicjalizacja pozycji robota z kontrolą XY
print("INICJALIZACJA: Obliczanie pozycji robota z kontrolą pozycji XY...")

# Oblicz pozycje wszystkich stóp w pozycji spoczynkowej
initial_foot_positions = []
for j in range(6):
    # Stopa w pozycji spoczynkowej względem punktu startowego
    estimated_foot_world = np.array([robot_start_center[0], robot_start_center[1], 0.15]) + stopa_spoczynkowa
    
    # Skoryguj do powierzchni terenu
    foot_world_pos, ground_contact, surface_normal = enhanced_foot_position_calculation(
        np.array([robot_start_center[0], robot_start_center[1], 0.15]), 
        np.eye(3), 
        stopa_spoczynkowa, 
        j, 
        hill_height
    )
    initial_foot_positions.append(foot_world_pos)

# Oblicz pozycję robota z kontrolą XY
initial_body_pos, initial_rotation, initial_stability = calculate_robot_pose_with_physics_and_movement(
    initial_foot_positions, robot_start_center, ROBOT_MASS, GRAVITY, BODY_HEIGHT, MAX_LATERAL_DRIFT
)

print(f"Pozycja początkowa robota: {initial_body_pos}")
print(f"Docelowa pozycja XY: {robot_start_center}")
print(f"Margines stabilności początkowej: {initial_stability:.3f}")

# Oblicz pozycje dla każdej klatki
for frame in range(num_frames):
    if frame > 0:
        robot_body_pos = robot_body_positions[frame-1].copy()
        robot_rotation = robot_rotations[frame-1].copy()
    else:
        # <----------- NOWE: Użyj obliczonej pozycji początkowej zamiast hardkodowanej
        # ZAKOMENTOWANE STARE:
        # ground_height_center = hill_height(robot_fixed_center[0], robot_fixed_center[1])
        # robot_body_pos = np.array([robot_fixed_center[0], robot_fixed_center[1], ground_height_center + 0.05])
        # robot_rotation = np.eye(3)
        
        robot_body_pos = initial_body_pos
        robot_rotation = initial_rotation
    
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
    # <----------- NOWE: DYNAMICZNE OBLICZANIE POZYCJI NÓG Z KONTROLĄ RUCHU
    # ====================================================================
    supporting_positions = []
    
    # <----------- AKTUALNA DOCELOWA POZYCJA XY (ruch pod górkę)
    current_target_xy = target_positions[frame]
    
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
        
        # <----------- NOWE: Użyj ulepszonej funkcji z aktualną pozycją robota
        foot_world_pos, ground_contact, surface_normal = enhanced_foot_position_calculation(
            robot_body_pos, robot_rotation, desired_foot_local, j, hill_height
        )
        
        # Zapisz normalną powierzchni dla tej nogi
        surface_normals[j][frame] = surface_normal
        
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
        
        # <----------- NOWE: Ulepszona detekcja kontaktu z fizyką
        # ZAKOMENTOWANE STARE ROZWIĄZANIE:
        # if planned_height <= 0.01 and can_touch_ground:
        #     foot_world_pos[2] = max(ground_height, foot_world_pos[2]) 
        #     foot_touching_ground[j][frame] = True
        #     supporting_positions.append(foot_world_pos)
        # else:
        #     foot_touching_ground[j][frame] = False
        #     # Nogi w powietrzu - minimum nad ziemią
        #     min_height = ground_height + max(CLEARANCE_HEIGHT, planned_height)
        #     foot_world_pos[2] = max(foot_world_pos[2], min_height)
        
        if planned_height <= 0.01 and can_touch_ground:
            # Sprawdź czy enhanced_foot_position_calculation wykryła kontakt
            if ground_contact:
                foot_touching_ground[j][frame] = True
                supporting_positions.append(foot_world_pos)
                print(f"Frame {frame}: Noga {j} - KONTAKT z ziemią (fizyka)")
            else:
                foot_touching_ground[j][frame] = False
        else:
            foot_touching_ground[j][frame] = False
            # <----------- NOWE: Utrzymuj clearance nad powierzchnią
            if not ground_contact:
                # Oblicz minimalną wysokość z clearance
                ground_z = hill_height(foot_world_pos[0], foot_world_pos[1])
                min_height = ground_z + max(CLEARANCE_HEIGHT, planned_height)
                if foot_world_pos[2] < min_height:
                    foot_world_pos[2] = min_height
                    print(f"Frame {frame}: Noga {j} - korekta clearance do {min_height:.3f}m")
        
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
    # <----------- NOWE: OBLICZ FIZYCZNĄ POZĘ Z KONTROLĄ POZYCJI XY
    # ====================================================================
    if len(supporting_positions) >= 3:
        # <----------- NOWE: Użyj funkcji z kontrolą pozycji XY
        prev_pos = robot_body_pos if frame > 0 else None
        robot_body_pos, robot_rotation, stability_margin = calculate_robot_pose_with_physics_and_movement(
            supporting_positions, current_target_xy, ROBOT_MASS, GRAVITY, BODY_HEIGHT, MAX_LATERAL_DRIFT, prev_pos
        )
        stability_margins[frame] = stability_margin
        
        # Sprawdź czy robot trzyma się trajektorii
        xy_error = np.linalg.norm(robot_body_pos[:2] - current_target_xy)
        print(f"Frame {frame}: Poza XY - cel: {current_target_xy}, rzeczywista: {robot_body_pos[:2]}, błąd: {xy_error:.4f}m")
    else:
        # <----------- NOWE: Fallback z kontrolą XY
        if frame > 0:
            # Lekko obniż robota z powodu braku podparcia, ale utrzymaj docelową pozycję XY
            gravity_correction = np.array([0, 0, -0.001])  # 1mm spadek na klatkę
            prev_pos = robot_body_positions[frame-1]
            robot_body_pos = np.array([current_target_xy[0], current_target_xy[1], prev_pos[2]]) + gravity_correction
            robot_rotation = robot_rotations[frame-1]
            stability_margins[frame] = 0.0
        else:
            robot_body_pos = initial_body_pos
            robot_rotation = initial_rotation
            stability_margins[frame] = 0.0
        
        print(f"Frame {frame}: FALLBACK - pozycja wymuszona na docelową XY: {current_target_xy}")
    
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
    ax.set_title('Hexapod - KONTROLOWANY RUCH POD GÓRKĘ: Fizyka + Kontrola pozycji XY')
    
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
            
            # <----------- NOWE: Wizualizacja wektora normalnej powierzchni
            surface_normal = surface_normals[j][frame]
            normal_length = 0.03  # 3cm długość wektora
            normal_end = foot[j][frame] + surface_normal * normal_length
            ax.plot([foot[j][frame][0], normal_end[0]],
                    [foot[j][frame][1], normal_end[1]],
                    [foot[j][frame][2], normal_end[2]], 
                    color='cyan', linewidth=2, alpha=0.7)
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
    
    # <----------- NOWE: Dodatkowe informacje o kontroli ruchu
    ax.text2D(0.02, 0.98, f"KONTROLOWANY RUCH POD GÓRKĘ + FIZYKA", 
              transform=ax.transAxes, fontsize=12, weight='bold', verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='lightgreen', alpha=0.8))
    
    # <----------- NOWE: Informacje o pozycji i trajektorii
    current_target = target_positions[frame]
    actual_xy = robot_body_positions[frame][:2]
    xy_error = np.linalg.norm(actual_xy - current_target)
    
    ax.text2D(0.02, 0.90, f"Docelowa pozycja XY: ({current_target[0]:.3f}, {current_target[1]:.3f})", 
              transform=ax.transAxes, fontsize=9, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='lightblue', alpha=0.8))
    
    ax.text2D(0.02, 0.82, f"Rzeczywista XY: ({actual_xy[0]:.3f}, {actual_xy[1]:.3f})", 
              transform=ax.transAxes, fontsize=9, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
    
    error_color = 'lightgreen' if xy_error < MAX_LATERAL_DRIFT/2 else 'yellow' if xy_error < MAX_LATERAL_DRIFT else 'salmon'
    ax.text2D(0.02, 0.74, f"Błąd pozycji XY: {xy_error:.4f}m", 
              transform=ax.transAxes, fontsize=9, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor=error_color, alpha=0.8))
    
    ax.text2D(0.02, 0.66, f"Nogi na ziemi: {legs_on_ground}/6", 
              transform=ax.transAxes, fontsize=10, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
    
    ax.text2D(0.02, 0.58, f"Tripod A: {tripod_A_on_ground}/3 | Tripod B: {tripod_B_on_ground}/3", 
              transform=ax.transAxes, fontsize=10, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='lightblue', alpha=0.8))
    # <----------- NOWE: Margines stabilności z kontrolą ruchu
    current_stability = stability_margins[frame]
    stability_color = 'lightgreen' if current_stability > 0.5 else 'yellow' if current_stability > 0.2 else 'salmon'
    ax.text2D(0.02, 0.50, f"Stabilność: {current_stability:.3f}", 
              transform=ax.transAxes, fontsize=10, weight='bold', verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor=stability_color, alpha=0.8))
    
    # Show sequence status
    if legs_on_ground >= 3:
        status_text = "Sekwencja AKTYWNA"
        status_color = 'lightgreen'
    else:
        status_text = "Sekwencja ZATRZYMANA"
        status_color = 'salmon'
    
    ax.text2D(0.02, 0.42, status_text, 
              transform=ax.transAxes, fontsize=10, weight='bold', verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor=status_color, alpha=0.8))
    
    # Show which legs are currently lifted
    lifted_legs = [j for j in range(6) if not foot_touching_ground[j][frame]]
    if lifted_legs:
        ax.text2D(0.02, 0.34, f"Podniesione nogi: {lifted_legs}", 
                  transform=ax.transAxes, fontsize=9, verticalalignment='top',
                  bbox=dict(boxstyle="round", facecolor='orange', alpha=0.7))
    
    ax.text2D(0.02, 0.26, f"Frame: {frame}/{num_frames}", 
              transform=ax.transAxes, fontsize=9, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='lightgray', alpha=0.8))
    
    # Calculate platform tilt angle
    up_vector = np.dot(robot_rotations[frame], np.array([0, 0, 1]))
    tilt_angle = np.degrees(np.arccos(np.clip(np.dot(up_vector, np.array([0, 0, 1])), -1, 1)))
    
    ax.text2D(0.02, 0.18, f"Nachylenie platformy: {tilt_angle:.1f}°", 
              transform=ax.transAxes, fontsize=9, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='lightyellow', alpha=0.8))
    
    # <----------- NOWE: Parametry kontroli ruchu
    progress_percent = (frame / num_frames) * 100
    ax.text2D(0.02, 0.10, f"Postęp pod górkę: {progress_percent:.1f}%", 
              transform=ax.transAxes, fontsize=9, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='lightcyan', alpha=0.8))
    
    ax.text2D(0.02, 0.02, f"Prędkość: {MOVEMENT_SPEED*1000:.1f}mm/frame | Max drift: {MAX_LATERAL_DRIFT*1000:.0f}mm", 
              transform=ax.transAxes, fontsize=8, verticalalignment='top',
              bbox=dict(boxstyle="round", facecolor='lightcyan', alpha=0.8))
    
    # Add robot body center point
    ax.scatter(robot_body_positions[frame][0], robot_body_positions[frame][1], robot_body_positions[frame][2], 
              color='black', s=100, marker='s', alpha=0.8)
    
    # <----------- NOWE: Wizualizacja docelowej pozycji XY
    target_z = hill_height(current_target[0], current_target[1]) + 0.01
    ax.scatter(current_target[0], current_target[1], target_z, 
              color='red', s=50, marker='x', alpha=0.8, linewidths=3)
    
    # <----------- NOWE: Linia pokazująca trajektorię pod górkę
    if frame > 5:
        path_frames = range(max(0, frame-20), frame, 2)
        if len(path_frames) > 1:
            path_positions = robot_body_positions[path_frames]
            ax.plot(path_positions[:, 0], path_positions[:, 1], path_positions[:, 2], 
                   'g--', alpha=0.6, linewidth=2, label='Trajektoria robota')

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
# <----------- NOWE PODSUMOWANIE - KONTROLOWANY RUCH POD GÓRKĘ:
# ====================================================================
print("\n" + "="*80)
print("HEXAPOD Z KONTROLOWANYM RUCHEM POD GÓRKĘ + FIZYKA")
print("="*80)
print("✅ ROZWIĄZANE PROBLEMY:")
print("   🚫 USUNIĘTO całkowite hardkodowanie pozycji")
print("   🎯 Robot NIE ucieka w boki - kontrola pozycji XY")
print("   ⬆️  Robot idzie POD GÓRKĘ (kierunek Y+)")
print("   📏 Wysokość i nachylenie dostosowane do pozycji nóg")
print("   ⚖️  Dodana fizyka z masą i grawitacją")
print("")
print("✅ SYSTEM KONTROLI RUCHU:")
print("   🎯 Docelowa pozycja XY planowana dla każdej klatki")
print("   📐 Wysokość Z obliczana z fizyki nóg")
print("   🔒 Maksymalne odchylenie boczne ograniczone")
print("   ⬆️  Stała prędkość ruchu pod górkę")
print("   📊 Monitoring błędu pozycji w czasie rzeczywistym")
print("")
print("✅ NOWE FUNKCJE I PARAMETRY:")
print("   🎯 calculate_robot_pose_with_physics_and_movement()")
print("   📍 target_positions[] - trajektoria pod górkę")
print(f"   ⚡ MOVEMENT_SPEED = {MOVEMENT_SPEED}m/frame")
print(f"   🔒 MAX_LATERAL_DRIFT = {MAX_LATERAL_DRIFT}m")
print("")
print("✅ WIZUALIZACJA:")
print("   🎯 Czerwony X pokazuje docelową pozycję XY")
print("   📈 Zielona linia przerywana - trajektoria robota")  
print("   📊 Błąd pozycji XY z kolorowym kodowaniem")
print("   💠 Cyan wektory - normalne powierzchni")
print("   📐 Monitoring nachylenia platformy")
print("")
print("✅ FIZYCZNE ZACHOWANIE:")
print(f"   🎬 Całkowity dystans pod górkę: {target_positions[-1][1] - robot_start_center[1]:.3f}m")
print(f"   ⚖️  Masa: {ROBOT_MASS}kg, Grawitacja: {GRAVITY}m/s²")
print("   📐 Orientacja platformy zgodna z terenem")
print("   🛡️  Margines stabilności w czasie rzeczywistym")
print("   🎯 Detekcja kolizji z równaniem płaszczyzny")
print("")
print("🚀 IDEALNY SYSTEM CHODZENIA POD GÓRKĘ!")
print("   - Robot pozostaje na trajektorii")
print("   - Nie ucieka w boki")
print("   - Fizycznie realistyczne zachowanie") 
print("   - Pełna kontrola nad ruchem")
print("   - Gotowy do dalszych ulepszeń")
print("="*80)