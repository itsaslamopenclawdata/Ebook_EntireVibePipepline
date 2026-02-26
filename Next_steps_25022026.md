# Next Steps - Vibe PDF Book Generation Platform

**Date:** February 25, 2026
**Repository:** https://github.com/itsaslamopenclawdata/Ebook_EntireVibePipepline
**Project Status:** Foundation Complete, Core Implementation Gaps Identified
**Goal:** Transform from testing/documentation phase to fully functional production application

---

## 📊 IMPLEMENTATION STATUS UPDATE - February 26, 2026

### ✅ COMPLETED TASKS (via 4 parallel subagents):

**Phase 1-5 Progress:**
- ✅ Backend Core: config, database, security modules
- ✅ Backend Models: User model with full schema
- ✅ Backend Routers: auth, users, ebooks, progress, reviews (5 routers)
- ✅ Backend Services: recommendations, sentiment, nlp_query, cache (4 services)
- ✅ Frontend: landing page, auth (login/register/reset), dashboard, reader, library
- ✅ Infrastructure: K8s manifests, Dockerfiles, namespace
- ✅ CI/CD: GitHub workflows (ci-cd.yaml, security.yaml)
- ✅ Tests: unit tests, integration tests, conftest, logging middleware
- ✅ All code pushed to GitHub

**Files Created:** 240+
**GitHub URL:** https://github.com/itsaslamopenclawdata/Ebook_EntireVibePipepline

---

### Remaining Tasks (Not Covered by Subagents):
- Database migrations and schema setup (Partially done - need alembic migrations run)
- Production deployment execution (Still needs to be done)
- Final integration testing

---

## Executive Summary

The Vibe PDF Book Generation Platform is an ambitious AI-powered web application designed to generate professional PDF books from simple user inputs. The project has completed **extensive testing infrastructure** with 100+ test files, 500+ tests, and comprehensive documentation. However, **critical implementation gaps** prevent the application from being functional.

### Current State Assessment

| Component | Status | Completion | Notes |
|-----------|--------|------------|-------|
| Testing Infrastructure | ✅ Complete | 95% | Excellent test coverage, Playwright E2E, Vitest unit tests |
| Documentation | ✅ Complete | 100% | Comprehensive guides, API docs, architecture docs |
| Frontend UI Code | ⚠️ Partial | 80% | UI components built, API integration incomplete |
| Backend API Endpoints | ❌ Critical Gap | 30% | Most endpoints are 501 NOT_IMPLEMENTED placeholders |
| AI Agents (LangGraph) | ✅ Ready | 95% | Outline, Content, Infographic, PDF agents implemented |
| MCP Integrations | ❌ Critical Gap | 40% | Google Drive, PDF manipulation incomplete |
| Database Migrations | ❌ Critical Gap | 0% | Not yet generated/applied |
| Authentication | ❌ Blocked | 70% | Import error blocking authentication service |
| Deployment | ❌ Not Started | 10% | No production configuration |

### Critical Blockers

1. **Book API endpoints return 501 NOT_IMPLEMENTED** - No CRUD operations work
2. **Import error in Auth Service** - `GoogleDriveStorageError` missing
3. **Missing Python dependencies** - anthropic, pypdf, pytest-cov, pytest-mock
4. **No database migrations** - Schema not deployed
5. **Generation API incomplete** - Celery tasks not wired to API

---

## Implementation Roadmap

### Phase 1: Critical Infrastructure Fixes (Days 1-2)

**Objective:** Remove all blockers preventing the application from running

#### 1.1 Fix Auth Service Import Error

**Priority:** 🔴 CRITICAL
**File:** `Backend/app/services/__init__.py`
**Estimated Time:** 30 minutes

**Issue:**
```python
ImportError: cannot import name 'GoogleDriveStorageError' from 'app.services.storage.google_drive'
```

**Action Steps:**
```python
# Add to Backend/app/services/storage/google_drive.py
class GoogleDriveStorageError(Exception):
    """Raised when Google Drive storage operations fail."""
    pass

# Update Backend/app/services/__init__.py
from app.services.storage.google_drive import GoogleDriveStorageError
```

**Verification:**
```bash
cd Backend
python -c "from app.services import AuthService"
# Should not raise ImportError
```

---

#### 1.2 Install Missing Python Dependencies

**Priority:** 🔴 CRITICAL
**File:** `Backend/requirements.txt`
**Estimated Time:** 15 minutes

**Missing Packages:**
```
anthropic>=0.18.0
pypdf>=3.17.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
```

**Action Steps:**
```bash
cd Backend
pip install anthropic pypdf pytest-cov pytest-mock
pip freeze > requirements.txt
```

**Verification:**
```bash
python -c "import anthropic, pypdf, pytest_cov, pytest_mock"
# Should not raise ImportError
```

---

#### 1.3 Generate and Apply Database Migrations

**Priority:** 🔴 CRITICAL
**Directory:** `Backend/alembic/versions/`
**Estimated Time:** 1 hour

**Action Steps:**
```bash
# Set up environment
cd Backend
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/vibepdf"

# Generate migration
alembic revision --autogenerate -m "Initial schema"

# Review generated migration
cat alembic/versions/*_initial_schema.py

# Apply migration
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"

# Test rollback
alembic downgrade -1
alembic upgrade head
```

**Expected Tables:**
- users
- books
- chapters
- generation_tasks
- refresh_tokens

**Verification:**
```bash
pytest tests/test_db_models.py -v
# All model tests should pass
```

---

#### 1.4 Implement Book API Endpoints

**Priority:** 🔴 CRITICAL
**File:** `Backend/app/api/v1/books.py`
**Estimated Time:** 3 hours

**Current State:** All endpoints return `501 NOT_IMPLEMENTED`

**Required Endpoints:**

##### GET /api/v1/books
```python
@router.get("/", response_model=BookListResponse)
async def list_books(
    skip: int = 0,
    limit: int = 20,
    status: Optional[BookStatus] = None,
    current_user: User = Depends(get_current_user),
):
    """List user's books with pagination and filtering."""
    books = await book_service.list_books(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )
    total = await book_service.count_books(current_user.id, status)
    return BookListResponse(items=books, total=total, skip=skip, limit=limit)
```

##### POST /api/v1/books
```python
@router.post("/", response_model=BookResponse)
async def create_book(
    book_data: BookCreateRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a new book."""
    book = await book_service.create_book(
        user_id=current_user.id,
        **book_data.dict()
    )
    return book
```

##### GET /api/v1/books/{book_id}
```python
@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Get book details."""
    book = await book_service.get_book(book_id)
    if book.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
    return book
```

