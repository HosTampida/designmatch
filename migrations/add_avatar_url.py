"""Add avatar_url to users table

Revision ID: 001
Revises:
Create Date: 2024-MM-DD

"""

import logging

from alembic import op
import sqlalchemy as sa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=False, server_default=''))
    logger.info("Added avatar_url column to users table")


def downgrade():
    op.drop_column('users', 'avatar_url')
    logger.info("Dropped avatar_url column")
