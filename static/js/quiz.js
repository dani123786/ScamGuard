/**
 * quiz.js — Main knowledge quiz logic.
 * Fully redesigned for ScamGuard dark theme.
 */

let questions = [];
let currentQuestion = 0;
let userAnswers = [];
let selectedDifficulty = '';
let userName = '';

document.addEventListener('DOMContentLoaded', function () {
    injectQuizStyles();

    document.getElementById('user-name').addEventListener('input', checkNameInput);

    document.querySelectorAll('.difficulty-card').forEach(function (card) {
        card.addEventListener('click', function () {
            document.querySelectorAll('.difficulty-card').forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            selectedDifficulty = this.dataset.difficulty;
            document.getElementById('quiz-setup').style.display = 'none';
            document.getElementById('name-input-section').style.display = 'block';
        });
    });

    document.getElementById('back-to-difficulty').addEventListener('click', function () {
        document.getElementById('name-input-section').style.display = 'none';
        document.getElementById('quiz-setup').style.display = 'block';
        document.getElementById('user-name').value = '';
        document.getElementById('start-quiz').disabled = true;
    });

    document.getElementById('start-quiz').addEventListener('click', startQuiz);
    document.getElementById('next-btn').addEventListener('click', nextQuestion);
    document.getElementById('prev-btn').addEventListener('click', prevQuestion);
    document.getElementById('submit-btn').addEventListener('click', submitQuiz);
    document.getElementById('retake-quiz').addEventListener('click', function () {
        location.reload();
    });
});