##### PUT /api/v1/books/{book_id}
```python
@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: UUID,
    book_data: BookUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    """Update book details."""
    book = await book_service.get_book(book_id)
    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    updated_book = await book_service.update_book(
        book_id,
        **book_data.dict(exclude_unset=True)
    )
    return updated_book
```

##### DELETE /api/v1/books/{book_id}
```python
@router.delete("/{book_id}")
async def delete_book(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Delete a book."""
    book = await book_service.get_book(book_id)
    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await book_service.delete_book(book_id)
    return {"message": "Book deleted successfully"}
```

##### GET /api/v1/books/{book_id}/chapters
```python
@router.get("/{book_id}/chapters", response_model=List[ChapterResponse])
async def list_chapters(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """List all chapters for a book."""
    book = await book_service.get_book(book_id)
    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    chapters = await book_service.list_chapters(book_id)
    return chapters
```

**Verification:**
```bash
# Test all endpoints
pytest tests/test_api_books.py -v

# Manual testing
curl http://localhost:8000/api/v1/books \
  -H "Authorization: Bearer $TOKEN"
```

---

#### 1.5 Test Authentication Flow End-to-End

**Priority:** 🔴 CRITICAL
**Estimated Time:** 1 hour

**Test Flow:**
```bash
# 1. Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","name":"Test User"}'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  | jq -r '.access_token' > /tmp/token

# 3. Verify token works
TOKEN=$(cat /tmp/token)
curl http://localhost:8000/api/v1/books \
  -H "Authorization: Bearer $TOKEN"

# 4. Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'

# 5. Logout
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Results:**
- Registration creates user in database
- Login returns JWT access token
- Protected endpoints return data with valid token
- Token refresh works
- Logout invalidates token

---

### Phase 2: Core Feature Implementation (Days 3-5)

#### 2.1 Implement Generation API Endpoints

**Priority:** 🟠 HIGH
**File:** `Backend/app/api/v1/generation.py`
**Estimated Time:** 4 hours

**Required Endpoints:**

##### POST /api/v1/generation/start
```python
@router.post("/start", response_model=GenerationStartResponse)
async def start_generation(
    request: GenerationStartRequest,
    current_user: User = Depends(get_current_user),
    celery_app: Celery = Depends(get_celery_app),
):
    """Start book generation process."""
    # Create book record
    book = await book_service.create_book(
        user_id=current_user.id,
        title=request.title,
        input_method=request.input_method,
        topic=request.topic,
        outline=request.outline,
        sheet_url=request.sheet_url,
        status=BookStatus.GENERATING
    )

    # Start Celery task
    task = generate_book_task.delay(
        book_id=str(book.id),
        user_id=str(current_user.id),
        **request.dict()
    )

    # Update generation task record
    await generation_service.create_task(
        book_id=book.id,
        celery_task_id=task.id,
        status=GenerationTaskStatus.PENDING
    )

    return GenerationStartResponse(
        book_id=book.id,
        task_id=task.id,
        status="started"
    )
