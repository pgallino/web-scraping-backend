"""
create tool table

Revision ID: 0001_create_tool_table
Revises: 
Create Date: 2025-10-25
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_tool_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "tool",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("link", sa.String, nullable=True),
    )


def downgrade():
    op.drop_table("tool")
