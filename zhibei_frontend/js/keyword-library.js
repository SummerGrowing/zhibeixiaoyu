// Keyword library modal logic

let keywordLibraryData = null;

async function initKeywordLibrary() {
    if (!keywordLibraryData) {
        try {
            keywordLibraryData = await ZhibeiAPI.getKeywordLibrary();
        } catch (e) {
            keywordLibraryData = {};
        }
    }

    const otherFocus = document.getElementById('otherFocus');
    const currentKeywords = otherFocus.value.split(/[,，]/).map(k => k.trim()).filter(k => k);
    const keywordLibraryBody = document.getElementById('keywordLibraryBody');
    let html = '';

    for (const [category, keywords] of Object.entries(keywordLibraryData)) {
        html += `<div class="keyword-category"><div class="keyword-category-title">${category}</div><div class="keyword-tags">`;
        for (const kw of keywords) {
            const isSelected = currentKeywords.includes(kw);
            html += `<span class="keyword-tag${isSelected ? ' selected' : ''}" data-keyword="${kw}">${kw}</span>`;
        }
        html += '</div></div>';
    }

    keywordLibraryBody.innerHTML = html;

    // Click handlers for keyword tags
    keywordLibraryBody.querySelectorAll('.keyword-tag').forEach(tag => {
        tag.addEventListener('click', () => {
            const keyword = tag.dataset.keyword;
            let currentValue = otherFocus.value.trim();
            const existingKeywords = currentValue.split(/[,，]/).map(k => k.trim()).filter(k => k);

            if (tag.classList.contains('selected')) {
                tag.classList.remove('selected');
                const filtered = existingKeywords.filter(k => k !== keyword);
                otherFocus.value = filtered.join('、');
            } else {
                tag.classList.add('selected');
                if (!existingKeywords.includes(keyword)) {
                    existingKeywords.push(keyword);
                    otherFocus.value = existingKeywords.join('、');
                }
            }
            updateCardSummaries();
        });
    });
}

// Keyword library modal open/close
document.getElementById('keywordLibraryLink').addEventListener('click', () => {
    initKeywordLibrary();
    document.getElementById('keywordLibraryModal').classList.add('show');
});

document.getElementById('keywordLibraryClose').addEventListener('click', () => {
    document.getElementById('keywordLibraryModal').classList.remove('show');
});

document.getElementById('confirmKeywordBtn').addEventListener('click', () => {
    document.getElementById('keywordLibraryModal').classList.remove('show');
    updateCardSummaries();
});

document.getElementById('clearOtherFocusBtn').addEventListener('click', () => {
    document.getElementById('otherFocus').value = '';
    document.querySelectorAll('.keyword-tag.selected').forEach(tag => tag.classList.remove('selected'));
    updateCardSummaries();
});
