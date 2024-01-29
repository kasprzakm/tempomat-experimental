document.addEventListener('DOMContentLoaded', function () {
    // Fetch initial data from the server
    fetch('/initial_data')
        .then(response => response.json())
        .then(data => {
            // Use Plotly to create initial plots
            var plots = createPlots(data);
            // Plotly.newPlot('plot1', [plots[0]]);
            // Plotly.newPlot('plot2', [plots[1]]);
            // Plotly.newPlot('plot3', [plots[2]]);
            // Plotly.newPlot('plot4', [plots[3]]);

            Plotly.newPlot('plot1', plots[0].traces, plots[0].layout);
            Plotly.newPlot('plot2', plots[1].traces, plots[1].layout);
            Plotly.newPlot('plot3', plots[2].traces, plots[2].layout);
            Plotly.newPlot('plot4', plots[3].traces, plots[3].layout);
        });

    // Function to validate input data
    function isValidNumberWithinLimits(value, min, max) {
        return !isNaN(value) && isFinite(value) && value >= min && value <= max;
    }

    // Apply error style to an input field
    function applyErrorStyle({classList}) {
        classList.add('incorrect-input');
    }

    // Remove error style from an input field
    function removeErrorStyle(inputFieldIds) {
        inputFieldIds.forEach(function (id) {
            var inputField = document.getElementById(id);
            if (inputField) {
                inputField.classList.remove('incorrect-input');
            }
        });
    }

    // Function to update data on click
    window.updateData = function () {
        // Read values from input boxes
        var newParameters = {
            'horsepower': parseFloat(document.getElementById('horsepower').value),
            'mass': parseFloat(document.getElementById('mass').value),
            'length': parseFloat(document.getElementById('length').value),
            'width': parseFloat(document.getElementById('width').value),
            'height': parseFloat(document.getElementById('height').value),
            'speed': parseFloat(document.getElementById('speed').value)
        };

        // Array of input field IDs
        var inputFieldIds = Object.keys(newParameters);
        // Array to store information about invalid inputs
        var invalidInputs = [];

        // Validate input values
        for (var key in newParameters) {
            var inputField = document.getElementById(key);

            switch (key) {
                case 'horsepower':
                    if (!isValidNumberWithinLimits(newParameters[key], 0, 1817)) {
                        invalidInputs.push(key);
                        // applyErrorStyle(document.getElementById('horsepower'));
                        // alert("Please enter valid numerical values for horsepower (0 to 1817 [HP]).");
                        // return;
                    }
                    break;
                case 'mass':
                    if (!isValidNumberWithinLimits(newParameters[key], 0, 20000)) {
                        invalidInputs.push(key);
                        // applyErrorStyle(document.getElementById('mass'));
                        // alert("Please enter valid numerical values for mass (0 to 20000 [kg]).");
                        // return;
                    }
                    break;
                case 'length':
                    if (!isValidNumberWithinLimits(newParameters[key], 0, 20)) {
                        invalidInputs.push(key);
                        // applyErrorStyle(document.getElementById('length'));
                        // alert("Please enter valid numerical values for length (0 to 20 [m]).");
                        // return;
                    }
                    break;
                case 'width':
                    if (!isValidNumberWithinLimits(newParameters[key], 0, 5)) {
                        invalidInputs.push(key);
                        // applyErrorStyle(document.getElementById('width'));
                        // alert("Please enter valid numerical values for width (0 to 5 [m]).");
                        // return;
                    }
                    break;
                case 'height':
                    if (!isValidNumberWithinLimits(newParameters[key], 0, 10)) {
                        invalidInputs.push(key);
                        // applyErrorStyle(document.getElementById('height'));
                        // alert("Please enter valid numerical values for height (0 to 10 [m]).");
                        // return;
                    }
                    break;
                case 'speed':
                    if (!isValidNumberWithinLimits(newParameters[key], 30, 200)) {
                        invalidInputs.push(key);
                        // applyErrorStyle(document.getElementById('speed'));
                        // alert("Please enter a valid numerical value for speed (30 to 200 [km/h]).");
                        // return;
                    }
                    break;
                default:
                    break;
            }

            // If the input is valid, remove the error style
            removeErrorStyle(inputFieldIds);
        }

        // Apply error styles to invalid inputs
        invalidInputs.forEach(function (inputId) {
            var inputField = document.getElementById(inputId);
            if (inputField) {
                applyErrorStyle(inputField);
            }
        });

        // If there are invalid inputs, stop processing
        if (invalidInputs.length > 0) {
            return;
        }

        // Send a POST request to update_data route
        fetch('/update_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newParameters)
        })
        .then(response => response.json())
        .then(updatedData => {
            // Use Plotly to update the existing plots with the new data
            var updatedPlots = createPlots(updatedData);
            // Plotly.react('plot1', [updatedPlots[0]]);
            // Plotly.react('plot2', [updatedPlots[1]]);
            // Plotly.react('plot3', [updatedPlots[2]]);
            // Plotly.react('plot4', [updatedPlots[3]]);

            Plotly.react('plot1', updatedPlots[0].traces, updatedPlots[0].layout);
            Plotly.react('plot2', updatedPlots[1].traces, updatedPlots[1].layout);
            Plotly.react('plot3', updatedPlots[2].traces, updatedPlots[2].layout);
            Plotly.react('plot4', updatedPlots[3].traces, updatedPlots[3].layout);
        });
    };

    // Function to create Plotly TEST plots
    function createTestPlots(data) {
        var squareLayout = {
            width: 300,
            height: 300,
            margin: { l: 30, r: 30, b: 30, t: 30 }
        };
        var layout = {
            grid: {rows: 2, columns: 2, pattern: 'M'},
            width: 600,
            height: 600
        };

        // TODO replace with actual plots config
        var plot1 = {
            x: data.x,
            y: data.y,
            type: 'scatter',
            mode: 'lines',
            name: 'Plot 1',
        };

        var plot2 = {
            x: data.x,
            y: data.y,
            type: 'scatter',
            mode: 'lines',
            name: 'Plot 2',
        };

        var plot3 = {
            x: data.x,
            y: data.y,
            type: 'scatter',
            mode: 'lines',
            name: 'Plot 3',
        };

        var plot4 = {
            x: data.x,
            y: data.y,
            type: 'scatter',
            mode: 'lines',
            name: 'Plot 4',
        };

        // Plots grid
        plot1.subplot = 'xy';
        plot2.subplot = 'xy2';
        plot3.subplot = 'xy3';
        plot4.subplot = 'xy4';

        return [plot1, plot2, plot3, plot4];
    }

    // Function to create Plotly plots based on data
    function createPlots(data) {
        var layout = {
            // width: 800,
            //height: 400,
            margin: { l: 50, r: 50, b: 50, t: 50 },
        };

        var plot1 = {
            x: data.x,
            y: data.y1,
            type: 'scatter',
            mode: 'lines',
            name: 'Error',
            title: 'Controler Error',
            xaxis: { title: 'time [s]' },
            yaxis: { title: 'error [m/s]' },
        };

        var plot2 = {
            x: data.x,
            y: data.y2,
            type: 'scatter',
            mode: 'lines',
            name: 'Press',
            title: 'Gas Pedal Pressure Level',
            xaxis: { title: 'time [s]' },
            yaxis: { title: 'press level [%]' },
        };

        var plot3 = {
            x: data.x,
            // y: data.y3,
            y: data.y3.map(value => value * 3.6),
            type: 'scatter',
            mode: 'lines',
            name: 'Velocity',
            title: 'Vehicle Velocity',
            xaxis: { title: 'time [s]' },
            yaxis: { title: 'velocity [m/s]' },
        };

        var plot4 = {
            x: data.x,
            y: data.y4,
            type: 'scatter',
            mode: 'lines',
            name: 'Fuzzy',
            title: 'Controler Fuzzy Logic Levels',
            xaxis: { title: 'x' },
            yaxis: { title: 'y' },
        };

        // return [plot1, plot2, plot3, plot4];
        return [
            { traces: [plot1], layout: { ...layout, title: 'Controler Error', xaxis: { title: 'time [s]' }, yaxis: { title: 'error [m/s]' } } },
            { traces: [plot2], layout: { ...layout, title: 'Gas Pedal Pressure Level', xaxis: { title: 'time [s]' }, yaxis: { title: 'press level [%]' } } },
            { traces: [plot3], layout: { ...layout, title: 'Vehicle Velocity', xaxis: { title: 'time [s]' }, yaxis: { title: 'velocity [m/s]' } } },
            { traces: [plot4], layout: { ...layout, title: 'Controler Fuzzy Logic Levels', xaxis: { title: 'x' }, yaxis: { title: 'y' } } },
        ];
    }
});
