// Curriculum cascading select logic

let curriculumData = null; // Cached curriculum data from API

// Chinese numeral sort helper
const CN_NUM = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10};

function chineseSort(a, b) {
    // Extract leading Chinese numeral (e.g. "四年级" → 4, "第一单元" → 1)
    const getNum = s => {
        const m = s.match(/^[第]?(一|二|三|四|五|六|七|八|九|十)/);
        return m ? (CN_NUM[m[1]] || 0) : 0;
    };
    const na = getNum(a), nb = getNum(b);
    if (na !== nb) return na - nb;
    // Secondary: 上册 before 下册
    const ua = a.includes('上册') ? 0 : (a.includes('下册') ? 1 : 2);
    const ub = b.includes('上册') ? 0 : (b.includes('下册') ? 1 : 2);
    if (ua !== ub) return ua - ub;
    return a.localeCompare(b, 'zh');
}

async function loadCurriculumData() {
    if (!curriculumData) {
        curriculumData = await ZhibeiAPI.getCurriculum();
    }
    return curriculumData;
}

function populateGradeSelect() {
    const gradeSelect = document.getElementById('gradeSelect');
    if (!curriculumData) return;
    gradeSelect.innerHTML = '';
    const grades = Object.keys(curriculumData).sort(chineseSort);
    grades.forEach(grade => {
        const opt = document.createElement('option');
        opt.value = grade;
        opt.textContent = grade;
        gradeSelect.appendChild(opt);
    });
    // Default to 四年级上册
    if (grades.includes('四年级上册')) {
        gradeSelect.value = '四年级上册';
    }
}

function populateUnitSelect(grade) {
    const unitSelect = document.getElementById('unitSelect');
    if (!curriculumData) return;
    unitSelect.innerHTML = '';
    if (!curriculumData[grade]) return;
    const units = Object.keys(curriculumData[grade]).sort(chineseSort);
    units.forEach(unit => {
        const opt = document.createElement('option');
        opt.value = unit;
        opt.textContent = unit;
        // Store unit number from first lesson's unitNumber
        const firstLesson = curriculumData[grade][unit][0];
        if (firstLesson && firstLesson.unitNumber) {
            opt.dataset.unitNumber = firstLesson.unitNumber;
        }
        unitSelect.appendChild(opt);
    });
    // Add placeholder if no units
    if (units.length === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = '—';
        unitSelect.appendChild(opt);
    }
}

function populateTitleSelect(grade, unit) {
    const titleSelect = document.getElementById('titleSelect');
    titleSelect.innerHTML = '';
    if (!curriculumData || !curriculumData[grade] || !curriculumData[grade][unit]) return;
    const lessons = curriculumData[grade][unit];
    lessons.forEach(lesson => {
        const opt = document.createElement('option');
        opt.value = lesson.name;
        opt.textContent = lesson.name;
        opt.dataset.type = lesson.type;
        opt.dataset.focus = (lesson.focus || []).join(',');
        if (lesson.lessonNumber) {
            opt.dataset.lessonNumber = lesson.lessonNumber;
        }
        titleSelect.appendChild(opt);
    });
    if (lessons.length === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = '—';
        titleSelect.appendChild(opt);
    }
}

function onGradeChange() {
    const grade = document.getElementById('gradeSelect').value;
    populateUnitSelect(grade);
    onUnitChange();
}

function onUnitChange() {
    const grade = document.getElementById('gradeSelect').value;
    const unit = document.getElementById('unitSelect').value;
    populateTitleSelect(grade, unit);
    onTitleChange();
}

async function onTitleChange() {
    const titleSelect = document.getElementById('titleSelect');
    const selected = titleSelect.selectedOptions[0];
    const type = selected ? (selected.dataset.type || '') : '';
    const focusArr = selected ? (selected.dataset.focus ? selected.dataset.focus.split(',') : []) : [];

    await updateUnitFocusSection(document.getElementById('gradeSelect').value, document.getElementById('unitSelect').value);
    updateFocusCheckboxes(type, focusArr, titleSelect.value);
    updateCardSummaries();
}
