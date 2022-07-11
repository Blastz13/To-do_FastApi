"""fix tables

Revision ID: 5962bc9b0934
Revises: 16109813f504
Create Date: 2022-07-08 21:56:45.979703

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5962bc9b0934'
down_revision = '16109813f504'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('status_task_task_id_fkey', 'status_task', type_='foreignkey')
    op.create_foreign_key(None, 'status_task', 'task', ['task_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'status_task', type_='foreignkey')
    op.create_foreign_key('status_task_task_id_fkey', 'status_task', 'task', ['task_id'], ['id'])
    # ### end Alembic commands ###