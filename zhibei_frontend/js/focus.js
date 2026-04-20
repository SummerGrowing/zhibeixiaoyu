// Focus checkbox management

let lessonDetailCache = {};  // Cache lesson details from API

async function getLessonDetailFromAPI(grade, unit, lesson) {
    const key = `${grade}|${unit}|${lesson}`;
    if (!lessonDetailCache[key]) {
        try {
            lessonDetailCache[key] = await ZhibeiAPI.getLessonDetail(grade, unit, lesson);
        } catch (e) {
            lessonDetailCache[key] = {};
        }
    }
    return lessonDetailCache[key];
}

async function getUnitFocusElements(grade, unit) {
    // Fetch unit keywords from API to get readingElement/writingElement
    try {
        const uk = await ZhibeiAPI.getUnitKeywords(grade, unit);
        if (!uk) return [];
        const elements = [];
        if (uk.readingElement) {
            elements.push({ value: uk.readingElement, checked: true, type: 'reading' });
        }
        if (uk.writingElement) {
            elements.push({ value: uk.writingElement, checked: true, type: 'writing' });
        }
        return elements;
    } catch (e) {
        return [];
    }
}

async function updateUnitFocusSection(grade, unit) {
    const unitFocusSection = document.getElementById('unitFocusSection');
    const unitFocusGroup = document.getElementById('unitFocusGroup');
    const elements = await getUnitFocusElements(grade, unit);

    if (elements.length === 0) {
        unitFocusSection.style.display = 'none';
        return;
    }

    unitFocusSection.style.display = 'block';
    unitFocusGroup.innerHTML = '';

    elements.forEach((el, idx) => {
        const label = document.createElement('label');
        label.className = 'checkbox-item';
        label.innerHTML = `<input type="checkbox" id="unitFocus${idx}" value="${el.value}" ${el.checked ? 'checked' : ''}><span>${el.value}</span>`;
        unitFocusGroup.appendChild(label);
    });
}