function injectQuizStyles() {
    if (document.getElementById('qz-injected-styles')) return;
    const style = document.createElement('style');
    style.id = 'qz-injected-styles';
    style.textContent = `
        /* ── Main Quiz Question Card ── */
        .qz-q-card {
            background: #0e1628;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 16px;
            padding: 28px;
        }
        .qz-q-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
        }
        .qz-q-label {
            font-size: 0.72rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.1em;
            color: #06d6a0;
            display: flex; align-items: center; gap: 6px;
        }
        .qz-q-label-dot {
            width: 6px; height: 6px; border-radius: 50%; background: #06d6a0;
        }
        .qz-q-counter-pill {
            font-family: 'DM Mono', monospace;
            font-size: 0.72rem; color: #7a8aaa;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.07);
            padding: 4px 12px; border-radius: 100px;
        }
        .qz-q-text {
            font-family: 'Outfit', sans-serif;
            font-size: 1.05rem; font-weight: 600;
            color: #fff; line-height: 1.55; margin-bottom: 22px;
        }
        .qz-opts { display: flex; flex-direction: column; gap: 10px; }
        .qz-opt {
            display: flex; align-items: center; gap: 14px;
            background: #141e35;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 11px; padding: 14px 18px;
            cursor: pointer; transition: all 0.18s; user-select: none;
        }
        .qz-opt:hover {
            border-color: rgba(6,214,160,0.3);
            background: rgba(6,214,160,0.04);
        }
        .qz-opt.selected {
            border-color: rgba(6,214,160,0.45);
            background: rgba(6,214,160,0.08);
        }
        .qz-opt-letter {
            width: 32px; height: 32px; border-radius: 9px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            display: flex; align-items: center; justify-content: center;
            font-size: 0.78rem; font-weight: 700; color: #7a8aaa;
            flex-shrink: 0; transition: all 0.18s;
        }
        .qz-opt.selected .qz-opt-letter {
            background: rgba(6,214,160,0.18);
            border-color: rgba(6,214,160,0.4);
            color: #06d6a0;
        }
        .qz-opt-text {
            font-size: 0.9rem; color: #c0c8d8; line-height: 1.45; transition: color 0.18s;
        }
        .qz-opt.selected .qz-opt-text { color: #06d6a0; }

        /* ── Main Quiz Results ── */
        .qz-res-hero {
            background: linear-gradient(135deg, #0d1f3c 0%, #0e1628 100%);
            padding: 48px 40px 36px; text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.07);
        }
        .qz-res-username {
            font-family: 'Outfit', sans-serif;
            font-size: 1.3rem; font-weight: 700; color: #fff;
            margin-bottom: 4px;
        }
        .qz-res-username span { color: #06d6a0; }
        .qz-diff-pill {
            display: inline-flex; align-items: center; gap: 5px;
            font-size: 0.75rem; font-weight: 600;
            padding: 4px 14px; border-radius: 100px; margin-bottom: 24px;
        }
        .qz-diff-pill.easy     { background: rgba(6,214,160,0.1);  color: #06d6a0; border: 1px solid rgba(6,214,160,0.25); }
        .qz-diff-pill.medium   { background: rgba(245,158,11,0.1); color: #f59e0b; border: 1px solid rgba(245,158,11,0.25); }
        .qz-diff-pill.difficult{ background: rgba(251,79,79,0.1);  color: #fb4f4f; border: 1px solid rgba(251,79,79,0.25); }

        .qz-res-ring {
            width: 120px; height: 120px; border-radius: 50%;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            margin: 0 auto 20px; border: 3px solid;
            font-family: 'Outfit', sans-serif;
        }
        .qz-res-ring .r-pct  { font-size: 2.2rem; font-weight: 800; line-height: 1; }
        .qz-res-ring .r-frac { font-size: 0.78rem; font-weight: 400; opacity: 0.65; margin-top: 3px; }
        .qz-res-ring.great  { border-color: #06d6a0; color: #06d6a0; background: rgba(6,214,160,0.07); }
        .qz-res-ring.mid    { border-color: #f59e0b; color: #f59e0b; background: rgba(245,158,11,0.07); }
        .qz-res-ring.low    { border-color: #fb4f4f; color: #fb4f4f; background: rgba(251,79,79,0.07); }

        .qz-res-title { font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; color: #fff; margin-bottom: 6px; }
        .qz-res-msg   { font-size: 0.875rem; color: #7a8aaa; margin-bottom: 24px; }

        .qz-stat-row { display: flex; justify-content: center; gap: 14px; flex-wrap: wrap; }
        .qz-stat {
            text-align: center; background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 12px; padding: 12px 22px; min-width: 88px;
        }
        .qz-stat .sv { font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 700; }
        .qz-stat .sl { font-size: 0.7rem; color: #7a8aaa; margin-top: 2px; }
        .qz-stat.c .sv { color: #06d6a0; }
        .qz-stat.w .sv { color: #fb4f4f; }
        .qz-stat.p .sv { color: #fff; }

        /* ── Result detail items ── */
        .qz-res-section { padding: 28px; }
        .qz-res-section-label {
            font-size: 0.7rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.1em;
            color: #7a8aaa; margin-bottom: 16px;
            display: flex; align-items: center; gap: 8px;
        }
        .qz-res-section-label::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.07); }

        .qz-ri {
            background: #141e35; border: 1px solid rgba(255,255,255,0.07);
            border-radius: 12px; padding: 18px 20px; margin-bottom: 12px;
        }
        .qz-ri.correct   { border-left: 3px solid #06d6a0; }
        .qz-ri.incorrect { border-left: 3px solid #fb4f4f; }

        .qz-ri-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
        .qz-ri-badge {
            display: inline-flex; align-items: center; gap: 5px;
            font-size: 0.68rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.06em;
            padding: 2px 8px; border-radius: 100px;
        }
        .qz-ri-badge.c { background: rgba(6,214,160,0.1);  color: #06d6a0; border: 1px solid rgba(6,214,160,0.2); }
        .qz-ri-badge.w { background: rgba(251,79,79,0.08); color: #fb4f4f; border: 1px solid rgba(251,79,79,0.2); }
        .qz-ri-qnum { font-size: 0.72rem; color: #7a8aaa; font-family: 'DM Mono', monospace; }

        .qz-ri-q { font-family: 'Outfit', sans-serif; font-size: 0.9rem; font-weight: 600; color: #fff; margin-bottom: 10px; line-height: 1.5; }
        .qz-ri-answers { display: flex; flex-direction: column; gap: 5px; margin-bottom: 10px; }
        .qz-ri-ans { display: flex; align-items: flex-start; gap: 8px; font-size: 0.82rem; line-height: 1.4; }
        .qz-ri-ans-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; min-width: 52px; padding-top: 2px; }
        .qz-ri-ans-label.your    { color: #7a8aaa; }
        .qz-ri-ans-label.correct { color: #06d6a0; }
        .qz-ri-ans-text          { color: #c0c8d8; }
        .qz-ri-ans-text.wrong    { color: #fb4f4f; }
        .qz-ri-ans-text.right    { color: #06d6a0; }

        .qz-ri-explanation {
            display: flex; align-items: flex-start; gap: 7px;
            background: rgba(255,255,255,0.03); border-radius: 8px;
            padding: 9px 12px; font-size: 0.78rem; color: #7a8aaa; line-height: 1.5;
        }
        .qz-ri-explanation i { color: #a78bfa; margin-top: 2px; flex-shrink: 0; font-size: 0.72rem; }
    `;
    document.head.appendChild(style);
}

