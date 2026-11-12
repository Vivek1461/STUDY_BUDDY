# Study Buddy — Project Overview & Development Plan

> **Document purpose:** Record what the current repository is intended to build, what is visibly implemented, the main engineering gaps, and a safe sequence for completing the product.
> **Repository reviewed:** `E:\desktoppppE\Study_Buddy`
> **Review scope:** Tracked source files, backend configuration, database models, schemas, routers, service modules, dependencies, and frontend directory. Secrets and local environment files were not opened.

---

## 1. Product vision

**Study Buddy is intended to be a personal, document-grounded AI study assistant for students.**

A student should be able to upload their own study material, ask questions about it, and receive explanations and exam-oriented help grounded in those uploaded documents. Rather than behaving like a general-purpose chatbot, the assistant is designed to prioritize the student's notes and clearly say when the uploaded material does not contain the answer.

The intended experience is:

1. A student opens Study Buddy and starts a study session.
2. The student can use a guest session or create an account.
3. The student uploads study files.
4. The backend extracts readable text from the files and splits it into searchable chunks.
5. The chunks are converted into embeddings and stored in a persistent vector database.
6. The student asks a question or selects a study action.
7. Relevant document chunks are retrieved and supplied to the language model as context.
8. The answer is streamed back to the interface.
9. The session, uploaded-file metadata, and chat messages can be persisted and revisited.

### Core value proposition

**Upload your notes. Ask anything about them. Learn the material and prepare for exams with answers grounded in your own documents.**

---

## 2. Intended feature set

### A. Study workspace
- Create and manage study sessions.
- Support guest and authenticated users.
- Associate uploaded files and chat history with a session.
- Give sessions useful labels, such as a subject or document name.
- Allow students to continue a previous session.

### B. Document ingestion
The current upload code indicates intended support for:
- PDF
- DOCX (and a declared legacy DOC format)
- PPTX (and a declared legacy PPT format)
- JPG/JPEG/PNG images using OCR
- TXT

The configured upload limit is 20 MB per file. The upload flow is intended to validate the extension and size, save the file, create a database record, extract its text, index the text, and return processing status and chunk count.

### C. Retrieval-augmented generation (RAG)
The current service design uses:
- Sentence Transformers model: `all-MiniLM-L6-v2` for embeddings.
- ChromaDB for persistent vector storage.
- Recursive text splitting with an intended chunk size of 1,800 characters and overlap of 200.
- Similarity retrieval to find relevant chunks for a student's question.
- Session-specific collections, so study material can be scoped to a study session.

### D. AI study assistant
The current LLM service is configured for:
- Groq API
- Model: `llama-3.1-8b-instant`
- Streaming responses
- A document-context-first system prompt
- A short chat-history window (the last six messages)

Four explicit study modes are described in the service:
- **Teach me:** explain a topic in an approachable way.
- **Key points:** summarize the most important points.
- **Quiz me:** create three MCQs with answers and explanations.
- **Exam tips:** identify exam-relevant facts and topics.

The intended assistant tone is concise, student-friendly, and focused on the uploaded notes.

### E. Accounts and security
The backend contains the beginnings of:
- Email-based user registration.
- Password hashing with bcrypt through Passlib.
- JWT access tokens.
- Optional bearer-token authentication for guest-compatible requests.
- A required-user dependency for protected operations.

---

## 3. What the repository currently contains

| Area | Observed state |
|---|---|
| Backend framework | FastAPI dependencies and Python application modules are present |
| Database layer | SQLAlchemy engine, session factory, and declarative base are present |
| Data models | User, StudySession, UploadFile, and Message models are drafted |
| API routers | Auth, chat, and upload router files exist |
| File parsing | PDF, DOCX, PPTX, image OCR, and TXT parsing logic is drafted |
| RAG | Embedding, chunking, ChromaDB indexing, retrieval, and deletion logic are drafted |
| LLM | Groq client and streaming completion logic are drafted |
| Frontend | The `frontend` directory was empty when inspected; no frontend source files were listed |
| Application entry point | No `main.py` or equivalent FastAPI application entry point appeared in the inspected tracked source list |
| Automated tests | No test files appeared in the inspected tracked source list |
| Dependencies | Backend requirements are pinned; a duplicate root requirements file is present |
| Git | Repository is on `main`, tracking `origin/main`; working tree had existing modifications |

