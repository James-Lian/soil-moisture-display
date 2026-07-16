# Soil Moisture/Humidity Display
A PCB project for sensing soil humidity levels using custom PCB capacitive sensors made from RC circuits and copper pads. 

<img width="545" height="789" alt="image" src="https://github.com/user-attachments/assets/ef3600cf-413b-4315-9253-ca38dd2f8427" />

## ⚡ In Action
### Features
- OLED display (% moisture level, status level, + raw timing cycles and other firmware data)
- custom capacitive touch sensor (copper pad - used to toggle OLED mode)
- custom capacitive soil moisture sensor (copper electrodes)

### How does it work?
<img width="490" height="322" alt="image" src="https://github.com/user-attachments/assets/f6ebe748-32d5-4eb1-9134-5d872578f369" />
The touch sensor is wired like so: 
<br>
```
MCU pin --> copper pad (capacitor) --> 1 MΩ resistor --> GND
```
<br>
Since a capacitor is fundamentally two conductors separated by an insulating material, when your finger (a conductor) approaches the copper pad, the copper pad + the air/silkscreen of the PCB + your finger form a capacitor! The closer your finger is, the higher the capacitance will be.<br>This circuit is what we call an RC (resistor-capacitor) circuit. In an RC circuit, the time it takes for a capacitor to discharge is determined by the formula t = R * C (time = resistance * capacitance). Therefore, if we can measure when the time for discharge has increased, we will know when our finger is touching the sensor!<br>To do so, in the firmware, we first drive the MCU pin HIGH, then we immediately switch the MCU pin to INPUT and count the number of cycles it takes for the pin to read LOW. When the number of cycles increases, that means that the sensor was touched.   <img width="1060" height="649" alt="image" src="https://github.com/user-attachments/assets/df0658fd-a0ab-4c4f-b1a5-e66058a5871c" />
<br>
<br>
The soil moisture sensor fundamentally relies on the same principle. However, this time, instead of having just one copper pad, we use two finger-shaped interdigiated copper electrodes, wired like so:
<br>
```
MCU pin --> 1 MΩ resistor --> copper electrode #1 --> copper electrode #2 --> GND
                 |
                 ↓
                GND
```
Since the two copper electrodes are interdigiated, the insulator of this custom "capacitor" will be the dielectric soil surrounding the probes. When the soil is moistened with water, however, capacitance will increase dramatically. This is because water has a very high dielectric constant (due to the water molecule's strong dipole behaviour + polarizability).

All in all, there are a two main factors to consider regarding capacitance when making custom PCB capacitive sensors:
- distance (more distance decreases capacitance)
- dielectric constant
Something interesting to note is that the capacitors created using these methods (flat copper islands) will usually be very weak (picofarads in terms of strength). In order to remedy that, we need to balance it with a super high resistance value in order to get a large enough time value in the t = R x C formulaf or us to measure. 

## 💾 List of Components
- through-hole 1 MΩ resistors
- 0.91 inch OLED I2C
- Seeed Seeeduino Xiao Rp2040
- copper pads are placed on the PCB design

## 🕹️Try it out!
Here's how to use the sensor yourself.
1. Download the production folder
2. Go to a PCB manufacturer like JLCPCB and upload the gerbers, and the bom.csv + designators.csv if you're ordering PCB assembly
3. If you didn't order PCB assembly, solder the components to the PCB when it arrives
4. Download the .uf2 file from [https://circuitpython.org/board/seeeduino_xiao_rp2040/](https://circuitpython.org/board/seeeduino_xiao_rp2040/) and the [Adafruit CircuitPython Library Bundle](https://circuitpython.org/libraries), and the [font5x8.bin](https://github.com/adafruit/Adafruit_CircuitPython_framebuf/blob/main/examples/font5x8.bin) file
5. Connect the Seeeduino XIAO RP2040 to your computer while holding B (BOOT) button on the chip in order to put your XIAO into Bootloader mode to flash new firmware
6. Upload the code from this repo to code.py on the Seeeduino USB, and add the font5x8.bin file to the root
7. Drag and drop the adafruit_ssd1306.mpy and adafruit_framebuf.mpy from the library bundle .zip to the lib folder on the XIAO

## 📃 Credits
Much thanks to sjm4306's video [DIY Capacitive Touch PCBs](https://www.youtube.com/watch?v=FjcVGP6vktM)! He does a great job explaining the basis of how the capacitive sensors work to detect touch. 
