"""
Initial database schema migration.

Creates all tables with optimized indexes for the Vibe PDF Platform.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    book_status = postgresql.ENUM(
        'draft', 'outlining', 'generating_content', 'generating_infographics',
        'compiling_pdf', 'uploading_to_drive', 'completed', 'failed', 'cancelled',
        name='bookstatus',
        create_type=False
    )
    book_status.create(op.get_bind(), checkfirst=True)

    input_method = postgresql.ENUM(
        'topic_description', 'structured_outline', 'existing_document',
        name='inputmethod',
        create_type=False
    )
    input_method.create(op.get_bind(), checkfirst=True)

    task_status = postgresql.ENUM(
        'pending', 'started', 'progress', 'success', 'failure', 'revoked', 'retry',
        name='taskstatus',
        create_type=False
    )
    task_status.create(op.get_bind(), checkfirst=True)

    interaction_type = postgresql.ENUM(
        'view', 'like', 'bookmark', 'download', 'share',
        name='interactiontype',
        create_type=False
    )
    interaction_type.create(op.get_bind(), checkfirst=True)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('google_id', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id'),
    )

    # Indexes for users
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_google_id', 'users', ['google_id'])

    # Create books table
    op.create_table(
        'books',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('topic', sa.String(1000), nullable=True),
        sa.Column('status', book_status, nullable=False, server_default='draft'),
        sa.Column('input_method', input_method, nullable=False),
        sa.Column('input_data', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('drive_url', sa.String(500), nullable=True),
        sa.Column('cover_url', sa.String(500), nullable=True),
        sa.Column('progress_percentage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_step', sa.String(255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Indexes for books (optimized for common queries)
    op.create_index('ix_books_user_id', 'books', ['user_id'])
    op.create_index('ix_books_status', 'books', ['status'])
    op.create_index('ix_books_category', 'books', ['category'])
    op.create_index('ix_books_user_status', 'books', ['user_id', 'status'])
    op.create_index('ix_books_user_created', 'books', ['user_id', 'created_at'])
    op.create_index('ix_books_created_at', 'books', ['created_at'])

    # Create chapters table
    op.create_table(
        'chapters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('content_summary', sa.Text(), nullable=True),
        sa.Column('parent_chapter_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('infographic_url', sa.String(500), nullable=True),
        sa.Column('page_start', sa.Integer(), nullable=True),
        sa.Column('page_end', sa.Integer(), nullable=True),
        sa.Column('content_embedding', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_chapter_id'], ['chapters.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('book_id', 'chapter_number', name='uq_chapter_number_per_book'),
    )

    # Indexes for chapters
    op.create_index('ix_chapters_book_id', 'chapters', ['book_id'])
    op.create_index('ix_chapters_book_number', 'chapters', ['book_id', 'chapter_number'])
    op.create_index('ix_chapters_parent_id', 'chapters', ['parent_chapter_id'])

    # Create generation_tasks table
    op.create_table(
        'generation_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('celery_task_id', sa.String(255), nullable=False),
        sa.Column('status', task_status, nullable=False, server_default='pending'),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_step', sa.String(255), nullable=True),
        sa.Column('result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('celery_task_id'),
    )

    # Indexes for generation_tasks
    op.create_index('ix_generation_tasks_book_id', 'generation_tasks', ['book_id'])
    op.create_index('ix_generation_tasks_celery_id', 'generation_tasks', ['celery_task_id'])
    op.create_index('ix_generation_tasks_status', 'generation_tasks', ['status'])

    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sentiment_score', sa.Numeric(5, 4), nullable=True),
        sa.Column('sentiment_label', sa.String(20), nullable=True),
        sa.Column('aspect_sentiments', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Indexes for reviews
    op.create_index('ix_reviews_book_id', 'reviews', ['book_id'])
    op.create_index('ix_reviews_user_id', 'reviews', ['user_id'])
    op.create_index('ix_reviews_book_user', 'reviews', ['book_id', 'user_id'], unique=True)
    op.create_index('ix_reviews_rating', 'reviews', ['rating'])

    # Create user_interactions table
    op.create_table(
        'user_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interaction_type', interaction_type, nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Indexes for user_interactions
    op.create_index('ix_user_interactions_user_id', 'user_interactions', ['user_id'])
    op.create_index('ix_user_interactions_book_id', 'user_interactions', ['book_id'])
    op.create_index(
        'ix_interactions_user_book_type',
        'user_interactions',
        ['user_id', 'book_id', 'interaction_type'],
        unique=True
    )
    op.create_index('ix_user_interactions_type', 'user_interactions', ['interaction_type'])
    op.create_index('ix_user_interactions_created', 'user_interactions', ['created_at'])

    # Create composite indexes for common query patterns
    # For recommendations: books by category with interactions
    op.create_index(
        'ix_books_category_status',
        'books',
        ['category', 'status']
    )

    # For dashboard: books by user with status
    op.create_index(
        'ix_books_user_status_progress',
        'books',
        ['user_id', 'status', 'progress_percentage']
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_books_user_status_progress', table_name='books')
    op.drop_index('ix_books_category_status', table_name='books')
    op.drop_index('ix_user_interactions_created', table_name='user_interactions')
    op.drop_index('ix_user_interactions_type', table_name='user_interactions')
    op.drop_index('ix_interactions_user_book_type', table_name='user_interactions')
    op.drop_index('ix_user_interactions_book_id', table_name='user_interactions')
    op.drop_index('ix_user_interactions_user_id', table_name='user_interactions')
    op.drop_index('ix_reviews_rating', table_name='reviews')
    op.drop_index('ix_reviews_book_user', table_name='reviews')
    op.drop_index('ix_reviews_user_id', table_name='reviews')
    op.drop_index('ix_reviews_book_id', table_name='reviews')
    op.drop_index('ix_generation_tasks_status', table_name='generation_tasks')
    op.drop_index('ix_generation_tasks_celery_id', table_name='generation_tasks')
    op.drop_index('ix_generation_tasks_book_id', table_name='generation_tasks')
    op.drop_index('ix_chapters_parent_id', table_name='chapters')
    op.drop_index('ix_chapters_book_number', table_name='chapters')
    op.drop_index('ix_chapters_book_id', table_name='chapters')
    op.drop_index('ix_books_created_at', table_name='books')
    op.drop_index('ix_books_user_created', table_name='books')
    op.drop_index('ix_books_user_status', table_name='books')
    op.drop_index('ix_books_category', table_name='books')
    op.drop_index('ix_books_status', table_name='books')
    op.drop_index('ix_books_user_id', table_name='books')
    op.drop_index('ix_users_google_id', table_name='users')
    op.drop_index('ix_users_email', table_name='users')

    # Drop tables
    op.drop_table('user_interactions')
    op.drop_table('reviews')
    op.drop_table('generation_tasks')
    op.drop_table('chapters')
    op.drop_table('books')
    op.drop_table('users')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS interactiontype')
    op.execute('DROP TYPE IF EXISTS taskstatus')
    op.execute('DROP TYPE IF EXISTS inputmethod')
    op.execute('DROP TYPE IF EXISTS bookstatus')
