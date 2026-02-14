"""add post.short_id + index

Revision ID: 2f3b9d5a6c4e
Revises: 87658e74e03c
Create Date: 2026-02-14 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = "2f3b9d5a6c4e"
down_revision = "87658e74e03c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # add nullable column so we can backfill existing rows
    op.add_column("post", sa.Column("short_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True))

    # backfill short_id from UUID (first dash-separated segment)
    op.execute("UPDATE post SET short_id = split_part(id::text, '-', 1)")

    # now make the column non-nullable and add an index for fast lookups
    op.alter_column("post", "short_id", nullable=False)
    op.create_index("ix_post_short_id", "post", ["short_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_post_short_id", table_name="post")
    op.drop_column("post", "short_id")
