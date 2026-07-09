# Exam Practice Tool

A self-contained, local exam practice application with two modes:
**Practice Mode** for relaxed study with instant feedback, and **Strict Mode**
for proctored exam simulation with camera, microphone, fullscreen enforcement,
and comprehensive violation monitoring.

No cloud services. No sign-ups. Everything runs on your machine.

---

## Features

| Feature | Practice Mode | Strict Mode |
|---|---|---|
| Instant correct/wrong feedback | Yes | No (revealed at end) |
| Detailed explanations on demand | Yes | No |
| Time limit | None | 1 hour |
| Camera monitoring | No | Yes |
| Microphone / noise detection | No | Yes |
| Fullscreen enforcement | No | Yes |
| Alt+Tab / new tab blocking | No | Yes |
| Keyboard shortcut restriction | No | Yes |
| Right-click disabled | No | Yes |
| Violation logging | No | Yes |
| Previous attempt statistics | Yes | Yes |
| Question & option shuffling | Configurable | Configurable |

---

## Requirements

- **Python 3.8+** (uses only the standard library — no `pip install` needed)
- A modern browser (Chrome, Edge, Firefox, or Safari)
- `exam_data.js` placed in the same folder as `main.py`

---

## Installation Tutorial

### Step 1 — Download the files

Place both files in the same folder:

```
your-folder/
├── main.py
└── exam_data.js
```

### Step 2 — Run the server

Open a terminal (or Command Prompt) in that folder and run:

```bash
python main.py
```

You will see a startup banner in the terminal:

```
  ╔══════════════════════════════════════════════════════════╗
  ║                EXAM PRACTICE TOOL                        ║
  ║                      Server Started                      ║
  ║    URL        : http://localhost:8080                    ║
  ║    exam_data  : Found                                    ║
  ╚══════════════════════════════════════════════════════════╝
```

Your default browser will open automatically to `http://localhost:8080`.

### Step 3 — Choose a mode and start

1. On the landing page, select **Practice Mode** or **Strict Mode**.
2. Click **Start**.
3. For Strict Mode, grant camera and microphone access when prompted,
   then click **Begin Exam** to enter fullscreen.

### Step 4 — Stop the server

Press **Ctrl+C** in the terminal window to shut down the server.

---

## Modifying Exam Data (`exam_data.js`)

### How the Tool Reads Exam Data

When the application starts, `main.py` looks for a file called
`exam_data.js` in the same directory. The browser loads this file via a
`<script src="exam_data.js"></script>` tag in the HTML. The file must
define two global JavaScript objects — `examConfig` (metadata about the
exam) and `examQuestions` (the array of questions). If the file is
missing or malformed, the landing page will display an error.

### Generating `exam_data.js` from Your Study Materials

You do **not** need to write JavaScript by hand. You can use any AI
assistant (ChatGPT, Gemini, Claude, MiMo, etc.) to generate the file
for you. The process is as follows:

**Step 1 — Prepare your source material.**

Gather your study content in any of these formats:
- **PDF files** (textbooks, slides, handouts)
- **Markdown notes** (`.md` files with headings, bullet points, definitions)
- **Plain text** (copy-pasted paragraphs, flashcard-style Q&A)
- **Any combination** of the above

**Step 2 — Use a 5-sentence prompt to generate `exam_data.js`.**

Copy and paste the prompt below into your AI assistant, then append your
notes or PDF content after the last line. Press Enter to generate.

---

> **Prompt (copy this entire block):**
>
> I am building exam questions for a JavaScript-based exam practice tool.
> The file must be named `exam_data.js` and must define two global
> variables: `examConfig` (an object with keys `title`, `subtitle`,
> `description`, `passingScore`, `shuffleQuestions`, and
> `shuffleOptions`) and `examQuestions` (an array of question objects,
> each having `id`, `type` (`"multiple-choice"` or `"exact-word"`),
> `question`, `options` (array, for multiple-choice only), `correctAnswer`
> (string matching one option or the expected exact word), `explanation`
> (string), and optionally `caseSensitive` for exact-word questions).
> Generate at least 20 questions from the study material I provide below,
> covering the key topics thoroughly. Mix multiple-choice and exact-word
> question types. Each explanation should be 1-3 sentences teaching why
> the answer is correct. Output ONLY the raw JavaScript code inside a
> single code block — no markdown fences, no extra commentary.
>
> **Study material follows:**
>
> *(paste your notes, markdown content, or extracted PDF text here) and must be generated with exam_data.js file as example*

---

**Step 3 — Save the output.**

The AI will return something that looks like this:

