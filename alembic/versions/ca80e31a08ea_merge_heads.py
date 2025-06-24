"""merge heads

Revision ID: ca80e31a08ea
Revises: 6365fd25385e, 87bb2fcee52a
Create Date: 2025-06-25 00:18:57.630904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca80e31a08ea'
down_revision: Union[str, Sequence[str], None] = ('6365fd25385e', '87bb2fcee52a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
