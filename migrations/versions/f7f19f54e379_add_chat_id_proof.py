"""Add chat_id proof

Revision ID: f7f19f54e379
Revises: a870f3d9edc7
Create Date: 2024-01-31 12:51:32.232697

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7f19f54e379'
down_revision = 'a870f3d9edc7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('proofs', 'chat_id',
               existing_type=sa.BIGINT(),
               nullable=True)
    op.alter_column('proofs', 'message_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('proofs', 'message_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('proofs', 'chat_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    # ### end Alembic commands ###