"""Turn on row-level security for every app table.

Supabase exposes tables in the public schema through its auto-generated REST API.
The Skindex app never uses that API (everything goes through this backend), so we
enable RLS with no policies: the publishable/anon key can read nothing, while the
backend, which connects as the table owner, is unaffected.

Revision ID: 0002
Revises: 0001
"""
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

TABLES = ["profiles", "preferences", "products", "cabinet_items", "entries", "entry_products",
          "analyses", "alembic_version"]


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    for t in TABLES:
        op.execute(f'ALTER TABLE "{t}" ENABLE ROW LEVEL SECURITY')


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    for t in TABLES:
        op.execute(f'ALTER TABLE "{t}" DISABLE ROW LEVEL SECURITY')
