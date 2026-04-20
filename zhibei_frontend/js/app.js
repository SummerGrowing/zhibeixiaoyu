// Main application logic - 智备小语

let currentProviders = null;

// Scroll state tracking for streaming
let userScrolledPrompt = false;
let userScrolledTeaching = false;

// Streaming abort controller
let promptAbortController = null;
let fragmentAbortController = null;

// ============================================================
// Button reset helpers
// ============================================================

function resetPromptBtn() {
    const btn = document.getElementById('generatePromptBtn');
    if (btn) {
        btn.classList.remove('loading');
        btn.textContent = '生成专业提示语';
    }
}

function resetFragmentBtn() {
    const btn = document.getElementById('generateFragmentBtn');
    if (btn) {
        btn.classList.remove('loading');
        btn.innerHTML = '生成完整的教学设计';
    }
}

function abortPromptStream() {
    if (promptAbortController) {
        promptAbortController.abort();
        promptAbortController = null;
    }
    resetPromptBtn();
    setStreamingStatus('prompt', false);
}

function abortFragmentStream() {
    if (fragmentAbortController) {
        fragmentAbortController.abort();
        fragmentAbortController = null;
    }
    resetFragmentBtn();
    setStreamingStatus('fragment', false);
}

// ============================================================
// Streaming status indicator
// ============================================================

function setStreamingStatus(target, isStreaming) {
    let indicator;
    if (target === 'prompt') {
        indicator = document.getElementById('promptStreamStatus');
    } else {
        indicator = document.getElementById('fragmentStreamStatus');
    }
    if (!indicator) return;
    if (isStreaming) {
        indicator.textContent = '生成中...';
        indicator.classList.add('streaming-active');
    } else {
        indicator.textContent = '生成完毕';
        indicator.classList.remove('streaming-active');
        setTimeout(() => { indicator.textContent = ''; }, 2000);
    }
}

// ============================================================
// Text cleanup - remove markdown formatting characters
// ============================================================

function cleanMarkdown(text) {
    let t = text;
    // Remove horizontal rules (--- or *** or ___)
    t = t.replace(/^[-*_]{3,}\s*$/gm, '');
    // Remove heading markers (# ## ### etc.)
    t = t.replace(/^#{1,6}\s+/gm, '');
    // Remove bold markers (**text** or __text__)
    t = t.replace(/\*\*(.+?)\*\*/g, '$1');
    t = t.replace(/__(.+?)__/g, '$1');
    // Remove italic markers (*text* or _text_)
    t = t.replace(/\*(.+?)\*/g, '$1');
    t = t.replace(/_(.+?)_/g, '$1');
    // Remove <br> tags
    t = t.replace(/<br\s*\/?>/gi, '\n');
    // Remove other HTML tags
    t = t.replace(/<[^>]+>/g, '');
    return t;
}

// ============================================================
// Toast utilities
// ============================================================

function showToast(msg) {
    const toast = document.getElementById('toast');
    toast.textContent = msg || '复制成功！';
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 1500);
}

function showSaveToast() {
    document.getElementById('saveToast').classList.add('show');
    setTimeout(() => document.getElementById('saveToast').classList.remove('show'), 1500);
}

async function copyText(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast();
    } catch (err) {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast();
    }
}

// ============================================================
// Steps modal
// ============================================================

document.getElementById('startBtn').addEventListener('click', () => {
    document.getElementById('stepsModal').classList.remove('hidden');
});

document.getElementById('confirmStartBtn').addEventListener('click', () => {
    document.getElementById('stepsModal').classList.add('hidden');
    document.getElementById('landingPage').classList.add('hidden');
    document.getElementById('mainInterface').classList.remove('hidden');
    document.getElementById('guidePage').classList.add('hidden');
});

document.getElementById('closeStepsBtn').addEventListener('click', () => {
    document.getElementById('stepsModal').classList.add('hidden');
});

// ============================================================
// Teaching panel show/hide (inline in mainInterface)
// ============================================================

function showTeachingPanel() {
    const layoutArea = document.getElementById('layoutArea');
    const bottomBtn = document.getElementById('bottomGenerateBtn');
    const teachingPanel = document.getElementById('teachingPanel');
    layoutArea.classList.add('hidden');
    bottomBtn.classList.add('hidden');
    teachingPanel.classList.remove('hidden');
}

function hideTeachingPanel() {
    const layoutArea = document.getElementById('layoutArea');
    const bottomBtn = document.getElementById('bottomGenerateBtn');
    const teachingPanel = document.getElementById('teachingPanel');
    teachingPanel.classList.add('hidden');
    layoutArea.classList.remove('hidden');
    bottomBtn.classList.remove('hidden');
    resetFragmentBtn();
}

