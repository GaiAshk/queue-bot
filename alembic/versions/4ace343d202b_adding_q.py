"""adding_q

Revision ID: 4ace343d202b
Revises: 
Create Date: 2023-01-20 17:45:41.288163

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4ace343d202b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'queue',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('message', sa.String(255), nullable=False),
        sa.Column('channel', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('enqueued', sa.Boolean, nullable=False)
    )


def downgrade():
    op.drop_table('queue')
