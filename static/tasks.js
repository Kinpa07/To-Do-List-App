document.addEventListener('DOMContentLoaded', () => {
    const taskList = document.getElementById('task-list');
    const editWrapper = document.getElementById('edit-wrapper');
    const editForm = document.getElementById('edit-form');
    const editTitle = document.getElementById('edit-title');
    const editPriority = document.getElementById('edit-priority');
    const editDone = document.getElementById('edit-done');
    const cancelBtn = document.getElementById('cancel-edit');
    const addForm = document.getElementById('add-form');
    const header = document.getElementById('main-header');

    // Due date field
    const editDueDate = document.getElementById('edit-due-date');

    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', () => {
            taskList.style.display = 'none';
            addForm.style.display = 'none';
            header.textContent = 'Task Editor';

            const title = button.dataset.title;
            const priority = button.dataset.priority.toLowerCase() || '';
            const done = button.dataset.done === "1";
            const dueDate = button.dataset.dueDate || '';

            editTitle.value = title;
            editPriority.value = priority;
            editDone.checked = done;
            editDueDate.value = dueDate;

            cancelBtn.dataset.originalTitle = title;
            cancelBtn.dataset.originalPriority = priority;
            cancelBtn.dataset.originalDone = button.dataset.done;
            cancelBtn.dataset.originalDueDate = dueDate;

            editForm.action = `/update/${button.dataset.taskId}`;
            editWrapper.style.display = 'block';
        });
    });

    cancelBtn.addEventListener('click', () => {
        const originalTitle = cancelBtn.dataset.originalTitle;
        const originalPriority = cancelBtn.dataset.originalPriority;
        const originalDone = cancelBtn.dataset.originalDone;
        const originalDueDate = cancelBtn.dataset.originalDueDate;

        const currentTitle = editTitle.value;
        const currentPriority = editPriority.value.toLowerCase();
        const currentDone = editDone.checked ? "1" : "0";
        const currentDueDate = editDueDate.value;

        const hasChanges =
            originalTitle !== currentTitle ||
            originalPriority !== currentPriority ||
            originalDone !== currentDone ||
            originalDueDate !== currentDueDate;

        if (hasChanges) {
            const confirmCancel = confirm("Discard your changes?");
            if (!confirmCancel) return;
        }

        // Remove visible error message (if present)
        const errorParagraph = document.querySelector('p[style*="color: red"]');
        if (errorParagraph) {
            errorParagraph.remove();
        }

        editWrapper.style.display = 'none';
        taskList.style.display = 'block';
        addForm.style.display = 'block';
        header.textContent = 'My Tasks';
    });

    // Open edit form automatically if reopen_id is present
    const reopenId = document.body.dataset.reopenId;
    if (reopenId) {
        taskList.style.display = 'none';
        addForm.style.display = 'none';
        header.textContent = 'Task Editor';
        editWrapper.style.display = 'block';

        editTitle.value = document.body.dataset.editTitle || '';
        editPriority.value = (document.body.dataset.editPriority || '').toLowerCase();
        editDueDate.value = document.body.dataset.editDueDate || '';
        editDone.checked = document.body.dataset.editDone === "1";

        editForm.action = `/update/${reopenId}`;

        // Scroll to top (optional)
        window.scrollTo(0, 0);
    }
});