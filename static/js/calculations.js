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
        if (imperialForces.length === 0 || (barbarianForces.length + barbarianFortifications.length) === 0) {
            alert('Please select combatants for both sides.');
            return;
        }

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

    function hasDuplicates(array) {
        const ids = array.map(obj => obj.force); // Change 'force' to 'fortification' if checking fortifications
        return new Set(ids).size !== array.length;
    }

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
                    const strengthElement = row.querySelector(`#${role}-strength-${forceId}`);
                    const orderElement = row.querySelector(`#${role}-order-${forceId}`);
                    const ritualElement = row.querySelector(`#${role}-ritual-${forceId}`);
                    // Check if elements are found before accessing their value property
                    const strengthValue = strengthElement ? strengthElement.value : '';
                    const orderValue = orderElement ? orderElement.value : '';
                    const ritualValue = ritualElement ? ritualElement.value : '';
                    const force = {
                        force: forceElement.value,
                        strength: strengthValue,
                        order: orderValue,
                        ritual: ritualValue
                    };
                    if (force.force.trim() !== '') {
                        forces.push(force);
                    }
                } else {
                    console.log('Force element not found for row:', row);
                }
            });
        } else {
            console.log(`Table body not found for role '${role}'`);
        }
        console.log('Forces collected:', forces);
        if (hasDuplicates(forces)) {
            alert('Please make sure each combatant is unique.');
            return [];
        }
        return forces;
    }

    function collectFortifications(role) {
        const fortifications = [];
        const tableBody = document.getElementById(`${role}-forces`);
        if (tableBody) {
            const rows = tableBody.querySelectorAll('tr');
            rows.forEach(function (row) {
                const forceId = row.id.split('-').pop();
                const fortificationElement = document.getElementById(`${role}-fortification-${forceId}`);
                if (fortificationElement) {
                    const strengthElement = document.getElementById(`${role}-fortification-strength-${forceId}`);
                    const besiegedElement = document.getElementById(`${role}-fortification-besieged-${forceId}`);
                    const ritualElement = document.getElementById(`${role}-fortification-ritual-${forceId}`);
                    // Check if elements are found before accessing their value property
                    const strengthValue = strengthElement ? strengthElement.value : '';
                    const besiegedValue = besiegedElement ? besiegedElement.checked : false;
                    const ritualValue = ritualElement ? ritualElement.value : '';
                    const fortification = {
                        fortification: fortificationElement.value,
                        strength: strengthValue,
                        besieged: besiegedValue,
                        ritual: ritualValue
                    };
                    if (fortification.fortification.trim() !== '') {
                        fortifications.push(fortification);
                    }
                } else {
                    console.log('Fortification element not found for row:', row);
                }
            });
        } else {
            console.log(`Table body not found for role '${role}'`);
        }
        console.log('Fortifications collected:', fortifications);
        if (hasDuplicates(fortifications.map(f => f.fortification))) {
            alert('Please make sure each combatant is unique.');
            return [];
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
            const remainingStrengthDisplay = force.remaining_strength === 0 ? '0 - destroyed' : force.remaining_strength;

            const forceRow = document.createElement('tr');
            forceRow.className = 'table-dark';
            forceRow.innerHTML = `
                <td>${force.force_name}</td>
                <td>${force.casualties_taken}</td>
                <td>${remainingStrengthDisplay}</td>
            `;
            forcesTable.appendChild(forceRow);
        }

        for (const key in data.fortifications_data) {
            const fortification = data.fortifications_data[key];
            const remainingStrengthDisplay = fortification.remaining_strength === 0 ? '0 - destroyed' : fortification.remaining_strength;

            const fortificationRow = document.createElement('tr');
            fortificationRow.className = 'table-dark';
            fortificationRow.innerHTML = `
                <td>${fortification.fortification_name}</td>
                <td>${fortification.casualties_taken}</td>
                <td>${remainingStrengthDisplay}</td>
                `;
            forcesTable.appendChild(fortificationRow);
        }
    }

});
