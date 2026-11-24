"""initial_schema

Revision ID: ace91d80022d
Revises: 
Create Date: 2026-11-23 20:59:59.543934

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

from app.models.models import Base

# revision identifiers, used by Alembic.
revision: str = 'ace91d80022d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Authoritative initial schema creation for all EduPath AI models."""
    bind = op.get_bind()
    Base.metadata.create_all(bind)

def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    Base.metadata.drop_all(bind)
