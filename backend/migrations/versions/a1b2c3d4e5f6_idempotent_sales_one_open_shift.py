"""sales.client_ref (idempotent checkout) and one open shift per cashier

Revision ID: a1b2c3d4e5f6
Revises: 06616187fee0
Create Date: 2026-11-07 12:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '06616187fee0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.add_column(sa.Column('client_ref', sa.String(length=64), nullable=True))
        batch_op.create_unique_constraint('uq_sales_client_ref', ['client_ref'])

    # Fractional sales (0.25 kg) were being rounded to whole numbers in the stock audit log
    with op.batch_alter_table('inventory_logs', schema=None) as batch_op:
        batch_op.alter_column('quantity_changed', existing_type=sa.Integer(),
                              type_=sa.Numeric(precision=10, scale=3), existing_nullable=False)

    # Keep only the newest open shift per cashier so the unique index can be created
    op.execute("""
        UPDATE shifts SET status = 'closed', end_time = start_time
        WHERE status = 'open' AND id NOT IN (
            SELECT DISTINCT ON (cashier_id) id FROM shifts WHERE status = 'open'
            ORDER BY cashier_id, start_time DESC
        )
    """)
    op.create_index('uq_one_open_shift_per_cashier', 'shifts', ['cashier_id'], unique=True,
                    postgresql_where=sa.text("status = 'open'"))


def downgrade():
    with op.batch_alter_table('inventory_logs', schema=None) as batch_op:
        batch_op.alter_column('quantity_changed', existing_type=sa.Numeric(precision=10, scale=3),
                              type_=sa.Integer(), existing_nullable=False)
    op.drop_index('uq_one_open_shift_per_cashier', table_name='shifts')
    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.drop_constraint('uq_sales_client_ref', type_='unique')
        batch_op.drop_column('client_ref')
