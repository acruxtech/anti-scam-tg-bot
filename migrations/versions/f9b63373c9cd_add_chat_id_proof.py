"""Add chat_id proof

Revision ID: f9b63373c9cd
Revises: 64e4b89d497c
Create Date: 2024-01-30 12:05:47.762685

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9b63373c9cd'
down_revision = '64e4b89d497c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scammers_reports_media', sa.Column('scammer_id', sa.BigInteger(), nullable=False))
    op.create_foreign_key(None, 'scammers_reports_media', 'scammers', ['scammer_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'scammers_reports_media', type_='foreignkey')
    op.drop_column('scammers_reports_media', 'scammer_id')
    # ### end Alembic commands ###