async function updateFocusCheckboxes(textType, defaultFocus, lessonName) {
    const focusCheckboxGrid = document.getElementById('focusCheckboxGrid');
    const BASIC_OPTION_VALUES = ['品读语言', '朗读感悟', '识字写字', '写作顺序', '修辞手法', '小练笔设计'];

    // Reset basic options: uncheck all, remove recommended highlight
    document.querySelectorAll('#basicOptionsGrid .checkbox-item').forEach(item => {
        item.querySelector('input[type="checkbox"]').checked = false;
        item.classList.remove('recommended');
    });

    // Check & highlight defaultFocus items that are basic options
    defaultFocus.forEach(val => {
        if (BASIC_OPTION_VALUES.includes(val)) {
            const cb = document.querySelector('#basicOptionsGrid input[value="' + val + '"]');
            if (cb) {
                cb.checked = true;
                cb.closest('.checkbox-item').classList.add('recommended');
            }
        }
    });

    // Build "一课一得" section
    focusCheckboxGrid.innerHTML = '';
    const addedValues = new Set();
    let idCounter = 0;

    // Get lesson detail from API
    const grade = document.getElementById('gradeSelect').value;
    const unit = document.getElementById('unitSelect').value;
    const detail = await getLessonDetailFromAPI(grade, unit, lessonName);

    const lessonFocusMap = detail.lessonFocusMap;

    if (lessonFocusMap) {
        // Priority A: Fine-grained per-lesson data (四年级上册)
        if (lessonFocusMap.recommended && lessonFocusMap.recommended.length > 0) {
            lessonFocusMap.recommended.forEach(f => {
                if (!addedValues.has(f) && !BASIC_OPTION_VALUES.includes(f)) {
                    addedValues.add(f);
                    const label = document.createElement('label');
                    label.className = 'checkbox-item recommended';
                    label.innerHTML = `<input type="checkbox" value="${f}" id="lessonFocus_${idCounter++}" checked><span>${f}</span>`;
                    focusCheckboxGrid.appendChild(label);
                }
            });
        }
        if (lessonFocusMap.optional && lessonFocusMap.optional.length > 0) {
            lessonFocusMap.optional.forEach(f => {
                if (!addedValues.has(f) && !BASIC_OPTION_VALUES.includes(f)) {
                    addedValues.add(f);
                    const label = document.createElement('label');
                    label.className = 'checkbox-item optional';
                    label.innerHTML = `<input type="checkbox" value="${f}" id="lessonFocus_${idCounter++}"><span>${f}</span>`;
                    focusCheckboxGrid.appendChild(label);
                }
            });
        }
    }

    // Priority B (fallback for other grades) + always append refinement if available
    if (detail.unitFocusRefinementMap) {
        const unitCheckedValues = [];
        document.querySelectorAll('#unitFocusGroup input[type="checkbox"]:checked').forEach(cb => {
            unitCheckedValues.push(cb.value);
        });
        unitCheckedValues.forEach(unitVal => {
            const refinement = detail.unitFocusRefinementMap[unitVal];
            if (!refinement) return;

            (refinement.refinedOptions || []).forEach(opt => {
                if (!addedValues.has(opt) && !BASIC_OPTION_VALUES.includes(opt)) {
                    addedValues.add(opt);
                    const label = document.createElement('label');
                    label.className = 'checkbox-item recommended';
                    label.innerHTML = `<input type="checkbox" value="${opt}" id="lessonFocus_${idCounter++}" checked><span>${opt}</span>`;
                    focusCheckboxGrid.appendChild(label);
                }
            });

            (refinement.relatedLessonFocus || []).forEach(opt => {
                if (!addedValues.has(opt) && !BASIC_OPTION_VALUES.includes(opt)) {
                    addedValues.add(opt);
                    const label = document.createElement('label');
                    label.className = 'checkbox-item recommended';
                    label.innerHTML = `<input type="checkbox" value="${opt}" id="lessonFocus_${idCounter++}" checked><span>${opt}</span>`;
                    focusCheckboxGrid.appendChild(label);
                }
            });
        });
    }

    // Type-specific extras (supplementary, not checked by default)
    try {
        const extras = await ZhibeiAPI.getFocusOptions(textType);
        const extraFiltered = extras.filter(e => !addedValues.has(e.value) && !BASIC_OPTION_VALUES.includes(e.value));
        extraFiltered.forEach(e => {
            addedValues.add(e.value);
            const label = document.createElement('label');
            label.className = 'checkbox-item extra-focus';
            label.innerHTML = `<input type="checkbox" value="${e.value}" id="lessonFocus_${idCounter++}"><span>${e.label}</span>`;
            focusCheckboxGrid.appendChild(label);
        });
    } catch (err) {
        console.error('Failed to load focus options:', err);
    }

    // Update keywords row for 四年级上册
    updateKeyWordsRow(grade, lessonName);

    updateCardSummaries();
}

function updateKeyWordsRow(grade, lessonName) {
    const keyWordsRow = document.getElementById('keyWordsRow');
    const keyWordsLabel = document.getElementById('keyWordsLabel');

    // Only show for 四年级上册
    if (grade !== '四年级上册') {
        keyWordsRow.style.display = 'none';
        return;
    }

    // Use correct cache key format: grade|unit|lesson
    const unit = document.getElementById('unitSelect').value;
    const cacheKey = `${grade}|${unit}|${lessonName}`;
    const lessonDetail = lessonDetailCache[cacheKey] || {};

    if (lessonDetail.vocabulary) {
        const keyWords = lessonDetail.vocabulary.split(/[,、，]/).filter(w => w.trim());
        if (keyWords.length > 0) {
            keyWordsRow.style.display = 'flex';
            keyWordsLabel.textContent = '重点字词：' + keyWords.join('、') + '（选讲）';
            return;
        }
    }
    keyWordsRow.style.display = 'none';
}