// ============================================================
// Page navigation
// ============================================================

document.getElementById('guideLink').addEventListener('click', () => {
    document.getElementById('landingPage').classList.add('hidden');
    document.getElementById('guidePage').classList.remove('hidden');
    document.getElementById('mainInterface').classList.add('hidden');
});

document.getElementById('backFromGuideBtn').addEventListener('click', () => {
    document.getElementById('guidePage').classList.add('hidden');
    document.getElementById('landingPage').classList.remove('hidden');
});

document.getElementById('returnFromTeachingBtn').addEventListener('click', () => {
    abortFragmentStream();
    hideTeachingPanel();
    enterCompactMode();
});

document.getElementById('homeFromMainBtn').addEventListener('click', () => {
    exitCompactMode();
    hideTeachingPanel();
    abortPromptStream();
    abortFragmentStream();
    document.getElementById('mainInterface').classList.add('hidden');
    document.getElementById('landingPage').classList.remove('hidden');
    document.getElementById('guidePage').classList.add('hidden');
});

// ============================================================
// Helper: extract position numbers from selects
// ============================================================

function getPositionNumbers() {
    const titleSelect = document.getElementById('titleSelect');
    const unitSelect = document.getElementById('unitSelect');
    const selected = titleSelect.selectedOptions[0];
    const selectedUnit = unitSelect.selectedOptions[0];
    return {
        unitNumber: selectedUnit ? (selectedUnit.dataset.unitNumber || 1) : 1,
        lessonNumber: selected ? (selected.dataset.lessonNumber || 1) : 1
    };
}

// ============================================================
// Cascading select event handlers
// ============================================================

document.getElementById('gradeSelect').addEventListener('change', onGradeChange);
document.getElementById('unitSelect').addEventListener('change', onUnitChange);
document.getElementById('titleSelect').addEventListener('change', onTitleChange);

// Checkbox change handlers
document.getElementById('focusCheckboxGrid').addEventListener('change', updateCardSummaries);
document.getElementById('basicOptionsGrid').addEventListener('change', updateCardSummaries);
document.getElementById('unitFocusGroup').addEventListener('change', updateCardSummaries);
document.getElementById('otherFocus').addEventListener('input', updateCardSummaries);
document.getElementById('ideaText').addEventListener('input', updateCardSummaries);
document.getElementById('keyWordsCheckbox')?.addEventListener('change', updateCardSummaries);

// Copy prompt button
document.getElementById('copyPromptBtn').addEventListener('click', () => {
    copyText(document.getElementById('editablePrompt').value);
});

// ============================================================
// Provider/model selector
// ============================================================

async function loadProviders() {
    try {
        currentProviders = await ZhibeiAPI.getProviders();
        populateProviderSelect();
    } catch (e) {
        console.error('Failed to load providers:', e);
    }
}

function populateProviderSelect() {
    const providerSelect = document.getElementById('providerSelect');
    providerSelect.innerHTML = '<option value="">本地模板</option>';

    if (!currentProviders) return;

    for (const [id, info] of Object.entries(currentProviders)) {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = info.name + (info.hasKey ? '' : '（未配置）');
        providerSelect.appendChild(opt);
    }
}

function populateModelSelect(providerId) {
    const modelSelect = document.getElementById('modelSelect');
    modelSelect.innerHTML = '<option value="">选择模型</option>';

    if (!providerId || !currentProviders || !currentProviders[providerId]) return;

    const models = currentProviders[providerId].models;
    models.forEach(model => {
        const opt = document.createElement('option');
        opt.value = model;
        opt.textContent = model;
        modelSelect.appendChild(opt);
    });
}

document.getElementById('providerSelect').addEventListener('change', (e) => {
    populateModelSelect(e.target.value);
});

// ============================================================
// Generate Prompt (with SSE streaming)
// ============================================================

