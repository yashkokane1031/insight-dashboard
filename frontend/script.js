document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('realtime-chart').getContext('2d');

    // 1. Initialize the chart
    const myChart = new Chart(ctx, {
        type: 'doughnut', // Doughnut charts can be used as gauges
        data: {
            labels: ['Temp', ''],
            datasets: [{
                label: 'CPU Temperature',
                data: [0, 100], // Initial data
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(201, 203, 207, 0.5)'
                ],
                circumference: 180, // Make it a semi-circle
                rotation: 270,      // Start at the bottom
            }]
        },
        options: {
            responsive: false,
            cutout: '80%', // Make the doughnut thinner
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    });

    const fetchLatestData = () => {
        fetch('http://127.0.0.1:8000/data/latest')
            .then(response => response.json())
            .then(data => {
                // 2. Update the chart's data
                // We set the gauge value and the remaining part of the circle
                myChart.data.datasets[0].data[0] = data.value;
                myChart.data.datasets[0].data[1] = 100 - data.value; // Assuming max temp is 100

                // 3. Tell the chart to re-render with the new data
                myChart.update();
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    };

    fetchLatestData();
    setInterval(fetchLatestData, 3000);
});