document.addEventListener('DOMContentLoaded', function () {
    // Prevent enter key from submitting the form
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
        }
    });

    let imperialCount = 1;
    let barbarianCount = 1;

    document.getElementById('imperial-force-0').addEventListener('change', function () {
        updateFormFields('imperial', 0);
    });

    document.getElementById('barbarian-force-0').addEventListener('change', function () {
        updateFormFields('barbarian', 0);
    });

    document.getElementById('barbarian-force-selector').addEventListener('change', function () {
        updateBarbarianForces();
    });

    function updateFormFields(role, index) {
        var selectedForceId = document.getElementById(role + '-force-' + index).value;
        var csrfToken = document.querySelector('input[name="csrf_token"]').value;

        if (selectedForceId === '') {
            document.getElementById(role + '-strength-' + index).value = '';
            document.getElementById(role + '-order-' + index).innerHTML = '<option value="">Select Order</option>';
            document.getElementById(role + '-ritual-' + index).innerHTML = '<option value="">Select Ritual</option>';
            return;
        }

        fetchForceInfo(selectedForceId, role, index, csrfToken)
            .then(forceQuality => {
                fetchOrdersByForce(selectedForceId, role, index, csrfToken, forceQuality)
                    .catch(error => console.error('Error:', error));
            })
            .catch(error => console.error('Error:', error));

        fetchRitualsByForce(selectedForceId, role, index, csrfToken)
            .catch(error => console.error('Error:', error));

        addStrengthInputListener(role, index);
    }

    function fetchForceInfo(selectedForceId, role, index, csrfToken) {
        return fetch('/get_force_info', {
            method: 'POST',
            body: new URLSearchParams({
                'force_id': selectedForceId,
                'csrf_token': csrfToken
            }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
            .then(response => response.json())
            .then(data => {
                var maxStrength = data.large ? 7500 : 5000;
                var strengthField = document.getElementById(role + '-strength-' + index);
                strengthField.setAttribute('data-max-strength', maxStrength);
                strengthField.value = maxStrength;
                strengthField.removeAttribute('readonly');
                var forceQuality = data.quality;
                return forceQuality;
            })
            .catch(error => console.error('Error:', error));
    }

    function fetchOrdersByForce(selectedForceId, role, index, csrfToken, forceQuality) {
        return fetch('/get_orders_by_force', {
            method: 'POST',
            body: new URLSearchParams({
                'force_id': selectedForceId,
                'force_quality': forceQuality,
                'csrf_token': csrfToken
            }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
            .then(response => response.json())
            .then(data => {
                var orderSelect = document.getElementById(role + '-order-' + index);
                orderSelect.innerHTML = '<option value="">Select Order</option>';
                data.orders.forEach(order => {
                    var option = document.createElement('option');
                    option.value = order[0];
                    option.textContent = order[1];
                    orderSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    function fetchRitualsByForce(selectedForceId, role, index, csrfToken) {
        return fetch('/get_rituals_by_force', {
            method: 'POST',
            body: new URLSearchParams({
                'force_id': selectedForceId,
                'csrf_token': csrfToken
            }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
            .then(response => response.json())
            .then(data => {
                var ritualSelect = document.getElementById(role + '-ritual-' + index);
                ritualSelect.innerHTML = '<option value="">Select Ritual</option>';
                data.rituals.forEach(ritual => {
                    var option = document.createElement('option');
                    option.value = ritual[0];
                    option.textContent = ritual[1];
                    ritualSelect.appendChild(option);
                });
                ritualSelect.addEventListener('change', function () {
                    updateStrengthWithRitual(role, index);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    document.getElementById('add-imperial').addEventListener('click', function (e) {
        e.preventDefault();
        addForm('imperial', imperialCount);
        imperialCount++;
    });

    document.getElementById('add-barbarian').addEventListener('click', function (e) {
        e.preventDefault();
        addForm('barbarian', barbarianCount);
        barbarianCount++;
        updateBarbarianForces();
    });

    function addForm(role, index) {
        var form = document.getElementById(role + '-form');
        var newRow = document.createElement('tr');
        newRow.id = role + '-row-' + index;

        newRow.innerHTML = `
            <td>
                <select id="${role}-force-${index}" class="form-control" name="${role}_force[${index}][force]">
                    <option value="">Select Force</option>
                </select>
            </td>
            <td><input type="text" id="${role}-strength-${index}" class="form-control" name="${role}_force[${index}][strength]" readonly></td>
            <td>
                <select id="${role}-ritual-${index}" class="form-control" name="${role}_force[${index}][ritual]">
                    <option value="">Select Ritual</option>
                </select>
            </td>
            <td>
                <select id="${role}-order-${index}" class="form-control" name="${role}_force[${index}][order]">
                    <option value="">Select Order</option>
                </select>
            </td>
            <td><button type="button" class="btn btn-danger delete-${role}-row" data-row-id="${role}-row-${index}">Delete</button></td>
        `;

        form.querySelector('tbody').appendChild(newRow);

        document.querySelector(`.delete-${role}-row[data-row-id="${role}-row-${index}"]`).addEventListener('click', function () {
            document.getElementById(`${role}-row-${index}`).remove();
        });

        if (role === 'barbarian') {
            updateBarbarianForces();
        } else {
            fetchForceOptions(role, index);
        }

        document.getElementById(`${role}-force-${index}`).addEventListener('change', function () {
            updateFormFields(role, index);
        });
    }

    function updateBarbarianForces() {
        var selectedBarbarian = document.getElementById('barbarian-force-selector').value;
        var csrfToken = document.querySelector('input[name="csrf_token"]').value;

        if (selectedBarbarian === '') {
            for (let i = 0; i < barbarianCount; i++) {
                document.getElementById('barbarian-force-' + i).innerHTML = '<option value="">Select Force</option>';
            }
            return;
        }

        fetch('/get_force_options', {
            method: 'POST',
            body: new URLSearchParams({
                'role': 'barbarian',
                'barbarian': 'true',
                'selected_barbarian': selectedBarbarian,
                'csrf_token': csrfToken
            }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
            .then(response => response.json())
            .then(data => {
                for (let i = 0; i < barbarianCount; i++) {
                    var forceDropdown = document.getElementById('barbarian-force-' + i);
                    forceDropdown.innerHTML = '<option value="">Select Force</option>';
                    data.forces.forEach(force => {
                        var option = document.createElement('option');
                        option.value = force[0];
                        option.textContent = force[1];
                        forceDropdown.appendChild(option);
                    });
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function fetchForceOptions(role, index) {
        var forceDropdown = document.getElementById(`${role}-force-${index}`);
        var csrfToken = document.querySelector('input[name="csrf_token"]').value;

        fetch('/get_force_options', {
            method: 'POST',
            body: new URLSearchParams({
                'role': role,
                'csrf_token': csrfToken
            }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (Array.isArray(data.forces)) {
                    forceDropdown.innerHTML = '<option value="">Select Force</option>';
                    data.forces.forEach(force => {
                        var option = document.createElement('option');
                        option.value = force[0];
                        option.textContent = force[1];
                        forceDropdown.appendChild(option);
                    });
                } else {
                    console.error('Invalid forces data:', data);
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to add input event listener to the strength field for validation
    function addStrengthInputListener(role, index) {
        var strengthField = document.getElementById(role + '-strength-' + index);
        strengthField.addEventListener('input', function () {
            validateStrength(role, index);
        });
    }

    /// Function to validate the strength input
    function validateStrength(role, index) {
        var maxStrength = parseInt(document.getElementById(role + '-strength-' + index).getAttribute('data-max-strength'));
        var strengthField = document.getElementById(role + '-strength-' + index);
        var minStrength = maxStrength === 7500 ? 1500 : 1000;

        strengthField.addEventListener('blur', function () {
            var strengthInput = strengthField.value.trim();

            if (strengthInput === '' || isNaN(strengthInput) || parseInt(strengthInput) < minStrength || parseInt(strengthInput) > maxStrength) {
                strengthField.value = maxStrength;
            }
        });
    }

    function updateStrengthWithRitual(role, index) {
        var selectedRitual = document.getElementById(role + '-ritual-' + index).value;
        var strengthField = document.getElementById(role + '-strength-' + index);
        var baseStrength = parseInt(strengthField.getAttribute('data-max-strength'));

        if (selectedRitual === 'ritual1') {
            strengthField.value = baseStrength + 500; // Example adjustment
        } else if (selectedRitual === 'ritual2') {
            strengthField.value = baseStrength + 1000; // Example adjustment
        } else {
            strengthField.value = baseStrength;
        }
    }
});