document.getElementById('generatePromptBtn').addEventListener('click', async () => {
    enterCompactMode();

    const generatePromptBtn = document.getElementById('generatePromptBtn');
    const editablePrompt = document.getElementById('editablePrompt');
    generatePromptBtn.classList.add('loading');
    generatePromptBtn.innerHTML = '<span class="loading-spinner"></span>生成中...';

    const grade = document.getElementById('gradeSelect').value;
    const unit = document.getElementById('unitSelect').value;
    const lesson = document.getElementById('titleSelect').value;
    const titleSelect = document.getElementById('titleSelect');
    const selected = titleSelect.selectedOptions[0];
    const textType = selected ? (selected.dataset.type || '散文') : '散文';
    const focuses = getSelectedFocusTexts();
    const otherFocus = document.getElementById('otherFocus').value.trim();
    const idea = document.getElementById('ideaText').value.trim();
    const provider = document.getElementById('providerSelect').value;
    const model = document.getElementById('modelSelect').value;
    const { unitNumber, lessonNumber } = getPositionNumbers();

    if (!provider || !model) {
        // No provider selected - get local template from backend
        try {
            const result = await ZhibeiAPI.generatePromptSync({
                grade, unit, lesson, textType, focuses, otherFocus, idea, unitNumber, lessonNumber
            });
            editablePrompt.value = cleanMarkdown(result.prompt);
            window.currentPrompt = editablePrompt.value;
            showSaveToast();
            showToast('提示：选择AI模型后可获得更专业的生成结果');
        } catch (e) {
            console.error('Local prompt generation failed:', e);
            editablePrompt.value = '生成失败，请检查后端服务是否正常启动。';
        }
        generatePromptBtn.classList.remove('loading');
        generatePromptBtn.textContent = '生成专业提示语';
        return;
    }

    // AI streaming generation
    let fullText = '';
    editablePrompt.value = '';
    userScrolledPrompt = false;
    setStreamingStatus('prompt', true);

    promptAbortController = new AbortController();

    await ZhibeiAPI.streamGenerate(
        '/generate-prompt',
        { grade, unit, lesson, textType, focuses, otherFocus, idea, provider, model, unitNumber, lessonNumber },
        (chunk) => {
            fullText += chunk;
            const cleaned = cleanMarkdown(fullText);
            editablePrompt.value = cleaned;
            if (!userScrolledPrompt) editablePrompt.scrollTop = editablePrompt.scrollHeight;
        },
        () => {
            // onDone
            promptAbortController = null;
            const cleaned = cleanMarkdown(fullText);
            editablePrompt.value = cleaned;
            window.currentPrompt = cleaned;
            generatePromptBtn.classList.remove('loading');
            generatePromptBtn.textContent = '生成专业提示语';
            setStreamingStatus('prompt', false);
            showSaveToast();
        },
        (error) => {
            // onError - fall back to local template
            promptAbortController = null;
            console.error('AI generation failed:', error);
            generatePromptBtn.classList.remove('loading');
            generatePromptBtn.textContent = '生成专业提示语';
            showToast('AI调用失败，尝试本地模板...');

            // Fallback to local
            ZhibeiAPI.generatePromptSync({
                grade, unit, lesson, textType, focuses, otherFocus, idea, unitNumber, lessonNumber
            }).then(result => {
            editablePrompt.value = cleanMarkdown(result.prompt);
            window.currentPrompt = editablePrompt.value;
                showSaveToast();
            }).catch(() => {
                editablePrompt.value = '生成失败，请检查后端服务。';
            });
        },
        promptAbortController ? promptAbortController.signal : undefined
    );
});

// ============================================================
// Generate Fragment (with SSE streaming)
// ============================================================

