"""Book models - extends Ebook with additional book-specific functionality.

This module provides the Book model which extends the Ebook model
with additional book-specific features and helpers.
"""
from app.models.user import Ebook, Chapter, BookStatus

# Re-export Ebook as Book for clarity in book-generation contexts
Book = Ebook
BookChapter = Chapter

__all__ = ["Book", "BookChapter", "BookStatus"]