```

##### GET /api/v1/generation/progress/{book_id}
```python
@router.get("/progress/{book_id}", response_model=GenerationProgressResponse)
async def get_progress(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Get generation progress."""
    book = await book_service.get_book(book_id)
    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = await generation_service.get_task(book_id)
    return GenerationProgressResponse(
        book_id=book_id,
        progress=book.progress,
        current_step=book.current_step,
        status=task.status,
        result=task.result,
        error=task.error,
        started_at=task.started_at,
        completed_at=task.completed_at
    )
```

##### POST /api/v1/generation/cancel/{book_id}
```python
@router.post("/cancel/{book_id}")
async def cancel_generation(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    celery_app: Celery = Depends(get_celery_app),
):
    """Cancel book generation."""
    book = await book_service.get_book(book_id)
    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = await generation_service.get_task(book_id)
    if task.celery_task_id:
        celery_app.control.revoke(task.celery_task_id, terminate=True)

    await book_service.update_book(
        book_id,
        status=BookStatus.CANCELLED
    )

    return {"message": "Generation cancelled"}
```

##### POST /api/v1/generation/retry/{book_id}
```python
@router.post("/retry/{book_id}", response_model=GenerationStartResponse)
async def retry_generation(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    celery_app: Celery = Depends(get_celery_app),
):
    """Retry failed book generation."""
    book = await book_service.get_book(book_id)
    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if book.status != BookStatus.FAILED:
        raise HTTPException(
            status_code=400,
            detail="Can only retry failed generations"
        )

    # Restart Celery task
    task = generate_book_task.delay(
        book_id=str(book.id),
        user_id=str(current_user.id)
    )

    await generation_service.update_task(
        book_id,
        celery_task_id=task.id,
        status=GenerationTaskStatus.PENDING,
        error=None
    )

    await book_service.update_book(
        book_id,
        status=BookStatus.GENERATING
    )

    return GenerationStartResponse(
        book_id=book_id,
        task_id=task.id,
        status="restarted"
    )
```

**Verification:**
```bash
# Test generation flow
pytest tests/test_api_generation.py -v

# Manual test
TOKEN=$(cat /tmp/token)
curl -X POST http://localhost:8000/api/v1/generation/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Test Book",
    "input_method":"single_line",
    "topic":"Artificial Intelligence"
  }'

# Poll progress
BOOK_ID="<from response>"
curl http://localhost:8000/api/v1/generation/progress/$BOOK_ID \
  -H "Authorization: Bearer $TOKEN"
```

---

#### 2.2 Implement Celery Background Tasks

**Priority:** 🟠 HIGH
**File:** `Backend/app/tasks/generation_tasks.py`
**Estimated Time:** 6 hours

**Task Implementation:**

```python
from app.tasks.celery_app import celery_app
from app.agents.graph import generation_graph
from app.services.book_service import BookService
from app.services.generation_service import GenerationService
from app.core.logging import logger

@celery_app.task(bind=True, name="generate_book_task")
def generate_book_task(self, book_id: str, user_id: str, **kwargs):
    """Main book generation task."""
    try:
        # Update status to running
        update_task_status(book_id, GenerationTaskStatus.RUNNING)
        update_book_progress(book_id, 5, "Initializing generation")

        # Run LangGraph generation pipeline
        result = generation_graph.invoke({
            "book_id": book_id,
            "user_id": user_id,
            **kwargs
        })

        # Update book with final status
        update_book_progress(book_id, 100, "Generation complete")
        update_task_status(book_id, GenerationTaskStatus.COMPLETED, result=result)

        return {"status": "completed", "book_id": book_id}

    except Exception as e:
        logger.error(f"Generation failed for book {book_id}: {str(e)}")
        update_task_status(book_id, GenerationTaskStatus.FAILED, error=str(e))
        update_book_status(book_id, BookStatus.FAILED)
        self.retry(exc=e, countdown=60, max_retries=3)

def update_task_status(book_id: str, status: str, result=None, error=None):
    """Update generation task status."""
    generation_service = GenerationService()
    from app.db.session import get_db
    import asyncio

    async def _update():
        db = next(get_db())
        await generation_service.update_task(
            UUID(book_id),
            status=status,
            result=result,
            error=error
        )
        db.close()

    asyncio.run(_update())

def update_book_progress(book_id: str, progress: int, current_step: str):
    """Update book progress."""
    book_service = BookService()
    from app.db.session import get_db
    import asyncio

    async def _update():
        db = next(get_db())
        await book_service.update_book(
            UUID(book_id),
            progress=progress,
            current_step=current_step
        )
        db.close()

    asyncio.run(_update())

def update_book_status(book_id: str, status: BookStatus):
    """Update book status."""
    book_service = BookService()
    from app.db.session import get_db
    import asyncio

    async def _update():
        db = next(get_db())
        await book_service.update_book(UUID(book_id), status=status)
        db.close()

    asyncio.run(_update())
```

**Celery Queues Configuration:**

```python
# Backend/app/tasks/celery_app.py
from celery import Celery

celery_app = Celery(
    "vibe_pdf",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_routes={
        "generate_book_task": {"queue": "generation"},
        "generate_infographic": {"queue": "image_gen"},
        "compile_pdf": {"queue": "pdf_compile"},
        "upload_to_drive": {"queue": "drive_upload"},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
```

**Verification:**
```bash
# Start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# Start Flower for monitoring
celery -A app.tasks.celery_app flower --port=5555

# Monitor: http://localhost:5555

# Test task execution
python -c "
from app.tasks.generation_tasks import generate_book_task
task = generate_book_task.delay('test-book-id', 'test-user-id')
print(f'Task ID: {task.id}')
"
```

---

#### 2.3 Complete MCP Server Integrations

**Priority:** 🟠 HIGH
**Directory:** `Backend/app/integrations/mcp/`
**Estimated Time:** 8 hours

**Required MCP Servers:**

##### Google Drive MCP
```python
# Backend/app/integrations/mcp/google_drive_mcp.py
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from typing import Optional
import os

class GoogleDriveMCP:
    """Google Drive integration for file storage and sharing."""

    def __init__(self):
        self.credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        self.folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        self.service = self._build_service()

    def _build_service(self):
        credentials = Credentials.from_authorized_user_file(self.credentials_path)
        return build("drive", "v3", credentials=credentials)

    async def upload_file(
        self,
        file_path: str,
        filename: str,
        mime_type: str = "application/pdf"
    ) -> dict:
        """Upload file to Google Drive."""
        file_metadata = {
            "name": filename,
            "parents": [self.folder_id]
        }

        media = MediaFileUpload(file_path, mimetype=mime_type)

        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        return {"file_id": file.get("id"), "filename": filename}

    async def get_share_link(self, file_id: str) -> str:
        """Get shareable link for file."""
        self.service.permissions().create(
            fileId=file_id,
            body={"role": "reader", "type": "anyone"}
        ).execute()

        file = self.service.files().get(
            fileId=file_id,
            fields="webViewLink"
        ).execute()

        return file.get("webViewLink")

    async def delete_file(self, file_id: str) -> bool:
        """Delete file from Drive."""
        self.service.files().delete(fileId=file_id).execute()
        return True
```

##### PDF Manipulation MCP
```python
# Backend/app/integrations/mcp/pdf_manipulation_mcp.py
import PyPDF2
import fitz  # PyMuPDF
from typing import List, Optional

class PDFManipulationMCP:
    """PDF manipulation operations."""

    async def merge_pdfs(self, pdf_paths: List[str], output_path: str) -> str:
        """Merge multiple PDFs into one."""
        merger = PyPDF2.PdfMerger()

        for pdf_path in pdf_paths:
            merger.append(pdf_path)

        merger.write(output_path)
        merger.close()

        return output_path

    async def compress_pdf(self, pdf_path: str, output_path: str, quality: int = 75) -> str:
        """Compress PDF by reducing image quality."""
        doc = fitz.open(pdf_path)
        doc.save(output_path, deflate=True, clean=True)
        doc.close()

        return output_path

    async def add_page_numbers(
        self,
        pdf_path: str,
        output_path: str,
        position: str = "bottom_right",
        format: str = "{page}/{total}"
    ) -> str:
        """Add page numbers to PDF."""
        doc = fitz.open(pdf_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = format.format(page=page_num + 1, total=len(doc))

            # Position based on choice
            if position == "bottom_right":
                rect = fitz.Rect(page.width - 100, page.height - 30, page.width, page.height)
            elif position == "bottom_center":
                rect = fitz.Rect(page.width / 2 - 50, page.height - 30, page.width / 2 + 50, page.height)

            page.insert_text(
                rect.bottom_left,
                text,
                fontsize=10,
                color=(0, 0, 0)
            )

        doc.save(output_path)
        doc.close()

        return output_path

    async def split_pdf(self, pdf_path: str, page_ranges: List[tuple], output_dir: str) -> List[str]:
        """Split PDF into multiple files based on page ranges."""
        doc = fitz.open(pdf_path)
        output_paths = []

        for i, (start, end) in enumerate(page_ranges):
            new_doc = fitz.open()
            for page_num in range(start - 1, end):
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

            output_path = f"{output_dir}/split_{i+1}.pdf"
            new_doc.save(output_path)
            new_doc.close()
            output_paths.append(output_path)

        doc.close()
        return output_paths

    async def add_watermark(
        self,
        pdf_path: str,
        output_path: str,
        watermark_text: str,
        opacity: float = 0.3
    ) -> str:
        """Add watermark to all pages."""
        doc = fitz.open(pdf_path)

        for page in doc:
            # Create watermark text
            rect = fitz.Rect(0, 0, page.width, page.height)
            page.insert_text(
                (page.width / 2, page.height / 2),
                watermark_text,
                fontsize=50,
                color=(0.5, 0.5, 0.5),
                opacity=opacity
            )

        doc.save(output_path)
        doc.close()

        return output_path
```

##### Markdown to PDF MCP
```python
# Backend/app/integrations/mcp/md_pdf_mcp.py
import markdown
from weasyprint import HTML, CSS
from typing import Optional

class MarkdownPDFMCP:
    """Convert Markdown to PDF with styling."""

    async def convert_markdown_to_pdf(
        self,
        markdown_content: str,
        output_path: str,
        css_path: Optional[str] = None
    ) -> str:
        """Convert markdown content to PDF."""
        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'codehilite']
        )

        # Wrap in HTML template
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Chapter Preview</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        </head>
        <body>
            <article class="markdown-body">
                {html_content}
            </article>
        </body>
        </html>
        """

        # Generate PDF
        if css_path:
            with open(css_path) as f:
                css = CSS(string=f.read())
            HTML(string=html_template).write_pdf(output_path, stylesheets=[css])
        else:
            HTML(string=html_template).write_pdf(output_path)

        return output_path

    async def apply_template(
        self,
        content: str,
        template_name: str,
        output_path: str
    ) -> str:
        """Apply predefined template to content."""
        templates = {
            "book_chapter": "templates/book_chapter.html",
            "report": "templates/report.html",
            "article": "templates/article.html"
        }

        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")

        # Load template and render with content
        with open(templates[template_name]) as f:
            template = f.read()

        html_content = template.replace("{{ content }}", content)
        HTML(string=html_content).write_pdf(output_path)

        return output_path

    async def add_styling(self, css_content: str, markdown_content: str, output_path: str) -> str:
        """Apply custom CSS styling."""
        html_content = markdown.markdown(markdown_content)
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>{css_content}</style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        HTML(string=styled_html).write_pdf(output_path)
        return output_path
```

##### LaTeX PDF MCP
```python
# Backend/app/integrations/mcp/latex_pdf_mcp.py
import subprocess
import os
from typing import Optional

class LaTeXPDFMCP:
    """Compile LaTeX to PDF."""

    async def compile_pdf(
        self,
        latex_content: str,
        output_path: str,
        template_path: Optional[str] = None
    ) -> str:
        """Compile LaTeX content to PDF."""
        # If template provided, merge content
        if template_path:
            with open(template_path) as f:
                template = f.read()
            latex_content = template.replace("{{ content }}", latex_content)

        # Write LaTeX to temporary file
        tex_file = output_path.replace(".pdf", ".tex")
        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(latex_content)

        # Compile with XeLaTeX
        try:
            result = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", tex_file],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(tex_file)
            )

            if result.returncode != 0:
                raise RuntimeError(f"LaTeX compilation failed: {result.stderr}")

        finally:
            # Clean up auxiliary files
            for ext in [".aux", ".log", ".out"]:
                aux_file = tex_file.replace(".tex", ext)
                if os.path.exists(aux_file):
                    os.remove(aux_file)

        return output_path
