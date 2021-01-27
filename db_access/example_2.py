""" A simple example how to read measurements from database and visualize them

Additional requirement for visualization - matplotlib
pip install matplotlib
sudo apt-get install python3-tk
"""

from datetime import datetime

import matplotlib.pyplot as plt

from view.device_view import DeviceView

device_name = 'dev_p_1'

newest_measurements = DeviceView.get_newest_measurements_for_device(device_id=device_name, max_number_of_measurements=15)
timestamps = []
vals = []

for measurement in newest_measurements:
    timestamps.append(measurement.timestamp / 1000)
    vals.append(measurement.value)

dates = [datetime.fromtimestamp(t).strftime("%H:%M:%S") for t in timestamps]

fig, ax = plt.subplots()
ax.plot(timestamps, vals, '-o')

ax.set(xlabel='Time', ylabel='Temperature (K)',
       title=f'Temperature for device "{device_name}"')
ax.set_xticklabels(dates)
ax.grid()
plt.xticks(rotation=70)
fig.savefig("test.png")
plt.show()
