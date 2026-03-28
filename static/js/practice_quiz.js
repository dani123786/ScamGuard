/**
 * practice_quiz.js — Practice quiz for scam detail pages.
 * Fully redesigned for ScamGuard dark theme.
 */

var practiceQuestions = [];
var currentPracticeQuestion = 0;
var practiceAnswers = [];

document.addEventListener('DOMContentLoaded', function () {
    var dataEl = document.getElementById('practice-questions-data');
    if (!dataEl) return;

    try {
        practiceQuestions = JSON.parse(dataEl.textContent || '[]');
    } catch (e) {
        console.error('Failed to parse practice questions:', e);
        return;
    }

    if (!practiceQuestions || practiceQuestions.length === 0) return;

    injectPracticeStyles();

    document.getElementById('start-practice-quiz').addEventListener('click', startPracticeQuiz);
    document.getElementById('practice-next-btn').addEventListener('click', nextPracticeQuestion);
    document.getElementById('practice-prev-btn').addEventListener('click', prevPracticeQuestion);
    document.getElementById('practice-submit-btn').addEventListener('click', submitPracticeQuiz);
    document.getElementById('practice-retake-btn').addEventListener('click', function () {
        document.getElementById('practice-quiz-results').style.display = 'none';
        document.getElementById('practice-quiz-intro').style.display = 'block';
        currentPracticeQuestion = 0;
        practiceAnswers = [];
    });
});

function injectPracticeStyles() {
    if (document.getElementById('pq-injected-styles')) return;
    var style = document.createElement('style');
    style.id = 'pq-injected-styles';
    style.textContent = `
        /* ── Practice Quiz Question Card ── */
        .pq-card {
            background: #141e35;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 14px;
            padding: 26px 24px;
        }
        .pq-q-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }
        .pq-q-num {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #a78bfa;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .pq-q-num-dot {
            width: 6px; height: 6px;
            border-radius: 50%;
            background: #a78bfa;
        }
        .pq-q-counter {
            font-family: 'DM Mono', monospace;
            font-size: 0.72rem;
            color: #7a8aaa;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.07);
            padding: 3px 10px;
            border-radius: 100px;
        }
        .pq-q-text {
            font-family: 'Outfit', sans-serif;
            font-size: 1rem;
            font-weight: 600;
            color: #fff;
            line-height: 1.55;
            margin-bottom: 20px;
        }
        .pq-options { display: flex; flex-direction: column; gap: 9px; }
        .pq-opt {
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 10px;
            padding: 12px 16px;
            cursor: pointer;
            transition: all 0.18s;
            user-select: none;
        }
        .pq-opt:hover {
            border-color: rgba(167,139,250,0.3);
            background: rgba(167,139,250,0.05);
            color: #e8edf8;
        }
        .pq-opt.selected {
            border-color: rgba(167,139,250,0.45);
            background: rgba(167,139,250,0.1);
        }
        .pq-opt-letter {
            width: 30px; height: 30px;
            border-radius: 8px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            display: flex; align-items: center; justify-content: center;
            font-size: 0.75rem; font-weight: 700;
            color: #7a8aaa;
            flex-shrink: 0;
            transition: all 0.18s;
        }
        .pq-opt.selected .pq-opt-letter {
            background: rgba(167,139,250,0.2);
            border-color: rgba(167,139,250,0.4);
            color: #a78bfa;
        }
        .pq-opt-text {
            font-size: 0.875rem;
            color: #c0c8d8;
            line-height: 1.45;
            transition: color 0.18s;
        }
        .pq-opt.selected .pq-opt-text { color: #a78bfa; }

        /* ── Practice Results ── */
        .pq-res-hero {
            text-align: center;
            padding: 36px 24px 28px;
            border-bottom: 1px solid rgba(255,255,255,0.07);
        }
        .pq-score-ring {
            width: 100px; height: 100px;
            border-radius: 50%;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            margin: 0 auto 18px;
            border: 3px solid;
            font-family: 'Outfit', sans-serif;
        }
        .pq-score-ring .r-num  { font-size: 1.8rem; font-weight: 800; line-height: 1; }
        .pq-score-ring .r-sub  { font-size: 0.7rem; font-weight: 400; opacity: 0.65; margin-top: 2px; }
        .pq-score-ring.great  { border-color: #06d6a0; color: #06d6a0; background: rgba(6,214,160,0.07); }
        .pq-score-ring.mid    { border-color: #f59e0b; color: #f59e0b; background: rgba(245,158,11,0.07); }
        .pq-score-ring.low    { border-color: #fb4f4f; color: #fb4f4f; background: rgba(251,79,79,0.07); }
        .pq-res-title { font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: #fff; margin-bottom: 6px; }
        .pq-res-msg   { font-size: 0.85rem; color: #7a8aaa; margin-bottom: 18px; }
        .pq-stat-row  { display: flex; justify-content: center; gap: 14px; flex-wrap: wrap; }
        .pq-stat {
            text-align: center;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 10px; padding: 10px 18px; min-width: 80px;
        }
        .pq-stat .sv { font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; }
        .pq-stat .sl { font-size: 0.7rem; color: #7a8aaa; margin-top: 2px; }
        .pq-stat.c .sv { color: #06d6a0; }
        .pq-stat.w .sv { color: #fb4f4f; }

        /* ── Result items ── */
        .pq-res-section { padding: 22px 24px; }
        .pq-res-section-label {
            font-size: 0.7rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.1em;
            color: #7a8aaa; margin-bottom: 14px;
            display: flex; align-items: center; gap: 8px;
        }
        .pq-res-section-label::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.07); }

        .pq-ri {
            background: #141e35;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 12px;
            padding: 16px 18px;
            margin-bottom: 10px;
        }
        .pq-ri.correct   { border-left: 3px solid #06d6a0; }
        .pq-ri.incorrect { border-left: 3px solid #fb4f4f; }

        .pq-ri-header {
            display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
        }
        .pq-ri-badge {
            display: inline-flex; align-items: center; gap: 5px;
            font-size: 0.68rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.06em;
            padding: 2px 8px; border-radius: 100px;
        }
        .pq-ri-badge.c { background: rgba(6,214,160,0.1); color: #06d6a0; border: 1px solid rgba(6,214,160,0.2); }
        .pq-ri-badge.w { background: rgba(251,79,79,0.08); color: #fb4f4f; border: 1px solid rgba(251,79,79,0.2); }
        .pq-ri-qnum { font-size: 0.72rem; color: #7a8aaa; font-family: 'DM Mono', monospace; }

        .pq-ri-q { font-family: 'Outfit', sans-serif; font-size: 0.875rem; font-weight: 600; color: #fff; margin-bottom: 10px; line-height: 1.45; }
        .pq-ri-answers { display: flex; flex-direction: column; gap: 5px; margin-bottom: 8px; }
        .pq-ri-ans {
            display: flex; align-items: flex-start; gap: 8px;
            font-size: 0.8rem; line-height: 1.4;
        }
        .pq-ri-ans-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; min-width: 52px; padding-top: 1px; }
        .pq-ri-ans-label.your    { color: #7a8aaa; }
        .pq-ri-ans-label.correct { color: #06d6a0; }
        .pq-ri-ans-text.wrong    { color: #fb4f4f; }
        .pq-ri-ans-text.right    { color: #06d6a0; }
        .pq-ri-ans-text          { color: #c0c8d8; }

        .pq-ri-explanation {
            display: flex; align-items: flex-start; gap: 7px;
            background: rgba(255,255,255,0.03);
            border-radius: 8px; padding: 9px 12px;
            font-size: 0.78rem; color: #7a8aaa; line-height: 1.5;
        }
        .pq-ri-explanation i { color: #a78bfa; margin-top: 2px; flex-shrink: 0; font-size: 0.72rem; }
    `;
    document.head.appendChild(style);
}