**Important:** The repository shows a clear product direction, but it is not yet a verified, working end-to-end application. Several inspected Python files contain syntax errors, misspelled imports, inconsistent names, and incomplete functions. The feature descriptions above explain the intended architecture, not a claim that every flow currently runs.

---

## 4. Proposed product architecture

```text
Student
  |
  v
Study Buddy Frontend (to be built)
  |  Login / Guest session / Upload / Chat / Study actions
  v
FastAPI Backend
  |
  +--> Authentication service
  |      +--> Password hashing
  |      +--> JWT validation
  |
  +--> Session and chat APIs
  |      +--> SQL database
  |             +--> Users
  |             +--> Study sessions
  |             +--> Uploaded-file metadata
  |             +--> Messages
  |
  +--> Upload and parsing pipeline
  |      +--> PDF / DOCX / PPTX / image OCR / TXT
  |
  +--> RAG service
  |      +--> Text chunking
  |      +--> Sentence Transformer embeddings
  |      +--> ChromaDB persistent vector store
  |      +--> Relevant context retrieval
  |
  +--> LLM service
         +--> Groq API
         +--> Context-grounded prompt
         +--> Streaming answer
```

### Current technology choices observed
- **Backend:** Python, FastAPI, Uvicorn
- **Relational database:** PostgreSQL is indicated by the example database URL; SQLAlchemy is used as the ORM
- **Vector database:** ChromaDB
- **Embeddings:** Sentence Transformers / `all-MiniLM-L6-v2`
- **LLM provider:** Groq
- **Document parsing:** PyMuPDF, python-docx, python-pptx, Pillow, pytesseract
- **Authentication:** JWT and bcrypt password hashing

No frontend framework could be confirmed because the frontend directory contained no files at review time. Choose the frontend stack after confirming the intended UI implementation approach; do not assume a framework is already in place.

---

## 5. Critical engineering findings to resolve first

The following issues were visible in the inspected source. They should be verified and fixed before building more features on top of the current implementation.

### P0 — Application cannot be considered runnable yet
- No FastAPI application entry point was found in the tracked source list. Create an application entry point, register routers, configure CORS, and add health-check endpoints.
- Several modules contain syntax/import/name errors. Run a full compile/import check and fix these before feature work.
- The chat router appears incomplete in the inspected file.
- The auth router file was empty at the time of inspection, even though auth schemas and service helpers exist.
- The service directory is named `sevices` (misspelled), while several imports refer to `app.services`. Standardize the directory name and imports consistently.

### P0 — Data model and database consistency
- The models file contains misspelled or inconsistent SQLAlchemy imports, foreign-key table names, defaults, and server-default declarations.
- The user relationship references should consistently target the actual `users` table.
- Session ownership and guest-session access rules need to be explicit.
- Add and verify database migrations rather than relying on implicit table creation.
- Confirm cascade behavior for deleting a session, its messages, uploaded-file records, and vector index.

### P0 — RAG service correctness
- The inspected RAG module has inconsistent function and variable names, including embedder/client accessors and retrieval/indexing names.
- Correct the chunking, collection naming, collection lookup, and ChromaDB client code.
- Define retrieval filters so a user can only retrieve chunks from files and sessions they are authorized to access.
- Add tests for empty documents, duplicate uploads, deleted files, and sessions with no indexed content.

### P0 — Upload and parser reliability
- The upload router contains malformed imports, annotations, response declarations, and function names.
- Enforce both extension and content validation; extension alone is not sufficient.
- Ensure files cannot be accessed by guessing a stored filename or another user's file ID.
- Make processing status and failures recoverable. Avoid leaving orphaned files or database records after partial failure.
- Confirm OCR dependencies and the Tesseract executable are installed and configured on the target machine.
- Legacy `.doc` and `.ppt` support should not be advertised until the parser actually supports those formats.

