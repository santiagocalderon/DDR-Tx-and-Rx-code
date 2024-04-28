import network
import espnow
from machine import Pin, DAC
import math
import time
import _thread

# Initialize WLAN interface
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()  # Disconnect from any previous network connection

# Initialize ESPNow
e = espnow.ESPNow()
e.active(True)

# Define LED pins
led_pins = [13, 12, 14, 27]  # Example pin numbers, adjust as needed
leds = [Pin(pin, Pin.OUT) for pin in led_pins]

# Define DAC output pin
DAC_PIN = 25  # Example pin number, adjust as needed
dac = DAC(Pin(DAC_PIN))

# Global variable to store button states
x = [0, 0, 0, 0]
x_lock = _thread.allocate_lock()  # Lock for thread-safe access to x
#################################
sample_rate = 10000
frequency = 1


################################
# Function to control LEDs based on button states
def control_leds():
    while True:
        with x_lock:  # Acquire lock before accessing x
            button_states = x[:]
        for i, state in enumerate(button_states):
            leds[i].value(state)
        # Introduce a short delay to reduce CPU usage
        time.sleep_ms(1)

# Function to play one period of a sine wave based on button states
def play_sine_wave():
    sample_rate = 10000
    frequency = 1
    while True:
        with x_lock:  # Acquire lock before accessing x
            button_states = x[:]
        
        # Determine the frequency based on the pressed button
        if button_states[0] == 0:
            frequency = 440
        elif button_states[1] == 0:
            frequency = 554.37
        elif button_states[2] == 0:
            frequency = 659.26  # Note E4
        elif button_states[3] == 0:
            frequency = 783.99  # Note F4
        else:
            frequency = 0  # No button pressed, silence
        
        # Generate one period of sine wave at the specified frequency
        if frequency != 0:
            # Calculate the number of samples needed for one period
            samples_per_period = sample_rate // frequency
            
            # Output the sine wave at the specified frequency
            for i in range(samples_per_period):
                value = int(127 * math.sin(2 * math.pi * i / samples_per_period) + 128)  # Scale the sine wave to 8-bit DAC range
                dac.write(value)  # Write the value to the DAC output
        else:
            pass
        
        # Introduce a short delay to reduce CPU usage
        time.sleep_ms(1)

# Start threads with different priorities
_thread.start_new_thread(control_leds, ())

# Start the higher-priority thread
_thread.start_new_thread(play_sine_wave, ())

# Main thread continues to receive and update button states
while True:
    host, msg = e.recv()
    if msg:
        with x_lock:  # Acquire lock before updating x
            x = list(msg)
            #print(x)

