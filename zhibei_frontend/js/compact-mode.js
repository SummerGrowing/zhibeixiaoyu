// Compact mode and card navigation

let activeCardIndex = -1;

function enterCompactMode() {
    const layoutArea = document.getElementById('layoutArea');
    const bottomBtn = document.getElementById('bottomGenerateBtn');
    const cards = [
        document.getElementById('card1'),
        document.getElementById('card2'),
        document.getElementById('card3')
    ];

    layoutArea.classList.add('layout-compact');
    bottomBtn.classList.add('hidden');
    updateCardSummaries();

    cards[0].querySelector('.card-summary').style.display = 'block';
    cards.forEach(card => card.classList.remove('active-card'));
    activeCardIndex = -1;
}

function exitCompactMode() {
    const layoutArea = document.getElementById('layoutArea');
    const bottomBtn = document.getElementById('bottomGenerateBtn');
    const cards = [
        document.getElementById('card1'),
        document.getElementById('card2'),
        document.getElementById('card3')
    ];

    layoutArea.classList.remove('layout-compact');
    bottomBtn.classList.remove('hidden');
    cards.forEach(card => {
        card.querySelector('.card-summary').style.display = 'none';
        card.classList.remove('active-card');
    });
    activeCardIndex = -1;

    // Reset prompt button if it was stuck in loading
    if (typeof resetPromptBtn === 'function') resetPromptBtn();
}

function setActiveCard(index) {
    const cards = [
        document.getElementById('card1'),
        document.getElementById('card2'),
        document.getElementById('card3')
    ];
    if (index < 0 || index >= cards.length) {
        cards.forEach(c => c.classList.remove('active-card'));
        activeCardIndex = -1;
        return;
    }
    cards.forEach(c => c.classList.remove('active-card'));
    cards[index].classList.add('active-card');
    activeCardIndex = index;
}

document.getElementById('reselectFocusBtn').addEventListener('click', exitCompactMode);

document.getElementById('cardsRow').addEventListener('wheel', (e) => {
    if (!document.getElementById('layoutArea').classList.contains('layout-compact')) return;
    e.preventDefault();
    let newIndex;
    const cardsCount = 3;
    if (e.deltaY > 0) {
        if (activeCardIndex === -1) newIndex = 0;
        else newIndex = (activeCardIndex + 1) % cardsCount;
    } else {
        if (activeCardIndex === -1) newIndex = cardsCount - 1;
        else newIndex = (activeCardIndex - 1 + cardsCount) % cardsCount;
    }
    setActiveCard(newIndex);
});