function checkNameInput() {
    const name = document.getElementById('user-name').value.trim();
    document.getElementById('start-quiz').disabled = !name;
}

async function startQuiz() {
    userName = document.getElementById('user-name').value.trim();
    if (!userName || !selectedDifficulty) { alert('Please enter your name!'); return; }

    try {
        const response = await fetch('/api/quiz/questions?difficulty=' + selectedDifficulty);
        questions    = await response.json();
        userAnswers  = new Array(questions.length).fill(null);
    } catch (e) {
        console.error('Failed to load questions:', e);
        return;
    }

    document.getElementById('name-input-section').style.display = 'none';
    document.getElementById('quiz-questions').style.display     = 'block';

    // Update meta badges
    const userEl = document.getElementById('user-display');
    if (userEl) userEl.innerHTML = '<i class="fas fa-user" style="font-size:0.7rem;"></i> ' + userName;

    const diffEl = document.getElementById('difficulty-display');
    if (diffEl) {
        const cap = selectedDifficulty.charAt(0).toUpperCase() + selectedDifficulty.slice(1);
        diffEl.textContent = cap;
        diffEl.className   = 'badge-diff ' + selectedDifficulty;
    }

    showQuestion(0);
}

function showQuestion(index) {
    currentQuestion = index;
    const question  = questions[index];
    const total     = questions.length;
    const progress  = ((index + 1) / total) * 100;

    document.getElementById('quiz-progress').style.width = progress + '%';

    // Update counter pill if present
    const counterEl = document.getElementById('question-counter');
    if (counterEl) counterEl.textContent = (index + 1) + ' / ' + total;

    const letters = ['A', 'B', 'C', 'D', 'E'];
    const optsHTML = question.options.map(function (opt, i) {
        const sel = userAnswers[index] === i ? ' selected' : '';
        return '<div class="qz-opt' + sel + '" data-idx="' + i + '">' +
            '<div class="qz-opt-letter">' + letters[i] + '</div>' +
            '<div class="qz-opt-text">'  + opt + '</div>' +
        '</div>';
    }).join('');

    const html =
        '<div class="qz-q-card">' +
            '<div class="qz-q-top">' +
                '<div class="qz-q-label"><div class="qz-q-label-dot"></div>Question ' + (index + 1) + '</div>' +
                '<div class="qz-q-counter-pill">' + (index + 1) + ' / ' + total + '</div>' +
            '</div>' +
            '<div class="qz-q-text">' + question.question + '</div>' +
            '<div class="qz-opts">' + optsHTML + '</div>' +
        '</div>';

    document.getElementById('question-container').innerHTML = html;

    document.querySelectorAll('.qz-opt').forEach(function (el) {
        el.addEventListener('click', function () {
            userAnswers[index] = parseInt(this.dataset.idx);
            document.querySelectorAll('.qz-opt').forEach(o => o.classList.remove('selected'));
            this.classList.add('selected');
            updateButtons();
        });
    });

    updateButtons();
}

function updateButtons() {
    const total   = questions.length;
    const cur     = currentQuestion;
    const answered = userAnswers[cur] !== null;
    const allDone  = userAnswers.every(a => a !== null);

    document.getElementById('prev-btn').style.display   = cur > 0 ? 'inline-flex' : 'none';
    document.getElementById('next-btn').style.display   = (cur < total - 1 && answered) ? 'inline-flex' : 'none';
    document.getElementById('submit-btn').style.display = (cur === total - 1 && allDone) ? 'inline-flex' : 'none';
}

function nextQuestion() { if (currentQuestion < questions.length - 1) showQuestion(currentQuestion + 1); }
function prevQuestion() { if (currentQuestion > 0) showQuestion(currentQuestion - 1); }

async function submitQuiz() {
    let results;
    try {
        const res = await fetch('/api/quiz/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: userAnswers, difficulty: selectedDifficulty, name: userName })
        });
        results = await res.json();
    } catch (e) {
        console.error('Submit failed:', e);
        return;
    }
    showResults(results);
}