```javascript
var examConfig = {
  title: "DP-800 SQL AI Engineer",
  subtitle: "Azure Data Fundamentals",
  description: "Practice questions covering Azure Synapse, Delta Lake, T-SQL, and data engineering concepts.",
  passingScore: 70,
  shuffleQuestions: true,
  shuffleOptions: true
};

var examQuestions = [
  {
    id: 1,
    type: "multiple-choice",
    question: "Which columnar file format is recommended by Microsoft for optimal query performance in Azure Synapse Analytics dedicated SQL pools?",
    options: ["CSV", "Apache Parquet", "Apache Avro", "JSON"],
    correctAnswer: "Apache Parquet",
    explanation: "Apache Parquet is a columnar storage format optimized for analytical queries. Azure Synapse dedicated SQL pools use PolyBase and CETAS which natively support Parquet for the best query performance and compression."
  },
  {
    id: 2,
    type: "exact-word",
    question: "What T-SQL clause is used to filter rows after GROUP BY aggregation?",
    correctAnswer: "HAVING",
    caseSensitive: false,
    explanation: "The HAVING clause filters groups after aggregation, unlike WHERE which filters individual rows before grouping."
  },
  {
    id: 3,
    type: "multiple-choice",
    question: "In Azure Databricks, what critical capability does Delta Lake add on top of standard Parquet file storage?",
    options: ["Row-level encryption", "ACID transactions and time travel", "Native JSON support", "Built-in machine learning"],
    correctAnswer: "ACID transactions and time travel",
    explanation: "Delta Lake adds ACID transaction support, schema enforcement, and time travel (versioning) on top of Parquet, enabling reliable data lake architectures."
  }
];
```

**Step 4 — Save as `exam_data.js`.**

Copy the entire output into a file named exactly `exam_data.js` and place
it in the same folder as `main.py`. Then restart the server:

```bash
python main.py
```

### `exam_config` Reference

| Key | Type | Description |
|---|---|---|
| `title` | string | Exam title shown on the landing page |
| `subtitle` | string | Subtitle shown below the title |
| `description` | string | Description paragraph shown on landing |
| `passingScore` | number | Minimum percentage to pass (e.g., `70`) |
| `shuffleQuestions` | boolean | Randomize question order each attempt |
| `shuffleOptions` | boolean | Randomize answer option order for MC questions |

### `examQuestions` Reference

| Key | Type | Required | Description |
|---|---|---|---|
| `id` | number | Yes | Unique identifier for the question |
| `type` | string | Yes | `"multiple-choice"` or `"exact-word"` |
| `question` | string | Yes | The question text displayed to the user |
| `options` | array | MC only | Array of answer option strings |
| `correctAnswer` | string | Yes | The correct answer (must match an option for MC) |
| `explanation` | string | Yes | Explanation shown after answering |
| `caseSensitive` | boolean | No | For exact-word: whether matching is case-sensitive (default `false`) |

### Using Multiple Exam Files

You can keep multiple exam data files in the same folder:

```
your-folder/
├── main.py
├── exam_data.js            ← active (loaded by the tool)
├── exam_data_python.js     ← backup
├── exam_data_azure.js      ← backup
└── exam_data_networking.js ← backup
```

To switch exams, rename the desired file to `exam_data.js` and restart
the server.

---

## Switching Between Light and Dark Theme

Click the sun/moon icon in the top-right corner of the header. Your
preference is saved in the browser's local storage and persists across
sessions.

---

## How Strict Mode Monitoring Works

When you select Strict Mode and click **Begin Exam**, the tool:

1. **Requests camera and microphone access** — verified in the
   environment check overlay before the exam starts.
2. **Activates fullscreen** — the browser enters kiosk-style fullscreen.
   Exiting triggers an immediate violation and a "Re-enter Fullscreen"
   prompt.
3. **Monitors focus** — `visibilitychange`, `blur`, and a periodic
   500ms `document.hasFocus()` check catch Alt+Tab, new tab creation,
   and OS-level application switching.
4. **Blocks dangerous keyboard shortcuts** — Alt+*, Ctrl+T/N/W/L/H/J,
   Ctrl+Shift+*, F1-F12, Escape, PrintScreen, and Meta/Windows key are
   intercepted and logged as violations.
5. **Disables right-click and middle-click** — context menus and
   middle-button actions are blocked with violation logging.
6. **Detects sustained noise** — microphone audio levels are analyzed
   via Web Audio API. Sustained sound above threshold for 1.5+ seconds
   triggers a noise violation.
7. **Enforces a 1-hour time limit** — the exam auto-submits when time
   expires, with unanswered questions marked incorrect.

All violations appear in the **Security Log** panel (bottom-left during
the exam) and in the **Violations** count on the results page.

---

## Tested Environments

| OS | Browser | Status |
|---|---|---|
| Windows 10/11 | Chrome, Edge, Firefox | Verified |
| Ubuntu 22+ | Chrome, Firefox | Verified |
| macOS 14+ | Safari, Chrome | Verified |

---

## License

For exam preparation purposes only.
