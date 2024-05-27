
$(document).ready(function () {
    // Add click event listener to delete button
    $('.delete-barbarian-row').click(function () {
        // Get the ID of the row to be deleted
        var rowId = $(this).data('row-id');

        // Remove the row from the table
        $('#' + rowId).remove();
    });
});

