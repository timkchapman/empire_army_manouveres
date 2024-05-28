document.addEventListener('DOMContentLoaded', function () {
    // Prevent enter key from submitting the form
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
        }
    });

    document.getElementById('calculate-outcome').addEventListener('click', function (e) {
        e.preventDefault();

        const imperialForces = collectForces('imperial');
        const barbarianForces = collectForces('barbarian');
        const imperialFortifications = collectFortifications('imperial');
        const barbarianFortifications = collectFortifications('barbarian');

        const data = {
            imperial_forces: imperialForces,
            imperial_fortifications: imperialFortifications,
            barbarian_forces: barbarianForces,
            barbarian_fortifications: barbarianFortifications
        };

        // Send data to the server for calculation
        fetch('/calculate_outcome', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken() // Include CSRF token in the headers
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                // Display outcome and details in the summary table
                showSummary(data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });

    // Function to collect forces data
    function collectForces(role) {
        const forces = [];
        const tableBody = document.getElementById(`${role}-forces`);
        if (tableBody) {
            const rows = tableBody.querySelectorAll('tr');
            rows.forEach(function (row) {
                const forceId = row.id.split('-').pop();
                const forceElement = document.getElementById(`${role}-force-${forceId}`);
                if (forceElement) {
                    let orderValue = row.querySelector(`#${role}-order-${forceId}`).value;
                    let ritualValue = row.querySelector(`#${role}-ritual-${forceId}`).value;
                    if (orderValue === '') {
                        orderValue = 6;
                    }
                    if (ritualValue === '') {
                        ritualValue = 0;
                    }
                    const force = {
                        force: forceElement.value,
                        strength: row.querySelector(`#${role}-strength-${forceId}`).value,
                        order: orderValue,
                        ritual: ritualValue
                    };
                    forces.push(force);
                }
            });
        }
        return forces;
    }

    // Function to collect fortifications data
    function collectFortifications(role) {
        const fortifications = [];
        const tableBody = document.getElementById(`${role}-forces`);
        if (tableBody) {
            const rows = tableBody.querySelectorAll('tr');
            rows.forEach(function (row) {
                const forceId = row.id.split('-').pop();
                const fortificationElement = document.getElementById(`${role}-fortification-${forceId}`);
                if (fortificationElement) {
                    const fortification = {
                        fortification: fortificationElement.value,
                        strength: document.getElementById(`${role}-fortification-strength-${forceId}`).value,
                        besieged: document.getElementById(`${role}-fortification-besieged-${forceId}`).checked,
                        ritual: document.getElementById(`${role}-fortification-ritual-${forceId}`).value
                    };
                    fortifications.push(fortification);
                }
            });
        }
        return fortifications;
    }

    // Function to get CSRF token value
    function getCSRFToken() {
        return document.querySelector('input[name="csrf_token"]').value;
    }

    // Function to display summary
    function showSummary(data) {
        document.getElementById('summary-total-victory-points').textContent = data.total_victory_points;
        document.getElementById('summary-offensive-victory-points').textContent = data.offensive_victory_points;
        document.getElementById('summary-defensive-victory-points').textContent = data.defensive_victory_points;
        document.getElementById('summary-outcome').textContent = data.outcome;

        const forcesTable = document.getElementById('summary-forces-details');
        forcesTable.innerHTML = ''; // Clear any previous content
        for (const key in data.forces_data) {
            const force = data.forces_data[key];
            const forceRow = document.createElement('tr');
            forceRow.className = 'table-dark';
            forceRow.innerHTML = `
                <td>${force.force_name}</td>
                <td>${force.casualties_taken}</td>
                <td>${force.remaining_strength}</td>
            `;
            forcesTable.appendChild(forceRow);
        }
    }

});