```

**MCP Orchestrator:**
```python
# Backend/app/integrations/orchestrator.py
from .mcp.google_drive_mcp import GoogleDriveMCP
from .mcp.pdf_manipulation_mcp import PDFManipulationMCP
from .mcp.md_pdf_mcp import MarkdownPDFMCP
from .mcp.latex_pdf_mcp import LaTeXPDFMCP

class MCPOrchestrator:
    """Coordinate all MCP server integrations."""

    def __init__(self):
        self.google_drive = GoogleDriveMCP()
        self.pdf_manipulation = PDFManipulationMCP()
        self.md_pdf = MarkdownPDFMCP()
        self.latex_pdf = LaTeXPDFMCP()

    async def process_chapter_pdf(
        self,
        chapter_pdf_path: str,
        chapter_number: int,
        book_title: str
    ) -> dict:
        """Process a chapter PDF: add numbering, watermark."""
        # Add page numbers
        numbered_pdf = chapter_pdf_path.replace(".pdf", "_numbered.pdf")
        await self.pdf_manipulation.add_page_numbers(
            chapter_pdf_path,
            numbered_pdf
        )

        # Add watermark
        watermarked_pdf = numbered_pdf.replace("_numbered.pdf", "_watermarked.pdf")
        await self.pdf_manipulation.add_watermark(
            numbered_pdf,
            watermarked_pdf,
            watermark_text=f"{book_title} - Chapter {chapter_number}"
        )

        return {"processed_pdf": watermarked_pdf}

    async def compile_full_book(
        self,
        chapter_pdfs: List[str],
        output_path: str
    ) -> str:
        """Merge all chapter PDFs into full book."""
        return await self.pdf_manipulation.merge_pdfs(
            chapter_pdfs,
            output_path
        )

    async def upload_and_share(self, pdf_path: str, filename: str) -> dict:
        """Upload to Google Drive and get share link."""
        result = await self.google_drive.upload_file(pdf_path, filename)
        share_link = await self.google_drive.get_share_link(result["file_id"])
        return {"file_id": result["file_id"], "share_link": share_link}
```

**Verification:**
```bash
# Test MCP integrations
pytest tests/integrations/test_mcp_*.py -v

# Manual test
python -c "
from app.integrations.orchestrator import MCPOrchestrator
import asyncio

async def test():
    orchestrator = MCPOrchestrator()
    # Test PDF merge
    result = await orchestrator.pdf_manipulation.merge_pdfs(
        ['ch1.pdf', 'ch2.pdf'],
        'full_book.pdf'
    )
    print(f'Merged: {result}')

asyncio.run(test())
"
```

---

#### 2.4 WebSocket Real-time Updates

**Priority:** 🟠 HIGH
**File:** `Backend/app/websocket/manager.py`
**Estimated Time:** 3 hours

**WebSocket Manager:**

```python
from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manage WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect new WebSocket."""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Disconnect WebSocket."""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_update(self, user_id: str, message: dict):
        """Send update to all connections for a user."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending WebSocket message: {e}")

    async def broadcast_progress(self, book_id: str, user_id: str, progress: int, step: str):
        """Broadcast generation progress."""
        message = {
            "type": "progress_update",
            "book_id": str(book_id),
            "data": {
                "progress": progress,
                "current_step": step
            }
        }
        await self.send_update(user_id, message)

    async def broadcast_complete(self, book_id: str, user_id: str, pdf_path: str, drive_url: str):
        """Broadcast generation completion."""
        message = {
            "type": "generation_complete",
            "book_id": str(book_id),
            "data": {
                "pdf_path": pdf_path,
                "drive_url": drive_url
            }
        }
        await self.send_update(user_id, message)

    async def broadcast_error(self, book_id: str, user_id: str, error: str):
        """Broadcast generation error."""
        message = {
            "type": "generation_error",
            "book_id": str(book_id),
            "data": {
                "error_message": error
            }
        }
        await self.send_update(user_id, message)

manager = WebSocketManager()
```

**WebSocket Endpoint:**
```python
# Backend/app/api/v1/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.auth_service import get_current_user
from app.websocket.manager import manager

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time updates."""
    try:
        # Verify token and get user
        user = await get_current_user(token=token, db=db)

        # Connect WebSocket
        await manager.connect(websocket, str(user.id))

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()

            # Handle incoming messages if needed
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, str(user.id))
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()
```

**Integration with Celery Tasks:**
```python
# Update generation task to send WebSocket updates
from app.websocket.manager import manager

