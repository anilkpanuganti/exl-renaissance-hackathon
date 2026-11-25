# GenAI-Assisted Legacy ETL Modernization Framework

### A Snowflake-Based Approach to Cloud-Native Data Platform Migration

**Organization:** EXL Pvt. Ltd., Gurgaon, Haryana, India
**Project Type:** Work-related Hackathon / PoC Project
**Project Area:** AI-Assisted Cloud Data Engineering (Enterprise Data Warehouse & ETL Modernization)

---

## 1. What This Project Is

Legacy ETL and data warehouse systems accumulate technical debt, undocumented business
rules, and complex dependencies over years of development. Modernizing them to
cloud-native platforms like **Snowflake** is traditionally a slow, manual, expert-dependent
process.

This project proposes and demonstrates a **Generative AI-Assisted Modernization
Framework** that supports the *entire* modernization lifecycle — not just code
conversion — including legacy code analysis, business rule extraction, migration
recommendations, dbt/Snowflake transformation, validation, and documentation generation.

## 2. Repository Structure & Branch Strategy

This repository follows a **two-branch model** during the hackathon phase:

| Branch | Contents | Purpose |
|---|---|---|
| `main` | Approved project outline, references, glossary, licensing, repo governance | The stable, "official" record of the project — what would be submitted/reviewed |
| `feature/genai-poc-framework` | Full framework docs + working proof-of-concept prototype code | Active development branch where the PoC, architecture docs, and evaluation artifacts are built and iterated on before merging back |

The feature branch will be merged into `main` via pull request once the PoC and
supporting documentation are reviewed and finalized.

## 3. Documentation Index (this branch)

| Document | Description |
|---|---|
| [`docs/project-outline-source.md`](docs/project-outline-source.md) | Full original project outline (background, problem statement, objectives, scope, methodology, plan of work, resources, risks, expected benefits) |
| [`docs/references.md`](docs/references.md) | Indicative APA references |
| [`docs/glossary.md`](docs/glossary.md) | Key terminology |

> Architecture diagrams, the working PoC, evaluation rubric, prompt-engineering
> approach, and competitive landscape analysis live on
> **[`feature/genai-poc-framework`](../../tree/feature/genai-poc-framework)**
> until they're reviewed and merged.

## 4. Project Objectives (Summary)

1. Analyze legacy ETL challenges (dependencies, technical debt, undocumented logic)
2. Study Snowflake's cloud-native capabilities as the modernization target
3. Design a GenAI-assisted modernization framework spanning the full lifecycle
4. Build a conceptual proof-of-concept (SQL interpretation → dbt/Snowflake transformation → validation → documentation)
5. Evaluate the framework's expected business benefits

## 5. Status

🚧 **Active hackathon build** — see the feature branch for current progress on the
proof-of-concept and supporting technical documentation.

## 6. License

See [`LICENSE`](LICENSE).

## Prompt

You are a senior desktop-app engineer. Build "AnswerEval AI", a Windows desktop app that helps a professor evaluate handwritten student answer sheets using AI. I attached a screenshot of 10 UI screens. Match its look: dark navy sidebar, blue primary buttons, cards, tables and a step wizard.

# 1. Purpose

The professor uploads (a) a student answer sheet, (b) a question paper and (c) a model answer/marking scheme. Any of them may be handwritten or scanned PDFs or photos. The AI extracts text, evaluates each answer and RECOMMENDS marks with feedback. The professor reviews, edits and finalizes the marks, then exports a PDF or Excel report. She can later look up any student by ID.

# 2. Non-negotiable constraints

- NO database. Store everything as files (JSON, plus copies of the PDFs and page images) in a local folder (default: Documents/AnswerEvalAI/).

- Ship ONE Windows installer (.exe) that needs no Node, Python or other installs. It must work offline except for the AI API calls.

- Stack: Electron + React + TypeScript + Vite + Tailwind. Package with electron-builder (NSIS). Use pdf.js for PDF rendering and pdf-lib/pdfkit for reports.

- The professor has only FREE AI keys. The app must work well on free tiers. This is the most important design driver.

- The professor enters her own API key in Settings. Encrypt it with Electron safeStorage. Never log it and never hardcode it.

# 3. Free-tier-first AI design

Free keys have tight limits (a few to ~15 requests per minute, daily caps, small context, sometimes no vision). Design for that:

Provider adapter interface with these providers:

- Google Gemini (default; free tier via AI Studio, supports vision)

- Groq (free tier, fast; vision-capable Llama models where available, otherwise text-only)

- OpenRouter (free ":free" models)

- Mistral (free tier)

- OpenAI and Anthropic (for any paid key she might get later)

- "Custom OpenAI-compatible endpoint" (base URL + model + key)

Each provider has a capability flag: supportsVision, maxImagesPerRequest, requestsPerMinute, dailyLimit, contextWindow. Show these in Settings with a "Test connection" button that also tests vision support.

Two-stage pipeline, so that text-only free models can still do the grading:

- Stage A, Vision/OCR (needs a vision model): handwritten page image -> structured text per question. Run it ONCE per document and cache the result on disk.

- Stage B, Evaluation (TEXT only): compare extracted student text with the model answer and marking points. This works on any free text model.

