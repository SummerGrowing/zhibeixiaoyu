// Teaching page display/edit logic

let originalTeachingContent = '';

// Copy
document.getElementById('copyTeachingBtn').addEventListener('click', () => {
    copyText(document.getElementById('teachingContent').innerText);
});

// Edit
document.getElementById('editTeachingBtn').addEventListener('click', () => {
    const teachingContent = document.getElementById('teachingContent');
    const teachingFooter = document.querySelector('.teaching-panel .teaching-footer:not(#teachingEditFooter)');
    const teachingEditFooter = document.getElementById('teachingEditFooter');

    teachingContent.setAttribute('contenteditable', 'true');
    teachingContent.focus();
    teachingFooter.classList.add('hidden');
    teachingEditFooter.classList.remove('hidden');
    originalTeachingContent = teachingContent.innerHTML;
});

// Save
document.getElementById('saveTeachingBtn').addEventListener('click', () => {
    const teachingContent = document.getElementById('teachingContent');
    const teachingFooter = document.querySelector('.teaching-panel .teaching-footer:not(#teachingEditFooter)');
    const teachingEditFooter = document.getElementById('teachingEditFooter');

    teachingContent.setAttribute('contenteditable', 'false');
    teachingFooter.classList.remove('hidden');
    teachingEditFooter.classList.add('hidden');
});

// Cancel edit
document.getElementById('cancelTeachingEditBtn').addEventListener('click', () => {
    const teachingContent = document.getElementById('teachingContent');
    const teachingFooter = document.querySelector('.teaching-panel .teaching-footer:not(#teachingEditFooter)');
    const teachingEditFooter = document.getElementById('teachingEditFooter');

    teachingContent.innerHTML = originalTeachingContent;
    teachingContent.setAttribute('contenteditable', 'false');
    teachingFooter.classList.remove('hidden');
    teachingEditFooter.classList.add('hidden');
});

// Auto-scroll teaching content during streaming
function scrollToBottomOfTeaching() {
    const teachingContent = document.getElementById('teachingContent');
    teachingContent.scrollTop = teachingContent.scrollHeight;
}
