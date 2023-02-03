"""adding duration in q

Revision ID: 4f965fed9874
Revises: e120e80de333
Create Date: 2023-01-22 21:02:58.678376

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4f965fed9874'
down_revision = 'e120e80de333'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('queue', sa.Column('q_duration_s', sa.Float, nullable=False, default=0.0))
    op.add_column('queue', sa.Column('last_update_ts', sa.TIMESTAMP(), nullable=False,
                                     server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))


def downgrade() -> None:
    op.drop_column('queue', 'q_duration_s')
    op.drop_column('queue', 'last_update_ts')
