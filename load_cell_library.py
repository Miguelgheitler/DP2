import qwiic_nau7802
import time

class Load_Cell_Sensor:
    def __init__(self):
        self.my_scale = None
        self.zero_offset = None
        self.calibration_factor = None
        self.current_weight = 0  
        self.last_time = time.time()  # Store the last time weight was incremented


    '''
    These methods are intended for use with the PHYSICAL load
    Your code should include these methods if running off of a Raspberry Pi
    '''
    def begin(self):
        self.my_scale = qwiic_nau7802.QwiicNAU7802()
        self.my_scale.begin()

    def set_zero_offset(self, zero_offset):
        self.zero_offset = int(zero_offset)
        self.my_scale.set_zero_offset(self.zero_offset)

    def set_calibration_factor(self, calibration_factor):
        self.calibration_factor = float(calibration_factor)
        self.my_scale.set_calibration_factor(self.calibration_factor)

    def get_weight(self):
        return round(self.my_scale.get_weight())


    '''
    This method simulates weight being added to a load cell
    You should call this method when NOT using the Raspberry Pi
    '''
    def get_virtual_weight(self, start_weight, step=None):
        # No step argument -> hold weight constant
        if step is None:
            return start_weight
        
        if start_weight > 90 or start_weight < 0:
            print("******INVALID START WEIGHT. MUST BE 0-90. TERMINATING.******")
            return

        current_time = time.time()
        if self.current_weight == 0:  # First call 
            self.current_weight = start_weight

        # Increment by 10g if "step" seconds have passed since last increment
        if current_time - self.last_time >= step:
            self.current_weight += 10
            self.last_time = current_time  # Reset last_time to now

        # Weight can only be 0-90
        self.current_weight = min(max(self.current_weight, 0), 90)

        return round(self.current_weight)
