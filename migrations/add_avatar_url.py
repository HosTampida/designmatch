"""Add avatar_url to users table

Revision ID: 001
Revises: 
Create Date: 2024-MM-DD

"""
from alembic import op
import sqlalchemy as sa


revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=False, server_default=''))
    print("✅ Added avatar_url column to users table")


def downgrade():
    op.drop_column('users', 'avatar_url')
    print("🔄 Dropped avatar_url column")