document.getElementById('generateFragmentBtn').addEventListener('click', async () => {
    const generateFragmentBtn = document.getElementById('generateFragmentBtn');
    const editablePrompt = document.getElementById('editablePrompt');
    const teachingContent = document.getElementById('teachingContent');
    const teachingFooter = document.querySelector('.teaching-panel .teaching-footer:not(#teachingEditFooter)');
    const teachingEditFooter = document.getElementById('teachingEditFooter');

    const provider = document.getElementById('providerSelect').value;
    const model = document.getElementById('modelSelect').value;
    const promptText = editablePrompt.value;

    const grade = document.getElementById('gradeSelect').value;
    const unit = document.getElementById('unitSelect').value;
    const lesson = document.getElementById('titleSelect').value;
    const titleSelect = document.getElementById('titleSelect');
    const selected = titleSelect.selectedOptions[0];
    const textType = selected ? (selected.dataset.type || '散文') : '散文';
    const focuses = getSelectedFocusTexts();
    const otherFocus = document.getElementById('otherFocus').value.trim();
    const idea = document.getElementById('ideaText').value.trim();
    const { unitNumber, lessonNumber } = getPositionNumbers();

    if (!provider || !model) {
        // Local template
        try {
            const result = await ZhibeiAPI.generateFragmentSync({
                prompt: promptText, grade, unit, lesson, textType, focuses, otherFocus, idea, unitNumber, lessonNumber
            });
            teachingContent.textContent = cleanMarkdown(result.fragment);
            teachingContent.setAttribute('contenteditable', 'false');
            originalTeachingContent = teachingContent.textContent;
            showTeachingPanel();
            teachingFooter.classList.remove('hidden');
            teachingEditFooter.classList.add('hidden');
            showToast('已使用本地模板生成，选择AI模型后可获得更好效果');
        } catch (e) {
            showToast('生成失败，请检查后端服务');
        }
        return;
    }

    // AI streaming generation
    generateFragmentBtn.classList.add('loading');
    generateFragmentBtn.innerHTML = '<span class="loading-spinner"></span>生成中...';

    let fullText = '';
    teachingContent.textContent = '';
    showTeachingPanel();
    teachingFooter.classList.remove('hidden');
    teachingEditFooter.classList.add('hidden');
    teachingContent.setAttribute('contenteditable', 'false');
    setStreamingStatus('fragment', true);

    fragmentAbortController = new AbortController();

    await ZhibeiAPI.streamGenerate(
        '/generate-fragment',
        { prompt: promptText, grade, unit, lesson, textType, focuses, otherFocus, idea, provider, model, unitNumber, lessonNumber },
        (chunk) => {
            fullText += chunk;
            const cleaned = cleanMarkdown(fullText);
            teachingContent.textContent = cleaned;
            if (!userScrolledTeaching) scrollToBottomOfTeaching();
        },
        () => {
            fragmentAbortController = null;
            const cleaned = cleanMarkdown(fullText);
            teachingContent.textContent = cleaned;
            originalTeachingContent = cleaned;
            generateFragmentBtn.classList.remove('loading');
            generateFragmentBtn.innerHTML = '生成完整的教学设计';
            setStreamingStatus('fragment', false);
        },
        (error) => {
            fragmentAbortController = null;
            console.error('Fragment generation failed:', error);
            generateFragmentBtn.classList.remove('loading');
            generateFragmentBtn.innerHTML = '生成完整的教学设计';
            showToast('AI调用失败，尝试本地模板...');

            // Fallback to local
            ZhibeiAPI.generateFragmentSync({
                prompt: promptText, grade, unit, lesson, textType, focuses, otherFocus, idea, unitNumber, lessonNumber
            }).then(result => {
            teachingContent.textContent = cleanMarkdown(result.fragment);
            originalTeachingContent = teachingContent.textContent;
            }).catch(() => {
                teachingContent.textContent = '生成失败，请检查后端服务。';
            });
        },
        fragmentAbortController ? fragmentAbortController.signal : undefined
    );
});

// ============================================================
// Edit prompt toggle
// ============================================================

const editPromptBtn = document.getElementById('editPromptBtn');
const editablePrompt = document.getElementById('editablePrompt');

editPromptBtn.addEventListener('click', () => {
    if (editablePrompt.hasAttribute('readonly')) {
        editablePrompt.removeAttribute('readonly');
        editablePrompt.classList.add('editing');
        editablePrompt.focus();
        editPromptBtn.textContent = '完成编辑';
        editPromptBtn.classList.add('btn-solid');
        editPromptBtn.classList.remove('btn-outline');
    } else {
        editablePrompt.setAttribute('readonly', '');
        editablePrompt.classList.remove('editing');
        editPromptBtn.textContent = '编辑';
        editPromptBtn.classList.remove('btn-solid');
        editPromptBtn.classList.add('btn-outline');
        window.currentPrompt = editablePrompt.value;
    }
});

// ============================================================
// Auto-save prompt
// ============================================================

let saveTimeout;
document.getElementById('editablePrompt').addEventListener('input', () => {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
        window.currentPrompt = document.getElementById('editablePrompt').value;
        showSaveToast();
    }, 500);
});
document.getElementById('editablePrompt').addEventListener('blur', () => {
    clearTimeout(saveTimeout);
    window.currentPrompt = document.getElementById('editablePrompt').value;
});

// ============================================================
// Scroll tracking for streaming - detect user manual scroll
// ============================================================

document.getElementById('editablePrompt').addEventListener('scroll', () => {
    const el = document.getElementById('editablePrompt');
    userScrolledPrompt = (el.scrollTop + el.clientHeight + 30) < el.scrollHeight;
});

document.getElementById('teachingContent').addEventListener('scroll', () => {
    const el = document.getElementById('teachingContent');
    userScrolledTeaching = (el.scrollTop + el.clientHeight + 30) < el.scrollHeight;
});

// ============================================================
// Initialization
// ============================================================

async function init() {
    try {
        await loadCurriculumData();
        populateGradeSelect();
        onGradeChange();
        await loadProviders();
    } catch (e) {
        console.error('Initialization failed:', e);
        showToast('初始化失败，请检查后端服务是否启动');
    }
}

init();
