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

    function updateFormFields(role, index) {
        var selectedForceId = document.getElementById(role + '-force-' + index).value;
        var csrfToken = document.querySelector('input[name="csrf_token"]').value;

        if (selectedForceId === '') {
            document.getElementById(role + '-strength-' + index).value = '';
            document.getElementById(role + '-order-' + index).innerHTML = '<option value="">Select Order</option>';
            document.getElementById(role + '-ritual-' + index).innerHTML = '<option value="">Select Ritual</option>';
            return;
        }

        // Fetch force info
        fetch('/get_force_info', {
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
            })
            .catch(error => console.error('Error:', error));

        // Fetch orders by force
        fetch('/get_orders_by_force', {
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

        // Fetch rituals by force
        fetch('/get_rituals_by_force', {
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
            })
            .catch(error => console.error('Error:', error));

        // Add input event listener to the strength field for validation
        addStrengthInputListener(role, index);
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
    });

    function addForm(role, index) {
        var form = document.getElementById(role + '-form');
        var formRow = document.querySelector(`#${role}-row-0`).cloneNode(true);

        // Update the IDs and clear the values in the cloned form fields
        formRow.id = role + '-row-' + index;
        formRow.querySelectorAll('*').forEach((element) => {
            if (element.id) {
                element.id = element.id.replace('-0', '-' + index);
            }
            if (element.name) {
                element.name = element.name.replace('-0', '-' + index);
            }
            if (element.tagName === 'INPUT' || element.tagName === 'SELECT') {
                element.value = '';
            }
        });

        // Remove the 'readonly' attribute from the strength field
        formRow.querySelector(`#${role}-strength-${index}`).removeAttribute('readonly');

        // Attach event listener to the cloned force field
        formRow.querySelector(`#${role}-force-${index}`).addEventListener('change', function () {
            updateFormFields(role, index);
        });

        // Add delete button to the cloned row
        var deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'btn btn-danger';
        deleteButton.innerText = 'Delete';
        deleteButton.addEventListener('click', function () {
            formRow.remove();
        });

        // Append delete button as the last column of the cloned row
        var lastTd = formRow.querySelector('td:last-child');
        lastTd.appendChild(deleteButton);

        form.querySelector('tbody').appendChild(formRow);

        // Add input event listener to the strength field for validation
        addStrengthInputListener(role, index);
    }

    // Function to add input event listener to the strength field for validation
    function addStrengthInputListener(role, index) {
        var strengthField = document.getElementById(role + '-strength-' + index);
        strengthField.addEventListener('input', function () {
            validateStrength(role, index);
        });
    }

    // Function to validate the strength input
    function validateStrength(role, index) {
        var maxStrength = parseInt(document.getElementById(role + '-strength-' + index).getAttribute('data-max-strength'));
        var strengthField = document.getElementById(role + '-strength-' + index);

        strengthField.addEventListener('blur', function () {
            var strengthInput = strengthField.value.trim();

            if (strengthInput === '' || isNaN(strengthInput) || parseInt(strengthInput) <= 0 || parseInt(strengthInput) > maxStrength) {
                strengthField.value = maxStrength;
            }
        });
    }
});
