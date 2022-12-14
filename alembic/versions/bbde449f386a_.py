"""empty message

Revision ID: bbde449f386a
Revises: 
Create Date: 2022-12-06 13:29:22.985227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bbde449f386a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Auditorium',
    sa.Column('auditorium_id', sa.Integer(), nullable=False),
    sa.Column('seats', sa.Integer(), nullable=True),
    sa.Column('adress', sa.String(length=45), nullable=True),
    sa.Column('price_per_hour', sa.DECIMAL(precision=10, scale=2), nullable=True),
    sa.PrimaryKeyConstraint('auditorium_id')
    )
    op.create_table('User',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=45), nullable=True),
    sa.Column('surname', sa.String(length=45), nullable=True),
    sa.Column('email', sa.String(length=45), nullable=True),
    sa.Column('password', sa.String(length=200), nullable=True),
    sa.Column('role', sa.String(length=45), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('Order',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('auditorium_id', sa.Integer(), nullable=True),
    sa.Column('reservation_start', sa.DATETIME(), nullable=True),
    sa.Column('hours_ordered', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['auditorium_id'], ['Auditorium.auditorium_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ),
    sa.PrimaryKeyConstraint('order_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Order')
    op.drop_table('User')
    op.drop_table('Auditorium')
    # ### end Alembic commands ###