- Let the user pick a different provider/model for each stage (for example Gemini for OCR and Groq for grading).

- Fallback: if no vision model is available, let the professor type or paste text (or use a manual-entry mode) for any page.

Free-tier survival features (all required):

- A central request queue with a per-provider rate limiter (token bucket) that respects RPM and a daily cap.

- Exponential backoff with jitter on HTTP 429 and 5xx. Read the Retry-After header. Show a "waiting for rate limit, resuming in 42s" message.

- Page images: JPEG, about 110-150 DPI, grayscale or compressed, long edge up to 1600px. Offer a Low/Medium/High quality setting. Send only the pages needed.

- Batch several questions per evaluation call when they fit the context window, with an automatic fallback to one question per call.

- Persistent job queue on disk: if the app is closed, the quota runs out or the network drops, "Resume" continues exactly where it stopped. Never re-bill or re-process completed pages or questions.

- A usage estimator before starting ("~24 requests, about 6 minutes on your free limit") and a daily-usage counter.

- Aggressive caching: key = hash(image + prompt + model).

- Strict JSON output with zod validation and ONE automatic repair retry. If a model ignores JSON mode, extract the JSON from the text.

- Low confidence (<0.6) automatically sets the status to "Needs Review". Never exceed max marks.

- Always label AI output "Recommended"; the professor has the final say.

# 4. Screens

Follow my screenshot for steps 1-10, with these changes and additions:

1. Login/Welcome: a local profile (name, optional PIN) stored in a file. No online account.

2. Dashboard: stat cards, Start New Evaluation, recent evaluations, and a global search box for student ID.

3. Upload Answer Sheet: drag and drop PDFs or photos (JPG/PNG), multiple files, page preview, reorder/rotate/delete pages.

4. Question Paper and Model Answer setup: upload (handwritten OK) OR enter manually. AI extracts questions, max marks, type (Theory/Numerical/Mixed) and marking points into an editable table. Save an "exam template" so the setup is reused for every student in the same exam.

5. Processing: live step list, progress bar, cancel, resume, rate-limit status, and requests used/remaining.

6. Results Summary: question-wise table, total, and Edit All Marks / Generate Report.

7. Question Detail: previous/next, a side-by-side view of the original image and the editable extracted text, and the model answer.

8. AI Evaluation and Feedback: per-criterion marks breakdown, what is correct, what is missing, a confidence score, and a "Re-evaluate this question" button.

9. Edit Marks and Finalize: AI marks vs final marks (audit trail), comments, Save.

10. Report: PDF (student report) and Excel (class sheet), with an "Open folder" button.

New screens:

- Student Results: search by ID or name, a history of exams per student, open/edit/re-export.

- Exams/Batch: bulk upload of many students, a class table, average/highest/lowest, a marks distribution chart, a Needs Review filter and a "Process all (queued)" button that respects the free limits.

- Settings: provider/model/key per stage, rate-limit values (editable), data folder (change, open, ZIP backup/restore), grading strictness (lenient/standard/strict), half-marks on/off, handwriting/language hints, dark mode.

- A privacy notice: student pages are sent to the chosen AI provider, and free-tier providers may use data for training. Show this once and keep it in Settings.

# 5. File storage layout (atomic writes: temp file, then rename; versioned schemas)

AnswerEvalAI/

  config.json (no keys)

  secrets.bin (safeStorage-encrypted)

  exams/<examId>/exam.json, source/question_paper.pdf, source/model_answer.pdf

  exams/<examId>/students/<studentId>/

    submission.pdf, pages/*.jpg, extraction.json, evaluation.json, final.json, report.pdf, jobs.json

  index/students.json (a search index, rebuilt by scanning folders if missing)

Provide the JSON schemas.

# 6. Prompts

Write and include the exact system and user prompt templates for: (a) question paper extraction, (b) model answer/marking point extraction, (c) handwritten answer extraction mapped to question numbers (handle answers spanning pages, skipped questions, crossed-out text, tables, diagrams and numerical working; mark unreadable text as [illegible] rather than guessing), and (d) evaluation. Keep the prompts short to save tokens, and include strictness and half-marks parameters.

# 7. Quality

- Clear errors (invalid key, quota exhausted, unreadable scan, model has no vision) with the next action suggested.

- Unit tests for the rate limiter, the JSON validation/repair, the file store and the resume logic.

- A mock AI provider for offline demo and testing.

- Keyboard shortcuts (next/previous question, save).

# 8. How to work

Work in phases; after each phase list the files created and WAIT for me to say "next". Give complete code, not snippets.

Phase 1: architecture, folder structure, schemas, the provider interface with capability flags, the prompts.

Phase 2: the Electron main process, file store, settings, key encryption and the job queue.

Phase 3: the AI pipeline (PDF rendering, rate limiter, extraction, evaluation, caching, resume).

Phase 4: the React shell and screens 1-6, plus Student Results and Exams.

Phase 5: screens 7-10, report generation (PDF/Excel) and charts.

Phase 6: electron-builder config, build commands for the .exe, a test checklist and a one-page professor guide on getting a free Gemini key and entering it.

Start with Phase 1.
 