### P1 — LLM behavior and reliability
- The current prompt says to use only retrieved context. Preserve that grounding behavior and make the no-context response predictable.
- Handle provider timeouts, rate limits, empty streams, and interrupted client connections.
- Do not expose raw provider exceptions, stack traces, or secrets in user-facing responses.
- Ensure chat history and retrieved context are combined in a consistent order.
- Validate that the selected action mode is supported and that the actual user question is not accidentally discarded when an action is selected.

### P1 — Security and privacy
- Keep real `.env` files, API keys, JWT secrets, uploaded documents, and local vector-store data out of Git.
- Replace development defaults such as `change-me` with required secure configuration in non-development environments.
- Enforce ownership checks for every session, file, and message endpoint.
- Validate file size, MIME type, extension, and generated storage paths.
- Add safe deletion for original files, database records, and vector-store chunks.
- Add rate limiting and request-size controls before public deployment.
- Define retention and deletion behavior for uploaded study material and chat history.

---

## 6. Development roadmap

### Phase 0 — Stabilize and establish a baseline
**Goal:** Make the existing backend importable and runnable before expanding it.

- [ ] Confirm the active Python environment and one canonical dependency file.
- [ ] Standardize the `app/services` package name and all imports.
- [ ] Fix syntax errors and inconsistent names in configuration, database, models, schemas, and services.
- [ ] Create the FastAPI application entry point.
- [ ] Register routers and configure CORS from settings.
- [ ] Add a health endpoint and database connectivity check.
- [ ] Add a minimal startup and shutdown lifecycle.
- [ ] Run compile/import checks and record the exact command used to start the backend.

**Exit criteria:** Backend starts reliably; health endpoint responds; database connection is verified.

### Phase 1 — Database and authentication
**Goal:** Make identity, guest access, and study-session ownership reliable.

- [ ] Finalize User, StudySession, UploadFile, and Message schemas.
- [ ] Add migrations and initialize the database.
- [ ] Implement registration and login endpoints.
- [ ] Validate password length and email format.
- [ ] Implement JWT creation, expiry, and validation.
- [ ] Define guest-session creation and access rules.
- [ ] Add current-user and session-ownership dependencies.
- [ ] Test unauthorized access and cross-user isolation.

**Exit criteria:** A user can register, log in, create a session, and access only their own permitted data.

### Phase 2 — Document upload and processing
**Goal:** Reliably turn supported study files into indexed text.

- [ ] Implement upload endpoint and file validation.
- [ ] Generate safe, unique server-side filenames.
- [ ] Store upload metadata and processing status.
- [ ] Implement PDF, DOCX, PPTX, TXT, and image OCR parsing.
- [ ] Normalize extracted text and retain page/slide references where possible.
- [ ] Split text into chunks with stable metadata.
- [ ] Generate embeddings and persist them in ChromaDB.
- [ ] Return processing status and chunk count.
- [ ] Implement file deletion across disk, database, and vector store.
- [ ] Test malformed, empty, oversized, duplicate, and unsupported files.

**Exit criteria:** A supported file can be uploaded, parsed, indexed, listed, and deleted without orphaned data.

### Phase 3 — Grounded AI chat
**Goal:** Deliver useful answers based on the student's own uploaded material.

- [ ] Implement session-aware context retrieval.
- [ ] Implement chat endpoint and persist user/assistant messages.
- [ ] Connect retrieved chunks to the Groq LLM service.
- [ ] Stream responses to the client using a documented streaming format.
- [ ] Implement Teach, Key Points, Quiz, and Exam Tips actions.
- [ ] Add source references (file name and page/slide/chunk where available).
- [ ] Handle no-context, provider-error, timeout, and interrupted-stream cases.
- [ ] Test retrieval relevance and verify that answers do not claim unsupported citations.

**Exit criteria:** A student can ask questions about an uploaded document and receive a streamed, context-grounded answer.

### Phase 4 — Frontend experience
**Goal:** Build a polished, accessible study workspace that connects to the verified APIs.

