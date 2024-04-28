import network
import espnow
from machine import Pin
import time
from LCD import LCD
import _thread

# Activate WLAN interface
sta = network.WLAN(network.STA_IF)  # Use STA_IF for station mode
sta.active(True)
sta.disconnect()  # Disconnect from any previous network connection

# Initialize ESPNow
e = espnow.ESPNow()
e.active(True)

# Define the MAC address of the receiver (RX) ESP32
peer = b'\xec\x64\xc9\x85\xc9\x40'
e.add_peer(peer)

# Define button pins
BUTTON_1 = Pin(36, Pin.IN, Pin.PULL_UP)
BUTTON_2 = Pin(39, Pin.IN, Pin.PULL_UP)
BUTTON_3 = Pin(34, Pin.IN, Pin.PULL_UP)
BUTTON_4 = Pin(35, Pin.IN, Pin.PULL_UP)

# Set LCD and initialize
lcd = LCD(enable_pin=21, reg_select_pin=19, data_pins=[3, 1, 22, 23])
lcd.init()
lcd.clear()

button_states = [1, 1, 1, 1]

# Function to read button states and send them over ESPNow
def button_interrupt(pin):
    global button_states
    
    # Update the button states based on the current state of all buttons
    button_states[3] = BUTTON_1.value()
    button_states[2] = BUTTON_2.value()
    button_states[1] = BUTTON_3.value()
    button_states[0] = BUTTON_4.value()
    
    # Send button states over ESPNow
    e.send(peer, bytes(button_states))
    #print(bytes(button_states))

# Register interrupt handlers for each button
BUTTON_1.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_interrupt)
BUTTON_2.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_interrupt)
BUTTON_3.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_interrupt)
BUTTON_4.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_interrupt)

# Function to update LCD screen periodically
def update_lcd():
    while True:
        # Update the LCD display with button states
        if button_states[3] == 0:
            lcd.go_to(0, 0)
            lcd.print(" RIGHT   RIGHT   " )
            lcd.go_to(0, 1)
            lcd.print("--> --> --> --> ")
        elif button_states[2] == 0:
            lcd.go_to(0, 0)
            lcd.print(" UP UP UP UP UP   " )
            lcd.go_to(0, 1)
            lcd.print("^ ^ ^ ^ ^ ^ ^ ^ ")
        elif button_states[1] == 0:
            lcd.go_to(0, 0)
            lcd.print("DOWN  DOWN  DOWN  " )
            lcd.go_to(0, 1)
            lcd.print("V V V V V V V V ")
        elif button_states[0] == 0:    
            lcd.go_to(0, 0)
            lcd.print("LEFT  LEFT  LEFT " )
            lcd.go_to(0, 1)
            lcd.print("<-- <-- <-- <--")
        time.sleep(0.2)  # Update the LCD every 0.2 seconds

# Start threads
_thread.start_new_thread(update_lcd, ())

# Main loop
while True:    
    time.sleep_ms(0.01)  # Sleep for a short duration to avoid busy-waiting
    
 