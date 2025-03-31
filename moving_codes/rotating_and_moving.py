import numpy as np

#przesuniecie srodka hexapoda
delta_x = -1
delta_y = 2

# obrot o kąt alfa (dodatni jest CCW)
alfa = np.deg2rad(15)

x_n = 2
y_n = 4

#obrót przyczepu wokół środka robota
x_no = x_n * np.cos(alfa) - y_n * np.sin(alfa)
y_no = x_n * np.sin(alfa) + y_n * np.cos(alfa)

#przesuniecie przyczepu wraz z robotem
x_n1 = x_no + delta_x
y_n1 = y_no + delta_y

#wspolrzedne punktu styku z podłogą (odleglosc od przyczepu ale w ukladzie wspolrzednych srodka robota a nie przyczepu)
A_x = 5
A_y = 1

beta = np.atan2(A_y, A_x)

# potrzebujemy informacji o odleglosci względem przyczepu tak aby każda noga była sterowana tak samo
A_x_wzgl_przyczepu = np.sqrt(A_x**2 + A_y**2)
A_y_wzgl_przyczepu = 0

#przesuniecie przyczepu wzdgledem ukladu wspolrzednych srodka robota
x_l = x_n1 - x_n
y_l = y_n1 - y_n
l = np.sqrt(x_l**2 + y_l**2)

#zmiana przesuniecia na uklad wspolrzednych przyczepu nogi
gamma = np.atan2(y_l, x_l)

teta = np.deg2rad(180) - gamma + beta
# todo nie jestem pewien czy tu zawsze minus dla różnych kątów trzeba się upewnić
x_l_wzgl_przyczepu = -np.cos(teta) * l
y_l_wzgl_przyczepu = np.sin(teta) * l

#polozenie punktu wzgledem przyczepu po przesunieciu robota
A_x_buf = A_x_wzgl_przyczepu - x_l_wzgl_przyczepu
A_y_buf = A_y_wzgl_przyczepu - y_l_wzgl_przyczepu

#polozenie punktu wzgledem przyczepu po obrocie robota
A_x_n = A_x_buf * np.cos(alfa) + A_y_buf * np.sin(alfa)
A_y_n = -A_x_buf * np.sin(alfa) + A_y_buf * np.cos(alfa)

print(A_x_n, A_y_n)


