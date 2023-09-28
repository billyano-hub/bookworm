"""empty message

Revision ID: b6875bff6a64
Revises: ece4777d5fd5
Create Date: 2023-09-20 13:22:09.558129

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b6875bff6a64'
down_revision = 'ece4777d5fd5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contactus',
    sa.Column('contact_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('contact_email', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('contact_id')
    )
    with op.batch_alter_table('lga', schema=None) as batch_op:
        batch_op.alter_column('lga_name',
               existing_type=mysql.VARCHAR(length=50),
               type_=sa.String(length=20),
               existing_nullable=False,
               existing_server_default=sa.text("''"))
        batch_op.create_foreign_key(None, 'state', ['state_id'], ['state_id'])

    with op.batch_alter_table('state', schema=None) as batch_op:
        batch_op.alter_column('state_name',
               existing_type=mysql.VARCHAR(length=80),
               type_=sa.String(length=20),
               existing_nullable=False,
               existing_server_default=sa.text("''"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('state', schema=None) as batch_op:
        batch_op.alter_column('state_name',
               existing_type=sa.String(length=20),
               type_=mysql.VARCHAR(length=80),
               existing_nullable=False,
               existing_server_default=sa.text("''"))

    with op.batch_alter_table('lga', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('lga_name',
               existing_type=sa.String(length=20),
               type_=mysql.VARCHAR(length=50),
               existing_nullable=False,
               existing_server_default=sa.text("''"))

    op.drop_table('contactus')
    # ### end Alembic commands ###
