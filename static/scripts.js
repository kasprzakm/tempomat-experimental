document.addEventListener('DOMContentLoaded', function () {
    // Fetch initial data from the server
    fetch('/initial_data')
        .then(response => response.json())
        .then(data => {
            // Use Plotly to create initial plots
            var plots = createPlots(data);
            Plotly.newPlot('plot1', [plots[0]]);
            Plotly.newPlot('plot2', [plots[1]]);
            Plotly.newPlot('plot3', [plots[2]]);
            Plotly.newPlot('plot4', [plots[3]]);
        });

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
            Plotly.react('plot1', [updatedPlots[0]]);
            Plotly.react('plot2', [updatedPlots[1]]);
            Plotly.react('plot3', [updatedPlots[2]]);
            Plotly.react('plot4', [updatedPlots[3]]);
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
        var plot1 = {
            x: data.x,
            y: data.y1,
            type: 'scatter',
            mode: 'lines',
            name: 'Plot 1',
        };

        var plot2 = {
            x: data.x,
            y: data.y2,
            type: 'scatter',
            mode: 'lines',
            name: 'Plot 2',
        };

        var plot3 = {
            x: data.x,
            y: data.y3,
            type: 'scatter',
            mode: 'lines',
            name: 'Plot 3',
        };

        var plot4 = {
            x: data.x,
            y: data.y4,
            type: 'scatter',
            mode: 'lines',
            name: 'Plot 4',
        };

        return [plot1, plot2, plot3, plot4];
    }
});
