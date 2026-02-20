"""Initial migration - Create books table.

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'books',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('author', sa.String(255), nullable=False),
        sa.Column('isbn', sa.String(20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('pages', sa.Integer(), nullable=True),
        sa.Column('published_year', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_books_author'), 'books', ['author'])
    op.create_index(op.f('ix_books_id'), 'books', ['id'])
    op.create_index(op.f('ix_books_isbn'), 'books', ['isbn'], unique=True)
    op.create_index(op.f('ix_books_title'), 'books', ['title'])


def downgrade() -> None:
    op.drop_index(op.f('ix_books_title'), table_name='books')
    op.drop_index(op.f('ix_books_isbn'), table_name='books')
    op.drop_index(op.f('ix_books_id'), table_name='books')
    op.drop_index(op.f('ix_books_author'), table_name='books')
    op.drop_table('books')