function startPracticeQuiz() {
    practiceAnswers = new Array(practiceQuestions.length).fill(null);
    document.getElementById('practice-quiz-intro').style.display = 'none';
    document.getElementById('practice-quiz-questions').style.display = 'block';
    showPracticeQuestion(0);
}

function showPracticeQuestion(index) {
    currentPracticeQuestion = index;
    var question = practiceQuestions[index];
    var total    = practiceQuestions.length;
    var progress = ((index + 1) / total) * 100;

    document.getElementById('practice-progress').style.width = progress + '%';

    var letters = ['A', 'B', 'C', 'D', 'E'];
    var optionsHTML = question.options.map(function (opt, i) {
        var sel = practiceAnswers[index] === i ? ' selected' : '';
        return '<div class="pq-opt' + sel + '" data-idx="' + i + '">' +
            '<div class="pq-opt-letter">' + letters[i] + '</div>' +
            '<div class="pq-opt-text">' + opt + '</div>' +
            '</div>';
    }).join('');

    var html = '<div class="pq-card">' +
        '<div class="pq-q-header">' +
            '<div class="pq-q-num"><div class="pq-q-num-dot"></div>Question ' + (index + 1) + '</div>' +
            '<div class="pq-q-counter">' + (index + 1) + ' / ' + total + '</div>' +
        '</div>' +
        '<div class="pq-q-text">' + question.question + '</div>' +
        '<div class="pq-options">' + optionsHTML + '</div>' +
    '</div>';

    document.getElementById('practice-question-container').innerHTML = html;

    document.querySelectorAll('.pq-opt').forEach(function (el) {
        el.addEventListener('click', function () {
            practiceAnswers[index] = parseInt(this.dataset.idx);
            document.querySelectorAll('.pq-opt').forEach(function (o) { o.classList.remove('selected'); });
            this.classList.add('selected');
            updatePracticeButtons();
        });
    });

    updatePracticeButtons();
}

