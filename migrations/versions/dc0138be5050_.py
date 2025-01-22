"""empty message

Revision ID: dc0138be5050
Revises: e40d76bfaa0c
Create Date: 2025-01-15 18:24:16.923671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc0138be5050'
down_revision = 'e40d76bfaa0c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorite_planets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('planet_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('favorite_planets_planets_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'planets', ['planet_id'], ['id'])
        batch_op.drop_column('planets_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorite_planets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('planets_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('favorite_planets_planets_id_fkey', 'planets', ['planets_id'], ['id'])
        batch_op.drop_column('planet_id')

    # ### end Alembic commands ###
