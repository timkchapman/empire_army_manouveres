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
        document.getElementById('summary-force-imperial').textContent = 'Imperial';
        document.getElementById('summary-victory-contribution-imperial').textContent = data.imperial_victory_contribution;
        document.getElementById('summary-casualties-inflicted-imperial').textContent = data.imperial_casualties_inflicted;
        document.getElementById('summary-victory-points-imperial').textContent = data.outcome === 'Imperial Victory' ? data.victory_points : '0';
        document.getElementById('summary-offensive-victory-points-imperial').textContent = data.outcome === 'Imperial Victory' ? data.offensive_victory_points : '0';
        document.getElementById('summary-defensive-victory-points-imperial').textContent = data.outcome === 'Imperial Victory' ? data.defensive_victory_points : '0';

        document.getElementById('summary-force-barbarian').textContent = 'Barbarian';
        document.getElementById('summary-victory-contribution-barbarian').textContent = data.barbarian_victory_contribution;
        document.getElementById('summary-casualties-inflicted-barbarian').textContent = data.barbarian_casualties_inflicted;
        document.getElementById('summary-victory-points-barbarian').textContent = data.outcome === 'Barbarian Victory' ? data.victory_points : '0';
        document.getElementById('summary-offensive-victory-points-barbarian').textContent = data.outcome === 'Barbarian Victory' ? data.offensive_victory_points : '0';
        document.getElementById('summary-defensive-victory-points-barbarian').textContent = data.outcome === 'Barbarian Victory' ? data.defensive_victory_points : '0';
    }
});