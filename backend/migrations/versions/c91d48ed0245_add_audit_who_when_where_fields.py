"""add_audit_who_when_where_fields

Revision ID: c91d48ed0245
Revises: fb2d71849d7b
Create Date: 2026-06-04 06:15:40.211110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c91d48ed0245'
down_revision = 'fb2d71849d7b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_categories_updater', 'users', ['updated_by_id'], ['id'])
        batch_op.create_foreign_key('fk_categories_creator', 'users', ['created_by_id'], ['id'])

    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_customers_creator', 'users', ['created_by_id'], ['id'])
        batch_op.create_foreign_key('fk_customers_updater', 'users', ['updated_by_id'], ['id'])

    with op.batch_alter_table('discounts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_discounts_creator', 'users', ['created_by_id'], ['id'])
        batch_op.create_foreign_key('fk_discounts_updater', 'users', ['updated_by_id'], ['id'])

    with op.batch_alter_table('inventory_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_inventory_logs_updater', 'users', ['updated_by_id'], ['id'])
        batch_op.create_foreign_key('fk_inventory_logs_creator', 'users', ['created_by_id'], ['id'])

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_products_creator', 'users', ['created_by_id'], ['id'])
        batch_op.create_foreign_key('fk_products_updater', 'users', ['updated_by_id'], ['id'])

    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.add_column(sa.Column('terminal_id', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('store_location', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('device_ip', sa.String(length=45), nullable=True))
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_sales_creator', 'users', ['created_by_id'], ['id'])
        batch_op.create_foreign_key('fk_sales_updater', 'users', ['updated_by_id'], ['id'])

    with op.batch_alter_table('shifts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('terminal_id', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('store_location', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_shifts_creator', 'users', ['created_by_id'], ['id'])
        batch_op.create_foreign_key('fk_shifts_updater', 'users', ['updated_by_id'], ['id'])

    with op.batch_alter_table('user_types', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_user_types_updater', 'users', ['updated_by_id'], ['id'], use_alter=True)
        batch_op.create_foreign_key('fk_user_types_creator', 'users', ['created_by_id'], ['id'], use_alter=True)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('last_login', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('last_login_ip', sa.String(length=45), nullable=True))
        batch_op.create_foreign_key('fk_users_creator', 'users', ['created_by_id'], ['id'])
        batch_op.create_foreign_key('fk_users_updater', 'users', ['updated_by_id'], ['id'])


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_updater', type_='foreignkey')
        batch_op.drop_constraint('fk_users_creator', type_='foreignkey')
        batch_op.drop_column('last_login_ip')
        batch_op.drop_column('last_login')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('user_types', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_types_creator', type_='foreignkey')
        batch_op.drop_constraint('fk_user_types_updater', type_='foreignkey')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('shifts', schema=None) as batch_op:
        batch_op.drop_constraint('fk_shifts_updater', type_='foreignkey')
        batch_op.drop_constraint('fk_shifts_creator', type_='foreignkey')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')
        batch_op.drop_column('store_location')
        batch_op.drop_column('terminal_id')

    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.drop_constraint('fk_sales_updater', type_='foreignkey')
        batch_op.drop_constraint('fk_sales_creator', type_='foreignkey')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')
        batch_op.drop_column('device_ip')
        batch_op.drop_column('store_location')
        batch_op.drop_column('terminal_id')

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_constraint('fk_products_updater', type_='foreignkey')
        batch_op.drop_constraint('fk_products_creator', type_='foreignkey')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('inventory_logs', schema=None) as batch_op:
        batch_op.drop_constraint('fk_inventory_logs_creator', type_='foreignkey')
        batch_op.drop_constraint('fk_inventory_logs_updater', type_='foreignkey')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('discounts', schema=None) as batch_op:
        batch_op.drop_constraint('fk_discounts_updater', type_='foreignkey')
        batch_op.drop_constraint('fk_discounts_creator', type_='foreignkey')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.drop_constraint('fk_customers_updater', type_='foreignkey')
        batch_op.drop_constraint('fk_customers_creator', type_='foreignkey')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.drop_constraint('fk_categories_creator', type_='foreignkey')
        batch_op.drop_constraint('fk_categories_updater', type_='foreignkey')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')