The frontend directory was empty during this review. First select and initialize the frontend stack, then implement:

- [ ] Responsive application shell and navigation.
- [ ] Landing / welcome screen.
- [ ] Sign up, login, and guest entry.
- [ ] Dashboard with recent study sessions.
- [ ] New study session flow.
- [ ] Document upload with progress and processing states.
- [ ] Uploaded-file list with status and delete action.
- [ ] Chat workspace with streaming assistant messages.
- [ ] Study action controls: Teach, Key Points, Quiz, Exam Tips.
- [ ] Conversation history and session switching.
- [ ] Empty, loading, error, and retry states.
- [ ] Responsive mobile/tablet layouts and keyboard accessibility.

**Exit criteria:** A student can complete the full study journey from the browser without using API tools manually.

### Phase 5 — Quality, security, and release
**Goal:** Make the application dependable and safe to deploy.

- [ ] Add automated unit and integration tests.
- [ ] Add end-to-end tests for registration, upload, chat, and deletion.
- [ ] Add structured logs without logging secrets or document contents unnecessarily.
- [ ] Add rate limits and upload abuse protection.
- [ ] Verify CORS, authentication, ownership, and deletion behavior.
- [ ] Add database backup and recovery instructions.
- [ ] Document environment variables and local setup.
- [ ] Add production deployment configuration and monitoring.
- [ ] Run a final privacy and security review.

**Exit criteria:** The product can be deployed with documented setup, tested core flows, and known operational limits.

---

## 7. Suggested frontend information architecture

A focused first release should avoid unnecessary complexity.

### Main navigation
1. **Dashboard** — welcome message, recent sessions, start studying.
2. **My Study Sessions** — list and reopen previous sessions.
3. **New Study Session** — upload material and create a session.
4. **Settings** — profile, account, and sign out.

### Main study workspace
- **Header:** session title, uploaded file count, session actions.
- **Left panel:** files in the current session and processing status.
- **Center panel:** conversation history and streamed AI response.
- **Composer:** question input, attachment action, send button.
- **Study action bar:** Teach me, Key points, Quiz me, Exam tips.
- **Answer details:** source document references and relevant page/slide when available.

The interface should make it obvious which documents are being used as context. Include clear states for no documents uploaded, processing, ready, failed, and no relevant answer found.

---

## 8. Definition of done for the first usable release

The first usable version is complete when a student can:

1. Open Study Buddy and enter as a guest or register/log in.
2. Create a study session.
3. Upload at least one supported PDF or DOCX file.
4. See whether the file is processing, ready, or failed.
5. Ask a question about the uploaded content.
6. Receive a streamed answer grounded in retrieved document content.
7. Use all four study modes.
8. See previous messages after reopening the session.
9. Delete an uploaded file and have its indexed content removed.
10. Be prevented from accessing another user's private sessions or files.

---

## 9. Working rules for future development

- Treat this plan as the project baseline; update it when architecture or scope changes.
- Inspect existing files before editing them.
- Make small, reviewable changes and test after each phase.
- Do not rewrite working modules merely for stylistic preference.
- Do not change database schema without documenting the migration.
- Never commit `.env`, API keys, passwords, uploaded documents, or vector database contents.
- Keep the frontend connected to real backend contracts; avoid fake success states.
- Do not claim a feature is complete until its end-to-end behavior has been tested.
- Preserve existing user work and inspect Git status before making changes.

---

## 10. Immediate next actions

1. **Stabilize the backend imports and syntax.** The current source has blockers that should be fixed before UI integration.
2. **Create and verify the FastAPI entry point.** Establish a reliable local backend startup command.
3. **Finalize the database models and auth/session rules.**
4. **Complete and test upload → parsing → chunking → embedding → ChromaDB indexing.**
5. **Complete the session-aware streaming chat endpoint.**
6. **Initialize the frontend and build the study workspace against the verified API.**

**Recommended priority:** Make one complete vertical slice work first — guest session → upload PDF → ask a question → receive a grounded streamed answer. Then expand authentication, history, more formats, and visual polish.