function showResults(results) {
    document.getElementById('quiz-questions').style.display = 'none';
    document.getElementById('quiz-results').style.display   = 'block';

    const pct   = Math.round(results.percentage);
    const score = results.score;
    const total = results.total;

    let ringClass, title, msg;
    if (pct >= 90)      { ringClass = 'great'; title = 'Excellent! 🎉'; msg = "Outstanding performance — you really know your scams!"; }
    else if (pct >= 70) { ringClass = 'great'; title = 'Great Job! ⭐'; msg = "You're well-prepared to spot online scams."; }
    else if (pct >= 50) { ringClass = 'mid';   title = 'Good Effort! 💪'; msg = 'A bit more practice and you\'ll be an expert!'; }
    else                { ringClass = 'low';   title = 'Keep Learning 📚'; msg = 'Check the Awareness section and try again.'; }

    const diffCap = selectedDifficulty.charAt(0).toUpperCase() + selectedDifficulty.slice(1);

    // Build hero
    const heroHTML =
        '<div class="qz-res-username">' + results.name + '\'s <span>Results</span></div>' +
        '<div class="qz-diff-pill ' + selectedDifficulty + '">' +
            '<i class="fas fa-layer-group" style="font-size:0.65rem;"></i> ' + diffCap +
        '</div>' +
        '<div class="qz-res-ring ' + ringClass + '">' +
            '<span class="r-pct">' + pct + '%</span>' +
            '<span class="r-frac">' + score + ' / ' + total + '</span>' +
        '</div>' +
        '<div class="qz-res-title">' + title + '</div>' +
        '<div class="qz-res-msg">' + msg + '</div>' +
        '<div class="qz-stat-row">' +
            '<div class="qz-stat c"><div class="sv">' + score + '</div><div class="sl">Correct</div></div>' +
            '<div class="qz-stat w"><div class="sv">' + (total - score) + '</div><div class="sl">Wrong</div></div>' +
            '<div class="qz-stat p"><div class="sv">' + pct + '%</div><div class="sl">Score</div></div>' +
        '</div>';

    // Build detail items
    let detailsHTML = '';
    results.results.forEach(function (result, i) {
        const q            = questions[i];
        const yourAns      = q.options[userAnswers[i]];
        const correctAns   = q.options[q.correct];
        const isCorrect    = result.correct;

        detailsHTML +=
            '<div class="qz-ri ' + (isCorrect ? 'correct' : 'incorrect') + '">' +
                '<div class="qz-ri-header">' +
                    '<span class="qz-ri-badge ' + (isCorrect ? 'c' : 'w') + '">' +
                        '<i class="fas fa-' + (isCorrect ? 'check' : 'times') + '"></i>' +
                        (isCorrect ? 'Correct' : 'Incorrect') +
                    '</span>' +
                    '<span class="qz-ri-qnum">Q' + (i + 1) + '</span>' +
                '</div>' +
                '<div class="qz-ri-q">' + q.question + '</div>' +
                '<div class="qz-ri-answers">' +
                    '<div class="qz-ri-ans">' +
                        '<span class="qz-ri-ans-label your">Your ans:</span>' +
                        '<span class="qz-ri-ans-text ' + (isCorrect ? 'right' : 'wrong') + '">' + yourAns + '</span>' +
                    '</div>' +
                    (!isCorrect ?
                        '<div class="qz-ri-ans">' +
                            '<span class="qz-ri-ans-label correct">Correct:</span>' +
                            '<span class="qz-ri-ans-text right">' + correctAns + '</span>' +
                        '</div>' : '') +
                '</div>' +
                '<div class="qz-ri-explanation">' +
                    '<i class="fas fa-lightbulb"></i>' +
                    (result.explanation || 'No explanation available.') +
                '</div>' +
            '</div>';
    });

    // Inject into existing score-display and results-details
    const scoreEl = document.getElementById('score-display');
    if (scoreEl) {
        // Wrap in hero container if not already
        scoreEl.innerHTML = heroHTML;
        // Also restyle parent .qz-score-hero
        const heroEl = scoreEl.closest('.qz-score-hero');
        if (heroEl) {
            heroEl.style.background = 'linear-gradient(135deg, #0d1f3c 0%, #0e1628 100%)';
            heroEl.style.padding    = '48px 40px 36px';
        }
    }

    const detailsEl = document.getElementById('results-details');
    if (detailsEl) {
        const wrap = detailsEl.closest('.qz-details-wrap');
        if (wrap) wrap.style.padding = '0';
        detailsEl.innerHTML =
            '<div class="qz-res-section">' +
                '<div class="qz-res-section-label">Question Review</div>' +
                detailsHTML +
            '</div>';
    }
}
