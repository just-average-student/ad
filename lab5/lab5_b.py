import numpy as np
import subprocess
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row, gridplot
from bokeh.models import ColumnDataSource, Button, CheckboxGroup, Select, Slider

#початкові параметри
default_amplitude = 1.0
default_frequency = 1.0
default_phase = 0.0
default_noise_mean = 0.0
default_noise_covariance = 0.1
default_window_size = 40
show_noise = True
t = np.linspace(0, 10, 1000)
noise = np.random.normal(0, 1, 1000)

#новий шум
def gen_new_noise():
    global noise
    noise = np.random.normal(0, 1, 1000)
    update(None, None, None)

#генерація гармоніки
def harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise):
    h = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    if show_noise:
        h += noise_mean + np.sqrt(noise_covariance) * noise
        return h
    return h

#фільтрація шуму 
def simple_moving_average(harmonic, window_size):
    n = len(harmonic)
    filtered = np.zeros(n)

    for i in range(n):
        start_index = max(0, i - window_size // 2)
        end_index = min(n, i + window_size // 2 + 1)
        filtered[i] = np.mean(harmonic[start_index:end_index])

    return filtered

h = harmonic_with_noise(t, default_amplitude, default_frequency, default_phase, default_noise_mean, default_noise_covariance, show_noise)
fil_h = simple_moving_average(h, default_window_size)

source = ColumnDataSource(data={'t': t, 'h': h, 'fil_h': fil_h})

plot1 = figure(title="Harmonic with noise", x_axis_label='Time (s)', y_axis_label='Amplitude', x_axis_type="linear", y_axis_type="linear", height=300, width=700)
plot2 = figure(title="Filtered harmonic", x_axis_label='Time (s)', y_axis_label='Amplitude', x_axis_type="linear", y_axis_type="linear", height=300, width=700)

line1 = plot1.line('t', 'h', source=source, line_width=2, color='crimson', line_alpha=0.7)
line2 = plot2.line('t', 'fil_h', source=source, line_width=2, color='wheat', line_alpha=0.7)

amplitude_slider = Slider(start=0.1, end=5.0, value=default_amplitude, step=0.1, title="Amplitude")
frequency_slider = Slider(start=0.1, end=5.0, value=default_frequency, step=0.1, title="Frequency")
phase_slider = Slider(start=-np.pi, end=np.pi, value=default_phase, step=0.1, title="Phase")
noise_mean_slider = Slider(start=-1.0, end=1.0, value=default_noise_mean, step=0.1, title="Noise Mean")
noise_covariance_slider = Slider(start=0.0, end=1.0, value=default_noise_covariance, step=0.05, title="Noise Covariance")
window_size_slider = Slider(start=10, end=80, value=40, step=10, title="window size")

checkbox = CheckboxGroup(labels=["Show Noise"], active=[0])

filter_menu = Select(title="Filtering", value="simple_moving_average", options=["simple_moving_average", "none"])

reset_button = Button(label="Reset")
new_noise_button = Button(label="New noise")

def update(attr, old, new):
    amplitude = amplitude_slider.value
    frequency = frequency_slider.value
    phase = phase_slider.value
    noise_mean = noise_mean_slider.value
    noise_dispersion = noise_covariance_slider.value
    window_size = window_size_slider.value
    show_noise = 0 in checkbox.active
    filter_type = filter_menu.value

    h = harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_dispersion, show_noise)

    if filter_type == "none":
        fil_h = h
    else:
        fil_h = simple_moving_average(h, window_size)

    source.data = {'t': t, 'h': h, 'fil_h': fil_h}

def reset():
    amplitude_slider.value = default_amplitude
    frequency_slider.value = default_frequency
    phase_slider.value = default_phase
    noise_mean_slider.value = default_noise_mean
    noise_covariance_slider.value = default_noise_covariance
    window_size_slider.value = default_window_size
    filter_menu.value = "simple_moving_average"
    update(None, None, None)

amplitude_slider.on_change('value', update)
frequency_slider.on_change('value', update)
phase_slider.on_change('value', update)
noise_mean_slider.on_change('value', update)
noise_covariance_slider.on_change('value', update)
window_size_slider.on_change('value', update)
checkbox.on_change('active', update)
filter_menu.on_change('value', update)
reset_button.on_click(reset)
new_noise_button.on_click(gen_new_noise)

layouts = column(gridplot([[plot1, plot2]], toolbar_location="above"), row(amplitude_slider, frequency_slider, phase_slider), row(noise_mean_slider, 
            noise_covariance_slider, window_size_slider), row(checkbox, filter_menu, reset_button, new_noise_button))

curdoc().add_root(layouts)
subprocess.run(["bokeh", "serve", "--show", __file__])