@celery_app.task(bind=True, name="generate_book_task")
def generate_book_task(self, book_id: str, user_id: str, **kwargs):
    """Main book generation task with WebSocket updates."""
    try:
        # Send initial update
        import asyncio
        asyncio.run(manager.broadcast_progress(
            book_id, user_id, 5, "Initializing generation"
        ))

        # Run generation pipeline
        result = generation_graph.invoke({**kwargs})

        # Send completion update
        asyncio.run(manager.broadcast_complete(
            book_id, user_id,
            result["pdf_path"],
            result["drive_url"]
        ))

        return result

    except Exception as e:
        # Send error update
        asyncio.run(manager.broadcast_error(
            book_id, user_id, str(e)
        ))
        raise
```

**Verification:**
```bash
# Test WebSocket connection
# Browser console:
const ws = new WebSocket('ws://localhost:8000/api/v1/ws?token=YOUR_TOKEN');
ws.onmessage = (event) => console.log(JSON.parse(event.data));

# Should receive progress updates during generation
```

---

### Phase 3: Frontend Integration (Days 6-7)

#### 3.1 Connect Frontend to Backend APIs

**Priority:** 🟠 HIGH
**Directory:** `Frontend/src/lib/api/`
**Estimated Time:** 4 hours

**Status:** ⚠️ Generation API completed, others need verification

**Action Items:**
```typescript
// Frontend/src/lib/api/books.ts - Verify implementation
import { apiClient } from './client';

export interface Book {
  id: string;
  title: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  progress: number;
  current_step: string;
  created_at: string;
}

export async function getBooks(params?: {
  skip?: number;
  limit?: number;
  status?: string;
}): Promise<{ items: Book[]; total: number }> {
  const response = await apiClient.get('/books', { params });
  return response.data;
}

export async function getBook(bookId: string): Promise<Book> {
  const response = await apiClient.get(`/books/${bookId}`);
  return response.data;
}

export async function createBook(data: {
  title: string;
  input_method: 'single_line' | 'outline' | 'google_sheet';
  topic?: string;
  outline?: string;
  sheet_url?: string;
}): Promise<Book> {
  const response = await apiClient.post('/books', data);
  return response.data;
}

export async function updateBook(
  bookId: string,
  data: Partial<Book>
): Promise<Book> {
  const response = await apiClient.put(`/books/${bookId}`, data);
  return response.data;
}

export async function deleteBook(bookId: string): Promise<void> {
  await apiClient.delete(`/books/${bookId}`);
}

export async function getBookChapters(bookId: string): Promise<any[]> {
  const response = await apiClient.get(`/books/${bookId}/chapters`);
  return response.data;
}
```

**Zustand Store Updates:**
```typescript
// Frontend/src/stores/booksStore.ts - Verify implementation
import { create } from 'zustand';
import { getBooks, getBook, createBook, updateBook, deleteBook } from '../lib/api/books';
import { Book } from '../types/book';

interface BooksState {
  books: Book[];
  currentBook: Book | null;
  loading: boolean;
  error: string | null;

  // Actions
  fetchBooks: () => Promise<void>;
  fetchBook: (id: string) => Promise<void>;
  createBook: (data: any) => Promise<void>;
  updateBook: (id: string, data: any) => Promise<void>;
  deleteBook: (id: string) => Promise<void>;
  clearCurrentBook: () => void;
}

