from math import sin, cos, radians, sqrt
from numpy import linspace
from simpful import FuzzySystem, LinguisticVariable, FuzzySet, Triangular_MF, Trapezoidal_MF  # fuzzy logic
import matplotlib.pyplot as plt

# TODO - consider using dict for different coefficients (e.g. friction (dry, wet, ice), drag (different cars))
HORSEPOWER = 735  # 1 HP in [Nm/s]
GRAVITY_COEFF = 9.81
FRICTION_COEFF = 0.7  # dry asphalt coeff
DRAG_COEF = 0.3  # average drag coeff for cars
AIR_DENSITY = 1.293  # average air density
INCLINATION = 0
MINIMAL_VELOCITY = 8.3
SAMPLING_TIME = 0.1
GAIN = 0.05
EXCEDING_TIME = 0.4
DOUBLING_TIME = 0.4


class Vehicle:
    def __init__(self, mass: int, dims: list, power: int, wheel_radius: float, destined_velocity: float,
                 runtime: int) -> None:
        self.mass = mass
        self.dims = dims
        self.horsepower = power
        self.wheel_radius = wheel_radius
        self.minimal_veocity = MINIMAL_VELOCITY
        self.destined_velocity = destined_velocity / 3.6
        self.frontal_area = None
        self.maximal_acceleration = None
        self.fuzzy_system = None
        self.linguistic_variables = None
        self.rules = None
        self.step = 0

        self.run = True
        self.runtime = runtime
        self.sampling_time = SAMPLING_TIME
        self.controler_gain = GAIN
        self.exceding_time = EXCEDING_TIME
        self.doubling_time = DOUBLING_TIME
        self.iterations = None
        self.time = []
        self.velocity = []
        self.press = []
        self.error = []
        self.dynamics = []
        ### ustawianie
        self.static_error = [1]
        self.sp = [0]
        self.si = [0]
        #self.sd = []
        

    # utils
    def normalize(self, press, minimum=0.0) -> float:
        return max(0.0, min(minimum + press, 1.0))

    def calc_iterations(self) -> None:
        self.iterations = int(self.runtime // self.sampling_time)

    def validate(self) -> None:
        if self.mass < 0:
            self.run = False
            print(f"Vehicle mass cannot be negative")
        if len(self.dims) != 3:
            self.run = False
            print(f"Invalid dimensions")
        if self.horsepower < 0:
            self.run = False
            print(f"Horsepower cannot be negative")
        if self.wheel_radius <= 0 or self.wheel_radius > 1:
            self.run = False
            print(f"Invalid wheel radius")
        if self.destined_velocity < 0:
            self.run = False
            print(f"Vehicle desire velocity cannot be negative")

    # set initial values for vehicle
    def initialize_fuzzy_system(self) -> None:
        self.fuzzy_system = FuzzySystem()

        self.define_error_variable()
        self.define_press_variable()
        self.define_acceleration_variable()

        self.define_rules()

        self.fuzzy_system.set_variable("Err_value", self.error[-1])
        self.fuzzy_system.set_variable("Pedal_press", self.press[-1])

    def define_error_variable(self) -> None:
        maximum = (self.destined_velocity - self.minimal_veocity) * 3.6
        steps = linspace(maximum, -maximum / 4, 5)

        high = FuzzySet(function=Trapezoidal_MF(steps[4], steps[4], steps[3], steps[2]), term="low")
        medium = FuzzySet(
            function=Trapezoidal_MF(steps[3], (steps[3] + steps[2]) / 2, (steps[2] + steps[1]) / 2, steps[1]),
            term="medium")
        low = FuzzySet(function=Trapezoidal_MF(steps[2], steps[1], steps[0], steps[0]), term="high")
        # print(low.get_value_fast('Err_value'))
        self.fuzzy_system.add_linguistic_variable("Err_value", LinguisticVariable([high, medium, low],
                                                                                  universe_of_discourse=[maximum,
                                                                                                         -maximum / 4]))

    def define_press_variable(self) -> None:
        low = FuzzySet(function=Triangular_MF(0.0, 0.25, 0.5), term="low")
        medium = FuzzySet(function=Triangular_MF(0.25, 0.5, 0.75), term="medium")
        high = FuzzySet(function=Trapezoidal_MF(0.5, 0.75, 1.0, 1.0), term="high")
        self.fuzzy_system.add_linguistic_variable("Pedal_press", LinguisticVariable([low, medium, high],
                                                                                    universe_of_discourse=[0.0, 1.0]))

    def define_acceleration_variable(self) -> None:
        steps = linspace(-self.maximal_acceleration, self.maximal_acceleration, 7)

        high_negative = FuzzySet(function=Trapezoidal_MF(steps[0], steps[0], steps[1], steps[2]), term="high_negative")
        average_negative = FuzzySet(function=Triangular_MF(steps[1], steps[2], steps[3]), term="average_negative")
        low_neutral = FuzzySet(function=Triangular_MF(steps[2], steps[3], steps[4]), term="low_neutral")
        average_positive = FuzzySet(function=Triangular_MF(steps[3], steps[4], steps[5]), term="average_positive")
        high_positive = FuzzySet(function=Trapezoidal_MF(steps[4], steps[5], steps[6], steps[6]), term="high_positive")
        self.fuzzy_system.add_linguistic_variable("Acceleration", LinguisticVariable(
            [high_negative, average_negative, low_neutral, average_positive, high_positive],
            universe_of_discourse=[-self.maximal_acceleration, self.maximal_acceleration]))

    def define_rules(self) -> None:
        self.rules = []
        self.rules.append("IF (Err_value IS high) AND ( Pedal_press IS high) THEN (Acceleration IS high_positive))")
        self.rules.append(
            "IF (Err_value IS high) AND ( Pedal_press IS medium) THEN (Acceleration IS average_positive))")
        self.rules.append("IF (Err_value IS high) AND ( Pedal_press IS low) THEN (Acceleration IS high_negative))")
        self.rules.append(
            "IF (Err_value IS medium) AND ( Pedal_press IS high) THEN (Acceleration IS average_positive))")
        self.rules.append(
            "IF (Err_value IS medium) AND ( Pedal_press IS medium) THEN (Acceleration IS average_positive))")
        self.rules.append("IF (Err_value IS medium) AND ( Pedal_press IS low) THEN (Acceleration IS average_negative))")
        self.rules.append("IF (Err_value IS low) AND ( Pedal_press IS high) THEN (Acceleration IS high_positive))")
        self.rules.append("IF (Err_value IS low) AND ( Pedal_press IS medium) THEN (Acceleration IS average_positive))")
        self.rules.append("IF (Err_value IS low) AND ( Pedal_press IS low) THEN (Acceleration IS low_neutral))")
        self.fuzzy_system.add_rules(self.rules)

    def update_fuzzy_variables(self) -> None:
        accel = self.fuzzy_system.inference()
        self.dynamics.append(accel["Acceleration"])

        self.fuzzy_system._variables["Err_value"] = self.error[-1]
        self.fuzzy_system._variables["Pedal_press"] = self.press[-1]

    def calc_frontal_area(self) -> None:
        self.frontal_area = round(self.dims[1] * self.dims[2], 2)

    def calc_max_accleration(self) -> None:
        self.maximal_acceleration = sqrt((self.horsepower * HORSEPOWER) / (2 * self.mass))

    def set_press(self) -> None:
        weight = self.calc_weight()
        friction = self.calc_friction()
        drag = self.calc_drag()
        #  print(f"weight: {weight}N, friction: {friction}N, drag: {drag}N, total: {weight + friction + drag}N ")
        driving = self.calc_driving_force(1)
        #  print(f"driving force: {driving}N")
        press = (weight + friction + drag) / driving
        #  print(f"press: {press * 100}%")
        self.press.append(self.normalize(press))

    def calc_minimal_press(self) -> float:
        # print(f"minimal press: {(self.calc_weight() + self.calc_friction() + self.calc_drag()) / self.calc_driving_force(1)}")
        return (self.calc_weight() + self.calc_friction() + self.calc_drag()) / self.calc_driving_force(1)

    def initialize_state(self) -> None:
        self.validate()
        if self.run:
            self.calc_iterations()
            self.calc_frontal_area()
            self.calc_max_accleration()
            self.time.append(0.0)
            self.velocity.append(self.minimal_veocity)
            self.set_press()
            self.error.append(self.destined_velocity - self.velocity[-1])

    # controler error
    def calc_control(self):
        p = self.error[-1]
        i = self. sampling_time / self.exceding_time * sum(self.error)
        d = self.doubling_time / self.sampling_time * (self.error[-1] - self.error[-2])
        # print(f"step: {self.step}, P: {p}, I: {i}, D: {d}")
        self.step += 1
        return (self.controler_gain * (p + i + d))
        
    # calculate forces

    def calc_weight(self) -> float:
        return self.mass * GRAVITY_COEFF * sin(radians(INCLINATION))

    def calc_friction(self) -> float:
        return self.mass * GRAVITY_COEFF * FRICTION_COEFF * cos(radians(INCLINATION))

    def calc_drag(self) -> float:
        return (DRAG_COEF * AIR_DENSITY * self.frontal_area * self.velocity[-1] ** 2) / 2

    def calc_driving_force(self, press) -> float:
        return (HORSEPOWER * self.horsepower * press) / (self.velocity[-1] * self.wheel_radius)

    def calc_resultant_force(self) -> float:
        # print(f"rforce: {self.calc_driving_force(self.press[-1]) - (self.calc_weight() + self.calc_friction() + self.calc_drag())}")
        return self.calc_driving_force(self.press[-1]) - (self.calc_weight() + self.calc_friction() + self.calc_drag())

    def get_valid_acceleration(self) -> float:
        # print(f"acel: {max(-self.maximal_acceleration, min(self.calc_resultant_force() / self.mass, self.maximal_acceleration))}")
        return max(-self.maximal_acceleration, min(self.calc_resultant_force() / self.mass, self.maximal_acceleration))

    # main loop
    def main_loop(self):
        self.initialize_state()
        self.initialize_fuzzy_system()
        if self.run:
            for _ in range(self.iterations):
                if abs(round(self.velocity[-1], 1) - self.destined_velocity) < 0.01:
                    print(f"car reached desire velocity at {self.time[-1]}")
                self.time.append(round(self.time[-1] + self.sampling_time, 2))
                self.error.append(self.destined_velocity - self.velocity[-1])
                self.press.append(self.normalize(self.calc_control() / self.destined_velocity, self.calc_minimal_press()))
                self.velocity.append(self.get_valid_acceleration() + self.velocity[-1])
                self.update_fuzzy_variables()


#if __name__ == "__main__":
#    w = Vehicle(1100, [4.06, 1.94, 1.43], 102, 0.28, 50, 20)
#    w.main_loop()
#    w.get_plot()
#    
#    print(f"time: {w.time}")
#    print(f"error: {w.error}")
#    print(f"press: {w.press}")
#    print(f"velocity: {w.velocity}")
#    print(f"fuzzy accel: {w.dynamics}")