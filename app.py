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
    'speed': 20
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
    v = Vehicle(mass, [width, length, height], horsepower, 0.28, speed, 1000)

    # test_dimensions = tuple([1.94, 4.06, 1.43])
    # v = Vehicle(1100, test_dimensions, 102, 0.28, 20, 1000)

    # Initializing function generating data for plots
    v.main_loop()

    # Just checking if module func works...
    print('time samples:', v.time[0], '|', v.time[-1], '|', len(v.time))
    print('controler error:', v.error[0], '|', v.error[-1], '|', len(v.error))
    print('press level:', v.press[0], '|', v.press[-1], '|', len(v.press))
    print('velocity:', v.velocity[0], '|', v.velocity[-1], '|', len(v.velocity))
    print('fuzzy samples:', v.dynamics[0], '|', v.velocity[-1], '|', len(v.dynamics))

    return {'x': v.time, 'y1': v.error, 'y2': v.press, 'y3': v.velocity, 'y4': v.dynamics}


# Default data initializer
# initial_data = generate_test_data(**initial_parameters)
initial_data = generate_data(**initial_parameters)


# Routes
@app.route('/')
def index():
    return render_template('index.html', initial_parameters=initial_parameters, initial_data=initial_data)

@app.route('/initial_data')
def get_initial_data():
    return jsonify(initial_data)

@app.route('/update_data', methods=['POST'])
def update_data():
    new_parameters = request.json
    #new_data = generate_test_data(**new_parameters)
    new_data = generate_data(**new_parameters)
    return jsonify(new_data)

if __name__ == '__main__':
    app.run(debug=True)