function getSelectedFocusTexts() {
    const texts = [];

    // Basic options
    document.querySelectorAll('#basicOptionsGrid input[type="checkbox"]:checked').forEach(cb => {
        texts.push(cb.value);
    });

    // Unit focus
    document.querySelectorAll('#unitFocusGroup input[type="checkbox"]:checked').forEach(cb => {
        texts.push(cb.value);
    });

    // Lesson focus (一课一得)
    document.getElementById('focusCheckboxGrid').querySelectorAll('input[type="checkbox"]:checked').forEach(cb => {
        texts.push(cb.value);
    });

    // Key words
    const keyWordsCheckbox = document.getElementById('keyWordsCheckbox');
    if (keyWordsCheckbox && keyWordsCheckbox.checked) {
        const keyWordsLabel = document.getElementById('keyWordsLabel');
        const keyWords = keyWordsLabel.textContent.replace('重点字词：', '').replace('（选讲）', '');
        texts.push('重点字词：' + keyWords);
    }

    return texts;
}

function updateCardSummaries() {
    const c1Summary = `${document.getElementById('gradeSelect').value} · ${document.getElementById('unitSelect').value} · ${document.getElementById('titleSelect').value}`;
    document.getElementById('card1').querySelector('.card-summary').textContent = c1Summary;

    const checkedFocus = getSelectedFocusTexts();
    const otherFocusValue = document.getElementById('otherFocus').value.trim();
    const allFocus = [...checkedFocus];
    if (otherFocusValue) allFocus.push(...otherFocusValue.split(/[,，]/).map(k => k.trim()).filter(k => k));
    const c2Summary = allFocus.join(' · ') || '未选择';
    document.getElementById('card2').querySelector('.card-summary').textContent = c2Summary;

    const idea = document.getElementById('ideaText').value.trim();
    const c3Summary = idea ? (idea.length > 30 ? idea.substring(0, 30) + '...' : idea) : '无';
    document.getElementById('card3').querySelector('.card-summary').textContent = c3Summary;

    // Update compact views
    const compactFocusView = document.getElementById('compactFocusView');
    if (compactFocusView) {
        const unitChecked = [];
        document.querySelectorAll('#unitFocusGroup input[type="checkbox"]:checked').forEach(cb => unitChecked.push(cb.value));
        const basicChecked = [];
        document.querySelectorAll('#basicOptionsGrid input[type="checkbox"]:checked').forEach(cb => basicChecked.push(cb.value));
        const courseChecked = [];
        document.getElementById('focusCheckboxGrid').querySelectorAll('input[type="checkbox"]:checked').forEach(cb => courseChecked.push(cb.value));
        const otherKeywords = otherFocusValue ? otherFocusValue.split(/[,，]/).map(k => k.trim()).filter(k => k) : [];

        let html = '';
        if (unitChecked.length) html += `<div class="compact-group"><span class="compact-group-label">单元重点</span><div class="compact-group-tags">${unitChecked.map(f => `<span class="compact-tag">${f}</span>`).join('')}</div></div>`;
        if (basicChecked.length) html += `<div class="compact-group"><span class="compact-group-label">基础能力</span><div class="compact-group-tags">${basicChecked.map(f => `<span class="compact-tag">${f}</span>`).join('')}</div></div>`;
        if (courseChecked.length) html += `<div class="compact-group"><span class="compact-group-label">一课一得</span><div class="compact-group-tags">${courseChecked.map(f => `<span class="compact-tag">${f}</span>`).join('')}</div></div>`;
        if (otherKeywords.length) html += `<div class="compact-group"><span class="compact-group-label">补充</span><div class="compact-group-tags">${otherKeywords.map(f => `<span class="compact-tag compact-tag-other">${f}</span>`).join('')}</div></div>`;
        compactFocusView.innerHTML = html;
    }

    const compactIdeaView = document.getElementById('compactIdeaView');
    if (compactIdeaView) {
        compactIdeaView.textContent = idea || '无';
    }
}
