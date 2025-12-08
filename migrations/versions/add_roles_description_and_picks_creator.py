"""Add roles.description and picks.creator_id

Revision ID: add_roles_description_and_picks_creator
Revises: 8019d75e3d9f
Create Date: 2025-12-03
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_roles_description_and_picks_creator'
down_revision = '8019d75e3d9f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    def table_exists(connection, table_name: str) -> bool:
        try:
            res = connection.execute(sa.text(f"PRAGMA table_info('{table_name}')"))
            return len(res.fetchall()) > 0
        except Exception:
            return False

    def column_exists(connection, table_name: str, column_name: str) -> bool:
        try:
            res = connection.execute(sa.text(f"PRAGMA table_info('{table_name}')"))
            rows = res.fetchall()
            return any(row[1] == column_name for row in rows)
        except Exception:
            return False

    # Add description column to roles if table and column missing
    if table_exists(conn, 'roles') and not column_exists(conn, 'roles', 'description'):
        try:
            op.add_column('roles', sa.Column('description', sa.String(length=500), nullable=True))
        except Exception:
            pass

    # Add creator_id column to picks if table exists and column missing
    if table_exists(conn, 'picks') and not column_exists(conn, 'picks', 'creator_id'):
        try:
            op.add_column('picks', sa.Column('creator_id', sa.Integer(), nullable=True))
        except Exception:
            pass
    
    # Try to create FK if both tables exist
    if table_exists(conn, 'picks') and table_exists(conn, 'users'):
        try:
            op.create_foreign_key(
                'fk_picks_creator_id_users',
                'picks', 'users',
                ['creator_id'], ['id'],
                ondelete='SET NULL'
            )
        except Exception:
            # If FK creation fails (e.g. legacy schema / SQLite limitations), skip safely
            pass


def downgrade() -> None:
    conn = op.get_bind()

    def table_exists(connection, table_name: str) -> bool:
        try:
            res = connection.execute(sa.text(f"PRAGMA table_info('{table_name}')"))
            return len(res.fetchall()) > 0
        except Exception:
            return False

    def column_exists(connection, table_name: str, column_name: str) -> bool:
        try:
            res = connection.execute(sa.text(f"PRAGMA table_info('{table_name}')"))
            rows = res.fetchall()
            return any(row[1] == column_name for row in rows)
        except Exception:
            return False

    if table_exists(conn, 'picks'):
        try:
            op.drop_constraint('fk_picks_creator_id_users', 'picks', type_='foreignkey')
        except Exception:
            pass
        if column_exists(conn, 'picks', 'creator_id'):
            try:
                op.drop_column('picks', 'creator_id')
            except Exception:
                pass
    
    if table_exists(conn, 'roles') and column_exists(conn, 'roles', 'description'):
        try:
            op.drop_column('roles', 'description')
        except Exception:
            pass
