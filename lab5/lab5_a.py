import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import butter, filtfilt

#початкові параметри
default_amplitude = 1.0
default_frequency = 1.0
default_phase = 0.0
default_noise_mean = 0.0
default_noise_covariance = 0.1
show_noise = True
t = np.linspace(0, 10, 1000)
noise = np.random.normal(0, 1, 1000)

#новий шум
def gen_new_noise(event):
    global noise
    noise = np.random.normal(0, 1, 1000)
    update(None)

#генерація гармоніки
def harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise):
    h = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    if show_noise:
        h += noise_mean + np.sqrt(noise_covariance) * noise
        return h
    return h

#фільтрація шуму 
def filter(harmonic, order=2):
    b, a = butter(order, 2, btype='low', fs=100)
    filtered = filtfilt(b, a, harmonic)
    return filtered

#створення фігури з графіками
fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 8))
plt.subplots_adjust(bottom=0.45)

h = harmonic_with_noise(t, default_amplitude, default_frequency, default_phase, default_noise_mean, default_noise_covariance, show_noise)
fil_h = filter(h)

ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Amplitude')
ax1.set_title('Harmonic with noise')
line1, = ax1.plot(t, h, lw=2, color='crimson')

ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Amplitude')
ax2.set_title('Filtered harmonic')
line2, = ax2.plot(t, fil_h, lw=2, color='wheat')

#слайдери
axes_amplitude = plt.axes([0.2, 0.35, 0.7, 0.03])
amplitude_slider = Slider(axes_amplitude, 'Amplitude', 0.1, 5.0, valinit=default_amplitude, valstep=0.1)
axes_frequency = plt.axes([0.2, 0.3, 0.7, 0.03])
frequency_slider = Slider(axes_frequency, 'Frequency', 0.1, 5.0, valinit=default_frequency, valstep=0.1)
axes_phase = plt.axes([0.2, 0.25, 0.7, 0.03])
phase_slider = Slider(axes_phase, 'Phase', -np.pi, np.pi, valinit=default_phase, valstep=0.1)
axes_noise_mean = plt.axes([0.2, 0.2, 0.7, 0.03])
noise_mean_slider = Slider(axes_noise_mean, 'Noise mean', -1.0, 1.0, valinit=default_noise_mean, valstep=0.1)
axes_noise_covariance = plt.axes([0.2, 0.15, 0.7, 0.03])
noise_covariance_slider = Slider(axes_noise_covariance, 'Noise covariance', 0.0, 1.0, valinit=default_noise_covariance, valstep=0.05)
axes_order = plt.axes([0.2, 0.1, 0.7, 0.03])
order_slider = Slider(axes_order, 'Order', 1, 10, valinit=2, valstep=1)

#накладання шуму
axes_checkbox = plt.axes([0.55, 0.03, 0.1, 0.04])
checkbox = CheckButtons(axes_checkbox, ['Show noise'], [show_noise])

#скидання параметрів
axes_reset = plt.axes([0.35, 0.03, 0.1, 0.04])
reset_button = Button(axes_reset, 'Reset')

#генерація нового шуму
axes_new_noise_button = plt.axes([0.45, 0.03, 0.1, 0.04])
new_noise_button = Button(axes_new_noise_button, 'New noise')

#функція оновлення графіків
def update(val):
    amplitude = amplitude_slider.val
    frequency = frequency_slider.val
    phase = phase_slider.val
    noise_mean = noise_mean_slider.val
    noise_dispersion = noise_covariance_slider.val
    order = order_slider.val
    show_noise = checkbox.get_status()[0]

    h = harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_dispersion, show_noise)
    fil_h = filter(h, order)

    line1.set_data(t, h)
    line2.set_data(t, fil_h)

    fig.canvas.draw_idle()

#функція скидання параметрів
def reset(event):
    amplitude_slider.reset()
    frequency_slider.reset()
    phase_slider.reset()
    noise_mean_slider.reset()
    noise_covariance_slider.reset()
    order_slider.reset()
    update(None)

#прив'язка функцій
amplitude_slider.on_changed(update)
frequency_slider.on_changed(update)
phase_slider.on_changed(update)
noise_mean_slider.on_changed(update)
noise_covariance_slider.on_changed(update)
order_slider.on_changed(update)
checkbox.on_clicked(update)
new_noise_button.on_clicked(gen_new_noise)
reset_button.on_clicked(reset)

plt.show()