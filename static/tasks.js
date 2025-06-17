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

    
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', () => {
            
            taskList.style.display = 'none';
            addForm.style.display = 'none';
            header.textContent = 'Task Editor';

            
            const title = button.dataset.title;
            const priority = button.dataset.priority.toLowerCase() || '';
            const done = button.dataset.done === "1";

            
            editTitle.value = title;
            editPriority.value = priority;
            editDone.checked = done;

            
            cancelBtn.dataset.originalTitle = title;
            cancelBtn.dataset.originalPriority = priority;
            cancelBtn.dataset.originalDone = button.dataset.done;

           
            editForm.action = `/update/${button.dataset.taskId}`;

           
            editWrapper.style.display = 'block';
        });
    });

   
    cancelBtn.addEventListener('click', () => {
        const originalTitle = cancelBtn.dataset.originalTitle;
        const originalPriority = cancelBtn.dataset.originalPriority;
        const originalDone = cancelBtn.dataset.originalDone;

        const currentTitle = editTitle.value;
        const currentPriority = editPriority.value.toLowerCase();
        const currentDone = editDone.checked ? "1" : "0";

        const hasChanges =
            originalTitle !== currentTitle ||
            originalPriority !== currentPriority ||
            originalDone !== currentDone;

        if (hasChanges) {
            const confirmCancel = confirm("Discard your changes?");
            if (!confirmCancel) return;
        }

       
        editWrapper.style.display = 'none';
        
        taskList.style.display = 'block';
        addForm.style.display = 'block';
        header.textContent = 'My Tasks';
    });
});