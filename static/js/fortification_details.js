function removeRow(rowId) {
    document.getElementById(rowId).remove();
}

document.addEventListener('DOMContentLoaded', function () {
    // Prevent enter key from submitting the form
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
        }
    });

    let imperialFortificationCount = 1;
    let barbarianFortificationCount = 1;

    document.getElementById('add-imperial-fortification').addEventListener('click', function (e) {
        e.preventDefault();
        addFortificationForm('imperial', imperialFortificationCount);
        imperialFortificationCount++;
    });

    document.getElementById('add-barbarian-fortification').addEventListener('click', function (e) {
        e.preventDefault();
        addFortificationForm('barbarian', barbarianFortificationCount);
        barbarianFortificationCount++;
    });

    function addFortificationForm(role, index) {
        var formRow = document.createElement('tr');
        formRow.id = role + '-fort-row-' + index;
        formRow.className = 'table-dark';

        formRow.innerHTML = `
            <td>
                <select id="${role}-fortification-${index}" class="form-control" name="${role}_fortification[${index}][fortification]">
                    <option value="">Select Fortification</option>
                </select>
            </td>
            <td>
                <select id="${role}-fortification-ritual-${index}" class="form-control" name="${role}_fortification[${index}][ritual]">
                    <option value="">Select Ritual</option>
                </select>
            </td>
            <td><input type="checkbox" id="${role}-fortification-besieged-${index}" class="form-check-input" name="${role}_fortification[${index}][is_besieged]"></td>
            <td><input type="text" id="${role}-fortification-strength-${index}" class="form-control" name="${role}_fortification[${index}][strength]"></td>
            <td></td>
        `;

        var form = document.getElementById(role + '-form');
        form.querySelector('tbody').appendChild(formRow);

        // Fetch fortification options and populate the dropdown list
        fetchFortificationOptions(role, index);
        // Fetch fortification ritual options and populate the dropdown list
        fetchFortificationRitualOptions(role, index);

        document.getElementById(`${role}-fortification-${index}`).addEventListener('change', function () {
            updateFortificationStrength(role, index);
        });

        // Add blur event listener to the fortification strength field for validation
        addFortificationStrengthBlurListener(role, index);

        // Create and attach the delete button
        var deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'btn btn-danger';
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', function () {
            removeRow(`${role}-fort-row-${index}`);
        });
        formRow.lastElementChild.appendChild(deleteButton);
    }

    function addFortificationStrengthBlurListener(role, index) {
        var strengthField = document.getElementById(role + '-fortification-strength-' + index);
        strengthField.addEventListener('blur', function () {
            var maxStrength = strengthField.getAttribute('data-max-strength');
            var strengthInput = strengthField.value.trim();
            if (strengthInput === '' || isNaN(strengthInput) || parseInt(strengthInput) < 1000 || parseInt(strengthInput) > maxStrength) {
                strengthField.value = maxStrength;
            }
        });
    }

    function fetchFortificationOptions(role, index) {
        var fortificationDropdown = document.getElementById(`${role}-fortification-${index}`);
        var csrfToken = document.querySelector('input[name="csrf_token"]').value;

        // Fetch fortification options
        fetch('/get_fortification_options', {
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
                // Populate the dropdown list with fortification options
                fortificationDropdown.innerHTML = '<option value="">Select Fortification</option>';
                data.fortifications.forEach(fortification => {
                    var option = document.createElement('option');
                    option.value = fortification[0];
                    option.textContent = fortification[1];
                    fortificationDropdown.appendChild(option);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    function fetchFortificationRitualOptions(role, index) {
        var fortificationRitualDropdown = document.getElementById(`${role}-fortification-ritual-${index}`);
        var csrfToken = document.querySelector('input[name="csrf_token"]').value;

        // Fetch fortification ritual options
        fetch('/get_rituals_by_fortification', {
            method: 'POST',
            body: new URLSearchParams({
                'csrf_token': csrfToken
            }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
            .then(response => response.json())
            .then(data => {
                // Populate the dropdown list with fortification ritual options
                fortificationRitualDropdown.innerHTML = '<option value="">Select Ritual</option>';
                data.rituals.forEach(ritual => {
                    var option = document.createElement('option');
                    option.value = ritual[0];
                    option.textContent = ritual[1];
                    fortificationRitualDropdown.appendChild(option);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    function updateFortificationStrength(role, index) {
        var selectedFortificationId = document.getElementById(role + '-fortification-' + index).value;
        var csrfToken = document.querySelector('input[name="csrf_token"]').value;

        if (selectedFortificationId === '') {
            document.getElementById(role + '-fortification-strength-' + index).value = '';
            return;
        }

        // Fetch fortification info
        fetch('/get_fortification_info', {
            method: 'POST',
            body: new URLSearchParams({
                'fortification_id': selectedFortificationId,
                'csrf_token': csrfToken
            }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
            .then(response => response.json())
            .then(data => {
                var maxStrength = data.strength;
                document.getElementById(role + '-fortification-strength-' + index).value = maxStrength;
                document.getElementById(role + '-fortification-strength-' + index).setAttribute('data-max-strength', maxStrength);
            })
            .catch(error => console.error('Error:', error));
    }
});

