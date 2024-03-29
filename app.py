from flask import Flask, render_template, jsonify, request
import numpy as np
from tempomat import Vehicle


app = Flask(__name__)

# Initial parameters
initial_parameters = {
    'horsepower': 100,
    'mass': 1000,
    'width': 1.9,
    'length': 4,
    'height': 1.2,
    'speed': 50
}

# Generic test data generator
def generate_test_data(horsepower, mass, width, length, height, speed):
    x = np.linspace(0, 10, 100)
    y = horsepower * np.sin(x) + speed
    return {'x': x.tolist(), 'y': y.tolist()}

# Original data generator
def generate_data(horsepower, mass, width, length, height, speed):
    print(horsepower, mass, width, height, length, speed)

    # Initializing object constructor based on prepared module
    v = Vehicle(mass, [width, length, height], horsepower, 0.28, speed, 90)

    # test_dimensions = tuple([1.94, 4.06, 1.43])
    # v = Vehicle(1100, test_dimensions, 102, 0.28, 20, 1000)

    # Initializing function generating data for plots
    v.main_loop()

    # Just checking if module func works...
    print('time samples:', v.time[0], '|', v.time[-1], '|', len(v.time))
    # print('controler error:', v.error[0], '|', v.error[-1], '|', len(v.error))
    print('velocity:', v.velocity[0], '|', v.velocity[-1], '|', len(v.velocity))
    print('fuzzy velocity:', v.fuzzy_velocity[0], '|', v.fuzzy_velocity[-1], '|', len(v.fuzzy_velocity))

    print('acceleration', v.acceleration[0], '|', v.acceleration[-1], '|', len(v.acceleration))
    print('fuzzy acceleration', v.dynamics[0], '|', v.dynamics[-1], '|', len(v.dynamics))

    print('press level:', v.press[0], '|', v.press[-1], '|', len(v.press))

    print('weight:', v.weight[0], '|', v.weight[-1], '|', len(v.weight))
    print('friction:', v.friction[0], '|', v.friction[-1], '|', len(v.friction))
    print('air_drag_force:', v.air_drag_force[0], '|', v.air_drag_force[-1], '|', len(v.air_drag_force))
    print('driving_force:', v.driving_force[0], '|', v.driving_force[-1], '|', len(v.driving_force))
    print('reluctant_force:', v.resultant_force[0], '|', v.resultant_force[-1], '|', len(v.resultant_force))

    return dict(
        x=v.time,
        y1=v.velocity,
        y2=v.fuzzy_velocity,
        y3=v.acceleration,
        y4=v.dynamics,
        y5=v.press,
        y6=v.weight,
        y7=v.friction,
        y8=v.air_drag_force,
        y9=v.driving_force,
        y10=v.resultant_force
    )

# Default data initializer
# initial_data = generate_test_data(**initial_parameters)
initial_data = generate_data(**initial_parameters)


# Routes
@app.route('/')
def index():
    return render_template('index.html', initial_parameters=initial_parameters, initial_data=initial_data)

@app.route('/initial_data')
def get_initial_data():
    print(f"json: {jsonify(initial_data)}")
    return jsonify(initial_data)

@app.route('/update_data', methods=['POST'])
def update_data():
    new_parameters = request.json
    #new_data = generate_test_data(**new_parameters)
    new_data = generate_data(**new_parameters)
    return jsonify(new_data)

if __name__ == '__main__':
    app.run(debug=True)