import time
import board
import digitalio
import busio
import adafruit_ssd1306

VAL_DRY = 2.0
VAL_DAMP = 17.5
VAL_WET = 35.0

# setup pin, copper pad is wired to D0 and to GND through a ~1M Ohm resistor
touch_pin = board.D0
soil_pin = board.D1

last_touch = [False, 0] # [is_touching, timestamp]
oled_raw_mode = False
DEBOUNCE_DELAY = 0.15

# initialize 0.91 inch OLED  
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

def read_capsense_raw(pin_name, samples=10, charge_delay = 0.0001):
    """
    Measures capacitance of a pin by timing how long it takes to discharge via RC filter circuit through an external pull-down resistor.

    Timing is given by the function t = R * C, where R is resistance and C is capacitance
    """

    total_cycles = 0

    # multiple samples for mean measurement
    for _ in range(samples):
        # 1. charge pad up to 3.3V (pull HIGH)
        with digitalio.DigitalInOut(pin_name) as pin:
            pin.direction = digitalio.Direction.OUTPUT
            pin.value = True
            time.sleep(charge_delay) # short pause to ensure full charge

            # 2. switch instantly to an INPUT (high impedance)
            pin.direction = digitalio.Direction.INPUT
            pin.pull = None # no internal pull-up/pull-down

            # 3. measure how long it takes to drain to ground
            # a finger near the copper pad increases the capacitance, which slows drain and increases cycle count
            cycles = 0
            while pin.value:
                cycles += 1
                # optional safety breakout to prevent infinite loops if pin fails
                if cycles > 3000:
                    break
            
            total_cycles += cycles
    
    return total_cycles / samples

def map_value(x, in_min, in_max, out_min, out_max):
    if in_max == in_min: # prevent divide by 0
        return out_min
    return (x-in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def get_piecewise_moisture(raw):
    if raw <= VAL_DRY:
        return 0.0
    elif raw >= VAL_WET:
        return 100.0
    
    # map from dry to damp
    if raw < VAL_DAMP:
        return map_value(raw, VAL_DRY, VAL_DAMP, 0.0, 50.0)
    # map from damp to wet
    else:
        return map_value(raw, VAL_DAMP, VAL_WET, 50.0, 100.0)

print("Calibrating baseline... Do not touch the pad.")
baseline = 0.0
for _ in range(20):
    baseline += read_capsense_raw(touch_pin)
    time.sleep(0.01)
baseline /= 20.0

print(f"Baseline software cycles: {baseline:.1f}")

while True:
    raw_val = read_capsense_raw(touch_pin)
    delta = raw_val - baseline

    # raw cycles > 10 = soil wet!
    soil_raw_val = read_capsense_raw(soil_pin, samples=100, charge_delay = 0.001)
    moisture_pct = get_piecewise_moisture(soil_raw_val)

    if moisture_pct < 35.0:
        status = "DRY"
    elif moisture_pct < 75.0:
        status = "DAMP"
    else:
        status = "TOO WET"

    print(f"Raw Cycles: {raw_val:.1f} | Delta: {delta:.1f} | Soil Raw Cycles: {soil_raw_val:.1f}")

    # update OLED display
    oled.fill(0)

    if oled_raw_mode:
        oled.text(f"Touch Raw (Hz): {raw_val:.1f}", 0, 0, 1)
        oled.text(f"Touch Delta: {delta:.1f}", 0, 11, 1)
        oled.text(f"Soil Raw (Hz): {soil_raw_val:.1f}", 0, 22, 1)
    else:
        # Header
        oled.text("SOIL MOISTURE", 0, 0, 1)
        oled.line(0, 10, 128, 10, 1)

        oled.text(f"Moist: {moisture_pct:.1f}% | {status}", 0, 13, 1)

        bar_width = int(map_value(moisture_pct, 0, 100, 0, 120))
        oled.rect(0, 25, 120, 8, 1)
        oled.fill_rect(2, 27, bar_width, 4, 1)

    oled.show()

    if delta > 1.5:
        print("🔴 Touch Detected!")

        # debouncer for capacitive touch - toggling OLED display mode
        if not last_touch[0] and time.time() - last_touch[1] >= DEBOUNCE_DELAY:
            last_touch = [True, time.time()]
    else:
        if last_touch[0] and time.time() - last_touch[1] >= DEBOUNCE_DELAY:
            last_touch = [False, time.time()]
            oled_raw_mode = not oled_raw_mode

    time.sleep(0.05)
