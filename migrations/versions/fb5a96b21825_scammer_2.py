"""Scammer 2

Revision ID: fb5a96b21825
Revises: ce3ef94eb737
Create Date: 2023-11-30 09:01:26.220885

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb5a96b21825'
down_revision = 'ce3ef94eb737'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('scammers_reports_media_scammers_reports_id_fkey', 'scammers_reports_media', type_='foreignkey')
    op.create_foreign_key(None, 'scammers_reports_media', 'scammers_reports', ['scammers_reports_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'scammers_reports_media', type_='foreignkey')
    op.create_foreign_key('scammers_reports_media_scammers_reports_id_fkey', 'scammers_reports_media', 'scammers_reports', ['scammers_reports_id'], ['id'])
    # ### end Alembic commands ###
