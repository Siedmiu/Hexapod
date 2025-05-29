import serial
import time
import matplotlib.pyplot as plt

"""
This program shows the raw and filtered data acquired from IMU in real time
change the data_index to select variable to observe
ax - 1, ay - 2, az - 3, roll - 4, pitch - 5, yaw - 6
"""

data_index = 2

times = []
ax = []
ax_filtered = []

# Alpha ( 0 - 1)
alpha = 0.1  # lower -> stronger filtering

ser = serial.Serial('COM3', 9600)
time.sleep(5)

#Plot init
plt.ion()
fig, ax_plot = plt.subplots(figsize=(10, 5))
ax_plot.set_title('Data')
ax_plot.set_ylabel('Data')
ax_plot.set_xlabel('Time')

try:
    while plt.fignum_exists(fig.number):
        line = ser.readline().decode('utf-8').strip()
        data = line.split(",")
        print(data)

        if len(data) >= 2:
            try:
                t = float(data[0])
                ax_val = float(data[data_index])

                times.append(t)
                ax.append(ax_val)

                # Filtering
                if len(ax_filtered) == 0:
                    ax_filtered.append(ax_val)
                else:
                    filtered = alpha * ax_val + (1 - alpha) * ax_filtered[-1]
                    ax_filtered.append(filtered)

                # Removing of old samples
                max_samples = 100
                if len(times) > max_samples:
                    times.pop(0)
                    ax.pop(0)
                    ax_filtered.pop(0)

                #Plot update
                ax_plot.cla()
                ax_plot.set_title('Data')
                ax_plot.set_ylabel('Variable')
                ax_plot.set_xlabel('Time (s)')
                ax_plot.plot(times, ax, label='Varaiable '  + 'raw', color='blue')
                ax_plot.plot(times, ax_filtered, label='Varaiable ' + 'filtered', color='red')
                ax_plot.legend()
                plt.pause(0.01)

            except ValueError:
                print("Data conversion error", data)

except KeyboardInterrupt:
    print("Aborted")
    ser.close()
