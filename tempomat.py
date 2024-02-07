from math import sin, cos, radians, sqrt
from numpy import linspace
# from simpful import FuzzySystem, LinguisticVariable, FuzzySet, Triangular_MF, Trapezoidal_MF  # fuzzy logic
from skfuzzy.control import Antecedent, Consequent, Rule, ControlSystem, ControlSystemSimulation
from skfuzzy.fuzzymath import fuzzy_ops
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
DOUBLING_TIME = 0.44


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
        self.error_v = None
        self.error_sum_v = None
        self.error_delta_v = None
        self.accel = None
        self.simulation = None

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
        self.dynamics = [0]
        self.acceleration = [0]
        ### ustawianie
        self.sp = [0]
        self.si = [0]
        self.sd = [self.destined_velocity - self.minimal_veocity]
        self.fuzzy_velocity =[]

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
        self.linguistic_variables = ["BN", "N", "Z", "P", "BP"]
        
        self.define_error_variable()
        self.define_error_sum_variable()
        self.define_error_delta_variable()
        self.define_acceleration_variable()

        self.define_rules()

        self.fuzzy_system = ControlSystem(rules=self.rules)
        self.simulation = ControlSystemSimulation(self.fuzzy_system)

    def define_error_variable(self) -> None:
        maximum = (self.destined_velocity - self.minimal_veocity)
        universe = linspace(-maximum, maximum, len(self.linguistic_variables))

        self.error_v = Antecedent(universe, "error")
        self.error_v.automf(names=self.linguistic_variables)

    def define_error_sum_variable(self) -> None:
        maximum = max(self.si[1:])
        universe = linspace(-maximum, maximum, len(self.linguistic_variables))
        
        self.error_sum_v = Antecedent(universe, "error_sum")
        self.error_sum_v.automf(names=self.linguistic_variables)

    def define_error_delta_variable(self) -> None:
        maximum = max(abs(x) for x in self.sd[1:])
        universe = linspace(-maximum, maximum, len(self.linguistic_variables))
        
        self.error_delta_v = Antecedent(universe, "error_delta")
        self.error_delta_v.automf(names=self.linguistic_variables)
    
    def define_acceleration_variable(self) -> None:
        maximum = max(abs(x) for x in self.acceleration)
        universe = linspace(-maximum, maximum, len(self.linguistic_variables))

        self.accel = Consequent(universe, "acceleration")
        self.accel.automf(names=self.linguistic_variables)

    def define_rules(self) -> None:
        self.rules = []
        self.rules.append(Rule(antecedent=((self.error_v['BN'] & self.error_sum_v['BN']) |  #dobrze
                                           (self.error_v['BN'] & self.error_sum_v['N'])  |  #dobrze
                                           (self.error_v['N'] & self.error_sum_v['BN'])  |  #może trzeba będzie rozbić z deltą: BN, N, P, BP
                                           (self.error_v['Z'] & self.error_sum_v['BN'])),   #może trzeba będzie rozbić z deltą: BN, Z, P, BP (?)
                               consequent=self.accel['BN'], label='rule BN'))
        
        self.rules.append(Rule(antecedent=((self.error_v['N'] & self.error_sum_v['N'])  |  #na 99% dobrze 
                                           (self.error_v['Z'] & self.error_sum_v['N'])  |  #na 99% dobrze
                                           (self.error_v['P'] & self.error_sum_v['BN'])),  #może trzeba będzie rozbić z deltą: BN, Z, P, BP (?)                                         
                               consequent=self.accel['N'], label='rule N'))
        
        self.rules.append(Rule(antecedent=((self.error_v['BN'] & self.error_sum_v['Z'])   | #może trzeba będzie rozbić z deltą: BN, Z, P, BP
                                           (self.error_v['BN'] & self.error_sum_v['P'])   | #może trzeba będzie rozbić z deltą: BN, P, BP
                                           (self.error_v['BN'] & self.error_sum_v['BP'])  | #może trzeba będzie rozbić z deltą: BN, Z, P, BP
                                           (self.error_v['N'] & self.error_sum_v['Z'])    | #może trzeba będzie rozbić z deltą: BN, Z, BP
                                           (self.error_v['Z'] & self.error_sum_v['Z'])    | #dobrze
                                           (self.error_v['Z'] & self.error_sum_v['P'])    |  # dobrze
                                           (self.error_v['P'] & self.error_sum_v['N'])    | #może trzeba będzie rozbić z deltą: BN, Z, BP
                                           (self.error_v['BP'] & self.error_sum_v['BN'])  | #dobrze
                                           (self.error_v['BP'] & self.error_sum_v['N'] & self.error_delta_v['Z'])  |
                                           (self.error_v['BP'] & self.error_sum_v['N'] & self.error_delta_v['P'])),
                               consequent=self.accel['Z'], label='rule Z'))
        
        self.rules.append(Rule(antecedent=((self.error_v['N'] & self.error_sum_v['P'])    | #może trzeba będzie rozbić z deltą: BN, N, Z, BP
                                           (self.error_v['N'] & self.error_sum_v['BP'])   | #może trzeba będzie rozbić z deltą: BN, BP (?)
                                           (self.error_v['Z'] & self.error_sum_v['BP'] & self.error_delta_v['BN'])   | #może trzeba będzie rozbić z deltą: BN, Z, P, BP
                                           (self.error_v['P'] & self.error_sum_v['Z'])    | #dobrze
                                           (self.error_v['P'] & self.error_sum_v['P'])    | #dobrze
                                           (self.error_v['BP'] & self.error_sum_v['N']) & self.error_delta_v['BN']   |
                                           (self.error_v['BP'] & self.error_sum_v['N']) & self.error_delta_v['N']   |
                                           (self.error_v['BP'] & self.error_sum_v['N']) & self.error_delta_v['BP']),
                               consequent=self.accel['P'], label='rule P'))
        
        self.rules.append(Rule(antecedent=((self.error_v['P'] & self.error_sum_v['BP'])   | #dobrze
                                           (self.error_v['BP'] & self.error_sum_v['Z'])   | #może trzeba będzie rozbić z deltą: BN, N, P, BP
                                           (self.error_v['BP'] & self.error_sum_v['P'])   | #może trzeba będzie rozbić z deltą: BN, P, BP
                                           (self.error_v['BP'] & self.error_sum_v['BP'])),  #dobrze
                               consequent=self.accel['BP'], label='rule BP'))

    def update_fuzzy_variables(self) -> None:
        for i in range(1, len(self.error)):
            self.simulation.input['error'] = self.sp[i]
            self.simulation.input['error_sum'] = self.si[i]
            self.simulation.input['error_delta'] = self.sd[i]
            self.simulation.compute()
            
            self.dynamics.append(self.simulation.output['acceleration'])
            self.fuzzy_velocity.append(self.fuzzy_velocity[-1] + self.dynamics[-1])

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
            self.fuzzy_velocity.append(self.minimal_veocity)
            self.set_press()
            self.error.append(self.destined_velocity - self.velocity[-1])

    # controller error
    def calc_control(self):
        p = self.error[-1]
        i = self. sampling_time / self.exceding_time * sum(self.error)
        d = self.doubling_time / self.sampling_time * (self.error[-1] - self.error[-2])
        self.sp.append(p)
        self.si.append(i)
        self.sd.append(d)
        # print(f"step: {self.step}, P: {p}, I: {i}, D: {d}")
        self.step += 1
        return self.controler_gain * (p + i + d)
        
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
        self.acceleration.append(max(-self.maximal_acceleration, min(self.calc_resultant_force() / self.mass, self.maximal_acceleration)))
        return max(-self.maximal_acceleration, min(self.calc_resultant_force() / self.mass, self.maximal_acceleration))
    
    def get_plot(self):
        plt.subplot(2, 1, 1)
        plt.plot(self.time, self.sp, label='P')
        plt.plot(self.time, self.si, label='I')
        plt.plot(self.time, self.sd, label='D')
        plt.legend()
        
        plt.subplot(2, 1, 2)
        plt.plot(self.time, self.fuzzy_velocity, label='fuzzy')
        plt.plot(self.time, self.velocity, label='accel')
        plt.legend()
        plt.show()

    # main loop
    def main_loop(self):
        self.initialize_state()
        if self.run:
            for _ in range(self.iterations):
                if abs(round(self.velocity[-1], 1) - self.destined_velocity) < 0.01:
                    print(f"car reached desire velocity at {self.time[-1]}")
                self.time.append(round(self.time[-1] + self.sampling_time, 2))
                self.error.append(self.destined_velocity - self.velocity[-1])
                self.press.append(self.normalize(self.calc_control() / self.destined_velocity, self.calc_minimal_press()))
                self.velocity.append(self.get_valid_acceleration() + self.velocity[-1])
        self.initialize_fuzzy_system()
        self.update_fuzzy_variables()
        


if __name__ == "__main__":
    w = Vehicle(1100, [4.06, 1.94, 1.43], 72, 0.28, 72, 20)
    w.main_loop()
    w.get_plot()
    #f= open("zmienne.txt", "w")
    #for i in range(len(w.acceleration)):
    #    f.write(f"{w.acceleration[i]};{w.sp[i]};{w.si[i]};{w.sd[i]}\n")
        
"""     print(f"press: {}")
    print(f"P: {}")
    print(f"I: {}")
    print(f"D: {}") """
    
#    print(f"time: {w.time}")
#    print(f"error: {w.error}")
#    print(f"press: {w.press}")
#    print(f"velocity: {w.velocity}")
#    print(f"fuzzy accel: {w.dynamics}")