function updatePracticeButtons() {
    var total  = practiceQuestions.length;
    var cur    = currentPracticeQuestion;
    var answered = practiceAnswers[cur] !== null;
    var allDone  = practiceAnswers.every(function (a) { return a !== null; });

    document.getElementById('practice-prev-btn').style.display = cur > 0 ? 'inline-flex' : 'none';
    document.getElementById('practice-next-btn').style.display = (cur < total - 1 && answered) ? 'inline-flex' : 'none';
    document.getElementById('practice-submit-btn').style.display = (cur === total - 1 && allDone) ? 'inline-flex' : 'none';
}

function nextPracticeQuestion() {
    if (currentPracticeQuestion < practiceQuestions.length - 1)
        showPracticeQuestion(currentPracticeQuestion + 1);
}

function prevPracticeQuestion() {
    if (currentPracticeQuestion > 0)
        showPracticeQuestion(currentPracticeQuestion - 1);
}

function submitPracticeQuiz() {
    var total   = practiceQuestions.length;
    var score   = 0;
    practiceAnswers.forEach(function (ans, i) {
        if (ans === practiceQuestions[i].correct) score++;
    });
    var pct = Math.round((score / total) * 100);

    var ringClass, title, msg;
    if (pct >= 90)      { ringClass = 'great'; title = 'Excellent! 🎉'; msg = "You've mastered this scam type. Keep staying vigilant!"; }
    else if (pct >= 70) { ringClass = 'great'; title = 'Great Job! ⭐'; msg = "You're well-prepared to spot this scam."; }
    else if (pct >= 50) { ringClass = 'mid';   title = 'Good Effort! 💪'; msg = 'A bit more review will sharpen your awareness.'; }
    else                { ringClass = 'low';   title = 'Keep Studying 📚'; msg = 'Review the information above and try again.'; }

    var heroHTML =
        '<div class="pq-score-ring ' + ringClass + '">' +
            '<span class="r-num">' + pct + '%</span>' +
            '<span class="r-sub">' + score + ' / ' + total + '</span>' +
        '</div>' +
        '<div class="pq-res-title">' + title + '</div>' +
        '<div class="pq-res-msg">' + msg + '</div>' +
        '<div class="pq-stat-row">' +
            '<div class="pq-stat c"><div class="sv">' + score + '</div><div class="sl">Correct</div></div>' +
            '<div class="pq-stat w"><div class="sv">' + (total - score) + '</div><div class="sl">Wrong</div></div>' +
            '<div class="pq-stat"><div class="sv" style="color:#fff;">' + pct + '%</div><div class="sl">Score</div></div>' +
        '</div>';

    var detailsHTML = '<div class="pq-res-section-label">Question Review</div>';
    practiceAnswers.forEach(function (ans, i) {
        var q       = practiceQuestions[i];
        var correct = ans === q.correct;
        var yourAnsText    = q.options[ans];
        var correctAnsText = q.options[q.correct];

        detailsHTML +=
            '<div class="pq-ri ' + (correct ? 'correct' : 'incorrect') + '">' +
                '<div class="pq-ri-header">' +
                    '<span class="pq-ri-badge ' + (correct ? 'c' : 'w') + '">' +
                        '<i class="fas fa-' + (correct ? 'check' : 'times') + '"></i>' +
                        (correct ? 'Correct' : 'Incorrect') +
                    '</span>' +
                    '<span class="pq-ri-qnum">Q' + (i + 1) + '</span>' +
                '</div>' +
                '<div class="pq-ri-q">' + q.question + '</div>' +
                '<div class="pq-ri-answers">' +
                    '<div class="pq-ri-ans">' +
                        '<span class="pq-ri-ans-label your">Your ans:</span>' +
                        '<span class="pq-ri-ans-text ' + (correct ? 'right' : 'wrong') + '">' + yourAnsText + '</span>' +
                    '</div>' +
                    (!correct ?
                        '<div class="pq-ri-ans">' +
                            '<span class="pq-ri-ans-label correct">Correct:</span>' +
                            '<span class="pq-ri-ans-text right">' + correctAnsText + '</span>' +
                        '</div>' : '') +
                '</div>' +
                '<div class="pq-ri-explanation">' +
                    '<i class="fas fa-lightbulb"></i>' +
                    (q.explanation || 'No explanation available.') +
                '</div>' +
            '</div>';
    });

    document.getElementById('practice-quiz-questions').style.display = 'none';
    document.getElementById('practice-quiz-results').style.display = 'block';
    document.getElementById('practice-score-display').innerHTML = heroHTML;
    document.getElementById('practice-results-details').innerHTML =
        '<div class="pq-res-section-label" style="margin-bottom:14px;">Question Review</div>' +
        detailsHTML;
}
