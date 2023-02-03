"""adding_indexes

Revision ID: e120e80de333
Revises: 4ace343d202b
Create Date: 2023-01-21 01:11:40.190160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e120e80de333'
down_revision = '4ace343d202b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "enqueued_channel",
        "queue",
        ["channel", "enqueued"]
    )
    op.create_index(
        "enqueued_channel_user",
        "queue",
        ["channel", "enqueued", "user_id"]
    )


def downgrade() -> None:
    op.drop_index("enqueued_channel")
    op.drop_index("enqueued_channel_user")