export const useBooksStore = create<BooksState>((set) => ({
  books: [],
  currentBook: null,
  loading: false,
  error: null,

  fetchBooks: async () => {
    set({ loading: true, error: null });
    try {
      const response = await getBooks();
      set({ books: response.items, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  fetchBook: async (id) => {
    set({ loading: true, error: null });
    try {
      const book = await getBook(id);
      set({ currentBook: book, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  createBook: async (data) => {
    set({ loading: true, error: null });
    try {
      const book = await createBook(data);
      set((state) => ({
        books: [...state.books, book],
        loading: false
      }));
      return book;
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  updateBook: async (id, data) => {
    set({ loading: true, error: null });
    try {
      const updated = await updateBook(id, data);
      set((state) => ({
        books: state.books.map((b) => (b.id === id ? updated : b)),
        currentBook: state.currentBook?.id === id ? updated : state.currentBook,
        loading: false
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  deleteBook: async (id) => {
    set({ loading: true, error: null });
    try {
      await deleteBook(id);
      set((state) => ({
        books: state.books.filter((b) => b.id !== id),
        currentBook: state.currentBook?.id === id ? null : state.currentBook,
        loading: false
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  clearCurrentBook: () => set({ currentBook: null }),
}));
```

**WebSocket Integration:**
```typescript
// Frontend/src/stores/websocketStore.ts
import { create } from 'zustand';

interface WebSocketState {
  connected: boolean;
  ws: WebSocket | null;

  connect: (token: string) => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
}

export const useWebSocketStore = create<WebSocketState>((set) => ({
  connected: false,
  ws: null,

  connect: (token) => {
    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws?token=${token}`);

    ws.onopen = () => {
      set({ connected: true, ws });
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      // Handle different message types
      if (message.type === 'progress_update') {
        // Update book progress in store
        useBooksStore.getState().updateBook(message.book_id, {
          progress: message.data.progress,
          current_step: message.data.current_step
        });
      } else if (message.type === 'generation_complete') {
        // Update book to completed status
        useBooksStore.getState().updateBook(message.book_id, {
          status: 'completed'
        });
      } else if (message.type === 'generation_error') {
        // Update book to failed status
        useBooksStore.getState().updateBook(message.book_id, {
          status: 'failed'
        });
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      set({ connected: false });
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      set({ connected: false, ws: null });
    };
  },

  disconnect: () => {
    const { ws } = useWebSocketStore.getState();
    if (ws) {
      ws.close();
    }
    set({ connected: false, ws: null });
  },

  sendMessage: (message) => {
    const { ws } = useWebSocketStore.getState();
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  },
}));
```

**Verification:**
```bash
# Test frontend-backend integration
cd Frontend
npm run dev

# Open browser to http://localhost:3000
# Test:
# - Login/Registration
# - Create book
# - View book list
# - Monitor generation progress (real-time updates)
```

---

### Phase 4: Testing & Quality Assurance (Days 8-10)

#### 4.1 Run Integration Tests

**Priority:** 🟡 MEDIUM
**Estimated Time:** 4 hours

**Test Execution:**
```bash
# Backend integration tests
cd Backend
pytest tests/integration/ -v --cov=app --cov-report=html

# Frontend integration tests
cd Frontend
npm run test:integration

# E2E tests (requires backend running)
npx playwright test
```

**Coverage Targets:**
- Backend: 80%+ coverage
- Frontend: 85%+ coverage
- Critical paths: 95%+ coverage

**Key Test Scenarios:**
1. User registration and login
2. Book creation (all input methods)
3. Generation progress tracking
4. PDF generation and download
5. Google Drive upload
6. WebSocket real-time updates
7. Error handling and recovery
8. Token refresh flow

---

#### 4.2 Performance Testing

**Priority:** 🟡 MEDIUM
**Tools:** Locust
**Estimated Time:** 4 hours

**Load Test Script:**
```python
# tests/load_test.py
from locust import HttpUser, task, between

class VibePDFUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login and get token
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpass123"}
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def list_books(self):
        self.client.get("/api/v1/books", headers=self.headers)

    @task(2)
    def get_book(self):
        self.client.get("/api/v1/books/1", headers=self.headers)

    @task(1)
    def create_book(self):
        self.client.post(
            "/api/v1/books",
            headers=self.headers,
            json={
                "title": "Load Test Book",
                "input_method": "single_line",
                "topic": "Test Topic"
            }
        )
```

**Performance Targets:**
```
API Response Times:
- p50: < 200ms
- p95: < 500ms
- p99: < 1000ms

Concurrent Users: 100
Sustained Requests/Second: 50
```

**Run Tests:**
```bash
# Start Locust
locust -f tests/load_test.py --host=http://localhost:8000

# Open http://localhost:8089
# Configure: 100 users, hatch rate: 10 users/s
# Run for 5-10 minutes
```

---

#### 4.3 Security Audit

**Priority:** 🟢 PRE-PRODUCTION
**Estimated Time:** 3 hours

**Security Checklist:**

**Authentication & Authorization:**
```bash
# Test JWT token handling
curl -H "Authorization: Bearer INVALID_TOKEN" http://localhost:8000/api/v1/books
# Should return 401 Unauthorized

# Test ownership verification
# Create book as User A
# Try to access as User B
# Should return 403 Forbidden
```

**Input Validation:**
```bash
# Test SQL injection prevention
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d '{"email":"admin@example.com","password":"\' OR 1=1 --"}'
# Should reject (500/400 error)

# Test XSS prevention in book titles
curl -X POST http://localhost:8000/api/v1/books \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"<script>alert(1)</script>"}'
# Should sanitize or reject
```

**Rate Limiting:**
```bash
# Test rate limiting endpoint
for i in {1..20}; do
  curl http://localhost:8000/api/v1/books
done
# Should trigger rate limit after threshold
```

**CORS Configuration:**
```bash
# Test CORS headers
curl -H "Origin: https://malicious-site.com" \
  -I http://localhost:8000/api/v1/books
# Access-Control-Allow-Origin should be whitelisted only
```

**Dependency Vulnerability Scan:**
```bash
# Python dependencies
pip-audit

# Node dependencies
npm audit

# Docker image
trivy image vibe-pdf-backend:latest
```

---

### Phase 5: Pre-Production Deployment (Days 11-14)

#### 5.1 Production Environment Configuration

**Priority:** 🟢 PRE-PRODUCTION
**Estimated Time:** 4 hours

**Environment Variables:**
```bash
# .env.production
APP_ENV=production
DEBUG=False
SECRET_KEY=<GENERATE_SECURE_JWT_SECRET>

# Database (production PostgreSQL)
DATABASE_URL=postgresql+asyncpg://vibepdf:<password>@prod-db-host:5432/vibepdf

# Redis (production Redis)
REDIS_URL=redis://prod-redis-host:6379/0

# OAuth (production Google Cloud Console)
GOOGLE_OAUTH_CLIENT_ID=<production-client-id>
GOOGLE_OAUTH_CLIENT_SECRET=<production-client-secret>
GOOGLE_OAUTH_REDIRECT_URI=https://api.vibepdf.com/api/v1/auth/google/callback

# LLM Providers
ANTHROPIC_API_KEY=<production-key>
OPENAI_API_KEY=<production-key>
GOOGLE_AI_API_KEY=<production-key>
LLM_PROVIDER_PRIORITY=anthropic,openai,google

# Storage (production Google Cloud Storage)
GOOGLE_CREDENTIALS_PATH=/app/credentials/production-google.json
GOOGLE_DRIVE_FOLDER_ID=<production-folder-id>

# CORS (production domains only)
CORS_ORIGINS=https://vibepdf.com,https://www.vibepdf.com

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Monitoring
SENTRY_DSN=<sentry-dsn>
PROMETHEUS_ENABLED=True
LOG_LEVEL=INFO
```

**Production Docker Compose:**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: vibepdf
      POSTGRES_USER: vibepdf
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: always

  backend:
    image: vibe-pdf-backend:latest
    environment:
      - DATABASE_URL=postgresql+asyncpg://vibepdf:${DB_PASSWORD}@postgres:5432/vibepdf
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  celery_worker:
    image: vibe-pdf-backend:latest
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://vibepdf:${DB_PASSWORD}@postgres:5432/vibepdf
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: always

  flower:
    image: vibe-pdf-backend:latest
    command: celery -A app.tasks.celery_app flower --port=5555
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: always
    ports:
      - "5555:5555"

  frontend:
    image: vibe-pdf-frontend:latest
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: always

volumes:
  postgres_data:
  redis_data:
```

---

#### 5.2 CI/CD Pipeline Configuration

**Priority:** 🟢 PRE-PRODUCTION
**File:** `.github/workflows/ci.yml`
**Estimated Time:** 3 hours

**GitHub Actions Workflow:**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    name: Lint Code
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd Backend
          pip install -r requirements.txt
          pip install ruff black

      - name: Run Ruff linting
        run: cd Backend && ruff check .

      - name: Run Black formatting check
        run: cd Backend && black --check .

  test-backend:
    name: Test Backend
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd Backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd Backend
          pytest tests/ -v --cov=app --cov-report=xml --cov-report=html

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: Backend/coverage.xml

  test-frontend:
    name: Test Frontend
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd Frontend
          npm ci

      - name: Run unit tests
        run: |
          cd Frontend
          npm run test -- --coverage

      - name: Run E2E tests
        run: |
          cd Frontend
          npx playwright install
          npm run test:e2e

  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  build-and-deploy:
    name: Build and Deploy
    needs: [lint, test-backend, test-frontend, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Build Docker images
        run: |
          docker build -t vibe-pdf-backend:latest -f Backend/Dockerfile .
          docker build -t vibe-pdf-frontend:latest -f Frontend/Dockerfile .

      - name: Deploy to production
        run: |
          # Deploy to your production environment
          # Example: docker push to registry, kubectl apply, etc.
          echo "Deploying to production..."
```

---

#### 5.3 Monitoring & Observability Setup

**Priority:** 🟢 PRE-PRODUCTION
**Estimated Time:** 4 hours

**Prometheus Metrics:**
```python
# Backend/app/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Business metrics
books_generated_total = Counter(
    'books_generated_total',
    'Total books generated'
)

generation_duration_seconds = Histogram(
    'generation_duration_seconds',
    'Book generation duration'
)

active_websocket_connections = Gauge(
    'active_websocket_connections',
    'Active WebSocket connections'
)

# Application info
app_info = Info('vibe_pdf', 'Vibe PDF application info')
app_info.info({
    'version': '1.0.0',
    'environment': os.getenv('APP_ENV', 'development')
})

# Middleware to track requests
from fastapi import Request
import time

async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    http_request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

**Grafana Dashboard:**
```json
{
  "dashboard": {
    "title": "Vibe PDF Platform",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "{{endpoint}}"
          }
        ]
      },
      {
        "title": "Books Generated",
        "targets": [
          {
            "expr": "rate(books_generated_total[1h])"
          }
        ]
      },
      {
        "title": "Active WebSocket Connections",
        "targets": [
          {
            "expr": "active_websocket_connections"
          }
        ]
      }
    ]
  }
}
```

**Alerting Rules:**
```yaml
# alerting_rules.yml
groups:
  - name: vibe_pdf_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p95 response time above 1s"

      - alert: DatabaseConnectionDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL database is down"

      - alert: RedisConnectionDown
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis is down"

      - alert: CeleryWorkerDown
        expr: up{job="celery_worker"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Celery worker is down"
```

**Sentry Error Tracking:**
```python
# Backend/app/core/logging.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(),
        CeleryIntegration()
    ],
    traces_sample_rate=0.1,
    environment=os.getenv("APP_ENV", "development")
)
```

---

#### 5.4 Database Backup Strategy

**Priority:** 🟢 PRE-PRODUCTION
**Estimated Time:** 2 hours

**Backup Script:**
```bash
#!/bin/bash
# scripts/backup_database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
DATABASE_URL="postgresql://vibepdf:${DB_PASSWORD}@postgres:5432/vibepdf"

# Create backup directory
mkdir -p $BACKUP_DIR

# Dump database
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Upload to cloud storage (optional)
# aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://vibepdf-backups/

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

**Cron Job:**
```bash
# Backup every day at 2 AM
0 2 * * * /app/scripts/backup_database.sh >> /var/log/backup.log 2>&1
```

---

#### 5.5 Final Smoke Tests

**Priority:** 🟢 PRE-PRODUCTION
**Estimated Time:** 2 hours

**Smoke Test Suite:**
```python
# tests/smoke_test.py
import pytest
import requests

BASE_URL = "https://api.vibepdf.com"

def test_health_check():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200

def test_user_registration():
    """Test user registration"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={
            "email": "smoketest@example.com",
            "password": "testpass123",
            "name": "Smoke Test"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_book_creation():
    """Test book creation"""
    token = get_test_token()

    response = requests.post(
        f"{BASE_URL}/api/v1/books",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Smoke Test Book",
            "input_method": "single_line",
            "topic": "Test Topic"
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Smoke Test Book"

def test_generation_start():
    """Test generation start"""
    token = get_test_token()
    book_id = create_test_book(token)

    response = requests.post(
        f"{BASE_URL}/api/v1/generation/start",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "book_id": book_id,
            "title": "Test Book"
        }
    )
    assert response.status_code == 200
    assert "task_id" in response.json()

def test_websocket_connection():
    """Test WebSocket connection"""
    token = get_test_token()
    ws = create_connection(f"ws://{BASE_URL}/api/v1/ws?token={token}")
    assert ws.connected

# Run smoke tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Pre-Production Checklist:**
```markdown
## Final Pre-Production Checklist

### Security
- [ ] JWT secret key rotated from default
- [ ] SSL/TLS certificates valid
- [ ] CORS configured for production domains only
- [ ] Rate limiting enabled
- [ ] All secrets removed from version control
- [ ] Dependency vulnerability scan passed
- [ ] Security headers configured
- [ ] SQL injection prevention tested
- [ ] XSS prevention tested
- [ ] CSRF protection enabled

### Performance
- [ ] Load tests passed (100 concurrent users)
- [ ] API response times meet targets (p95 < 500ms)
- [ ] Database indexes created
- [ ] Connection pooling configured
- [ ] Redis caching enabled
- [ ] CDN configured for static assets

### Operations
- [ ] Monitoring dashboards configured (Grafana)
- [ ] Alert rules set up and tested
- [ ] Log aggregation configured (Fluentd/Elasticsearch)
- [ ] Error tracking set up (Sentry)
- [ ] Backup schedule configured and tested
- [ ] Backup restore procedure tested
- [ ] Rollback plan documented
- [ ] Runbooks created for common issues

### Documentation
- [ ] API documentation complete
- [ ] Deployment guide written
- [ ] Monitoring guide written
- [ ] Troubleshooting guide written
- [ ] Architecture diagram updated
- [ ] Team onboarding guide updated

### Testing
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] E2E tests passing
- [ ] Smoke tests passed
- [ ] Performance benchmarks met
- [ ] Security audit passed

### Deployment
- [ ] Production Docker images built
- [ ] CI/CD pipeline tested
- [ ] Database migrations applied to production
- [ ] Secrets injected securely
- [ ] DNS configured
- [ ] Load balancer configured
- [ ] SSL certificates installed
```

---

## Implementation Timeline Summary

| Phase | Duration | Critical Tasks | Deliverables |
|-------|----------|----------------|--------------|
| **Phase 1** | Days 1-2 | Fix imports, deps, migrations, Book API | Running application, auth working |
| **Phase 2** | Days 3-5 | Generation API, Celery tasks, MCP integrations, WebSocket | Core features functional |
| **Phase 3** | Days 6-7 | Frontend integration, API connectivity | End-to-end user flow working |
| **Phase 4** | Days 8-10 | Integration tests, performance tests, security audit | Quality assured |
| **Phase 5** | Days 11-14 | Production config, CI/CD, monitoring, deployment | Production ready |

**Total Estimated Time:** 14 days

---

## Success Criteria

### Minimum Viable Product (MVP)
- [ ] User can register and login
- [ ] User can create a book from topic/outline/sheet
- [ ] User can see generation progress in real-time
- [ ] User can download generated PDF
- [ ] User can view their book library
- [ ] PDF uploads to Google Drive
- [ ] Basic error handling and recovery

### Production Ready
- [ ] All MVP criteria met
- [ ] 80%+ backend test coverage
- [ ] 85%+ frontend test coverage
- [ ] Security audit passed
- [ ] Performance benchmarks met
- [ ] Monitoring and alerting configured
- [ ] CI/CD pipeline operational
- [ ] Backup strategy in place
- [ ] Documentation complete

---

## Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **LLM API rate limits** | Medium | High | Implement queuing, use multiple providers, add exponential backoff |
| **PDF generation failures** | Medium | Medium | Add retry logic with exponential backoff, error recovery, partial generation support |
| **Database migration issues** | Low | High | Test migrations in staging, create backups before migration, have rollback plan |
| **WebSocket connection issues** | Low | Medium | Implement reconnection logic, fallback to polling, connection health monitoring |
| **Google Drive quota exceeded** | Low | Medium | Add quota monitoring, fallback to S3 storage, implement cleanup jobs |
| **Celery task queue overflow** | Medium | Medium | Scale workers, implement task prioritization, add queue monitoring |
| **Memory leaks in long-running processes** | Low | Medium | Regular worker restarts, memory profiling, use memory-efficient libraries |
| **Security vulnerabilities in dependencies** | Medium | High | Regular dependency scans, automated updates, security-focused code review |

---

## Recommended Starting Point

### Task 1: Fix Auth Service Import Error

**Why start here:** This blocks authentication, which is required for all protected endpoints.

**Estimated Time:** 30 minutes

**Steps:**
1. Add `GoogleDriveStorageError` class to `Backend/app/services/storage/google_drive.py`
2. Update `Backend/app/services/__init__.py` to export the error
3. Run `python -c "from app.services import AuthService"` to verify
4. Run auth service tests: `pytest tests/unit/test_auth_service.py`

### Task 2: Install Missing Dependencies

**Why:** Required for tests and some features to work.

**Estimated Time:** 15 minutes

**Steps:**
1. Add missing packages to `Backend/requirements.txt`
2. Run `pip install -r Backend/requirements.txt`
3. Verify imports work

### Task 3: Generate and Apply Database Migrations

**Why:** Database schema not yet deployed.

**Estimated Time:** 1 hour

**Steps:**
1. Ensure PostgreSQL is running
2. Run `alembic revision --autogenerate -m "Initial schema"`
3. Review the generated migration
4. Run `alembic upgrade head`
5. Verify tables created

### Task 4: Implement Book API Endpoints

**Why:** Core CRUD operations don't work.

**Estimated Time:** 3 hours

**Steps:**
1. Implement each endpoint (GET /books, POST /books, etc.)
2. Add proper error handling
3. Add ownership verification
4. Run tests: `pytest tests/test_api_books.py`

---

## Resources & Documentation

### Project Documentation
- [CLAUDE.md](CLAUDE.md) - Complete project reference and architecture
- [plans/remaining_tasks_plan.md](plans/remaining_tasks_plan.md) - Previous task analysis
- [All test reports](.) - Comprehensive testing documentation

### Key Files Reference
| Component | File | Purpose |
|-----------|------|---------|
| Backend API | `Backend/app/api/v1/books.py` | Book CRUD endpoints |
| Backend API | `Backend/app/api/v1/generation.py` | Generation endpoints |
| Backend Services | `Backend/app/services/book_service.py` | Book business logic |
| Backend Services | `Backend/app/services/generation_service.py` | Generation orchestration |
| Backend Tasks | `Backend/app/tasks/generation_tasks.py` | Celery background tasks |
| Frontend API | `Frontend/src/lib/api/books.ts` | Frontend API client |
| Frontend API | `Frontend/src/lib/api/generation.ts` | Generation API client ✅ Completed |
| Frontend Stores | `Frontend/src/stores/booksStore.ts` | Book state management |
| Frontend Stores | `Frontend/src/stores/websocketStore.ts` | WebSocket state management |
| Database | `Backend/app/db/models/*.py` | ORM models |
| Migrations | `Backend/alembic/versions/*.py` | Database migrations |

### Testing References
- Unit Tests: `tests/unit/*.py`, `Frontend/src/**/*.spec.ts`
- Integration Tests: `tests/integration/*.py`
- E2E Tests: `Frontend/e2e/*.spec.ts`
- Load Tests: `tests/load_test.py`
- Visual Tests: `Frontend/src/e2e/visual/*.spec.ts`

---

## Notes for Development Team

1. **Testing Infrastructure:** Excellent foundation with 100+ test files already created. Use these templates for new tests.

2. **Code Quality:** Follow existing patterns in the codebase. The frontend uses TypeScript with strict typing - maintain this standard.

3. **Documentation:** Keep documentation updated as features are implemented. Update CLAUDE.md as the system evolves.

4. **API Design:** Maintain RESTful principles. Use consistent error responses and status codes.

5. **WebSocket:** Real-time updates are a key differentiator. Ensure WebSocket connections are robust and handle reconnection gracefully.

6. **Error Handling:** User-facing errors should be clear and actionable. Log technical details for debugging.

7. **Performance:** The application will handle PDF generation which can be resource-intensive. Optimize for performance and scalability from the start.

8. **Security:** Never hardcode credentials. Use environment variables for all secrets. Follow OWASP security best practices.

9. **Monitoring:** Set up monitoring early in development. Metrics and alerts are invaluable for production debugging.

10. **Backward Compatibility:** When making changes, ensure backward compatibility where possible. Use versioning for breaking API changes.

---

## Contact & Support

For questions or issues related to this implementation plan:

1. **Architecture questions:** Review CLAUDE.md for detailed architecture docs
2. **Testing issues:** Check existing test reports in root directory
3. **API design:** Refer to Backend/app/api/ directory for patterns
4. **Frontend integration:** Check Frontend/src/lib/api/ for existing implementations
5. **Performance concerns:** Review PERFORMANCE_BASELINE.md
6. **Security concerns:** Review SECURITY_AUDIT_REPORT.md (if exists)

---

**Document Version:** 1.0
**Last Updated:** February 25, 2026
**Next Review:** After Phase 1 completion

---

*This implementation plan is based on comprehensive analysis of the existing codebase, testing infrastructure, and documentation. Priorities may need adjustment based on actual implementation challenges discovered during development.*
