from matplotlib import pyplot as plt
from load_cell_library import Load_Cell_Sensor
import time
import math
from gpiozero import LED

#Miguel Gonzalez 400529229
#calculating resultant tensile stress of implant stem and bone:
def applied_load(s_val):
    n = s_val/10   #number of 10g weights
    load = mass*n*g  #force on femoral head
    return round(load, 1)


#calculating elastic modulus of bone
def em_b(a):
    modulus_b = None
    if a <= 40:
        modulus_b = 17
    else:  #(if age is greater than 40)
        if s == 'male':        #if sex of patient is male
            modulus_b = -0.123 * (a - 40) + 17
        elif s == 'female':    #if sex of patient is female
            modulus_b = -0.196 * (a - 40) + 17
        else:
            print("Invalid s value. Must be either 'male' or 'female'")

    return round(modulus_b, 1)


def result_tens_stress_b(load, e_b):
    #properties of bone
    bone_area = (math.pi/4)*(dia_o**2-dia_i**2) # A
    moment_of_inertia_bone = (math.pi/64)*(dia_o**4-dia_i**4) # I

    #calculating tensile stress on bone 
    axial_stress_bone = -load / bone_area
    bending_stress_bone = (load * fem_offset * dia_o / 2) / moment_of_inertia_bone

    tensile_stress_bone = axial_stress_bone + bending_stress_bone

    #calculating resultant stress on bone
    resultant_stress_bone = tensile_stress_bone * ((3 * e_b) / (e_b + E_s)) ** (1 / 4)

    return round(resultant_stress_bone, 1) 


def result_tens_stress_s(load, e_b):
    #properties of stem
    stem_area = (math.pi/4)*(dia_s**2)
    moment_of_inertia_stem = (math.pi/64)*(dia_s**4)
    
    #calculating tensile stress on stem
    axial_stress_stem = -load / stem_area
    bending_stress_stem = (load * fem_offset * (dia_s / 2)) / moment_of_inertia_stem #(half stem diameter is neutral axis distance)

    tensile_stress_stem = axial_stress_stem + bending_stress_stem
    
    #resultant stress of stem
    resultant_stress_stem = tensile_stress_stem * (1 - (3 * e_b / (e_b + E_s))) ** 1 / 4

    return round(resultant_stress_stem, 1)

#Andrew Lian 400567387
def uts(mths, e_implant, e_bone):
    e_ratio = math.sqrt(e_implant/e_bone)
    tensile_strength = 175/(1+0.05*math.e**(0.06*(mths)*e_ratio))

    return round(tensile_strength, 1)

#Andrew Lian 400567387
def plot_chart(t_post_op, r_stress, ultimate_strength):
    fig, axes = plt.subplots(figsize=(8, 4))

    axes.plot(t_post_op, ultimate_strength, label='Ultimate tensile strength in bone (UTSb)')
    axes.plot(t_post_op, r_stress, label='Resultant tensile stress in bone (σ resb)')

    axes.set(xlabel='Time (Years Post-Surgery)', ylabel='Stress (MPa)')
    axes.legend(loc='upper right')

    plt.title('Stress vs Time Post Surgery')
    plt.minorticks_on()
    plt.grid(which='both', axis='both')
    plt.show()

#Andrew Lian 400567387 & Miguel Gonzalez 400529229
def read_load():
    global sensor_val, mths_postop #updates global variables

    # header row
    headers = ['mths', 'applied load', 'Res. stress, bone', 'Res. stress, stem', 'E, bone', 'UTS, bone']
    print(' '.join(header.ljust(20) for header in headers))

    #make sure LEDs are off
    red_led.off()
    green_led.off()
    yellow_led.off()

    while True:
        sensor_val = load_sensor.get_weight()
        #sensor_val = load_sensor.get_virtual_weight(10, 1)    #virtual sensor (used for testing)
        load = applied_load(sensor_val)

        #creating a chart of data and plotting UTS and Result-stress vs years
        if sensor_val > 0:
            mths_postop += 1
            e_b = em_b(age + mths_postop/12)

            dataset[0].append(round(mths_postop, 1))
            dataset[1].append(load)
            dataset[2].append(result_tens_stress_b(load, e_b))
            dataset[3].append(result_tens_stress_s(load, e_b))
            dataset[4].append(e_b)
            dataset[5].append(uts(mths_postop/12, E_s, e_b))

            print(' '.join(str(data).ljust(20) for data in [*map(lambda data: data[-1], dataset)]))


        #Miguel Gonzalez 400529229
        #LED outputs
        if dataset[2][mths_postop - 1] < 0.1*dataset[5][mths_postop - 1]:
            green_led.on()
            yellow_led.off()
            red_led.off()

        elif 0.1*dataset[5][mths_postop - 1] <= dataset[2][mths_postop - 1] < 0.5*dataset[5][mths_postop - 1]:
            green_led.off()
            yellow_led.on()
            red_led.off()

        elif 0.5 * dataset[5][mths_postop - 1] <= dataset[2][mths_postop - 1] < dataset[5][mths_postop -1]:
            green_led.off()
            yellow_led.off()
            red_led.on()

        else:     #if resultant stress of bone is >= to UTS
            if red_led.is_lit: red_led.off()
            red_led.blink(0.05)
            green_led.off()
            yellow_led.off()


        #Andrew Lian
        if len(dataset[0]) == 360:
            plot_chart([*map(lambda data: data/12, dataset[0])], dataset[2], dataset[5])
            
            #resets all LEDs to 'off' status
            green_led.off()
            yellow_led.off()
            red_led.off()
            return

        time.sleep(0)

#Miguel Gonzalez 400529229
#defining variables:

#Gravitational Constant
g = 9.81
#assigned patient data
age = 51 #(years)
mass = 111 #(kg)
s = 'male'
#Femoral Bone Morphology
dia_o = 33 #(mm)
dia_i = 19 #(mm)
fem_offset = 47

#Implant Design Parameters
dia_s = 33
E_s = 105 #elastic modulus of Ti-6Al-7Nb

#load cell data
sensor_val = 0
mths_postop = 0
zero_offset = 107832.875
calibration_factor = 424.93263888

#setting LED pins of each colour
green_led = LED(26)
yellow_led = LED(20)
red_led = LED(16)

#Andrew Lian
dataset = [[], [], [], [], [], []] # define dataset to store calculated stress values

#initialize sensor
load_sensor = Load_Cell_Sensor()
load_sensor.begin()
load_sensor.set_zero_offset(zero_offset)
load_sensor.set_calibration_factor(calibration_factor)

read_load()