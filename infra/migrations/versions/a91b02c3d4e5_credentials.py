"""Workspace-scoped encrypted credential references; additive, preserves existing data."""
from alembic import op
import sqlalchemy as sa
revision='a91b02c3d4e5'
down_revision='d701ca032ccb'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('credentials',sa.Column('id',sa.String(36),primary_key=True),sa.Column('workspace_id',sa.String(36),sa.ForeignKey('workspaces.id'),nullable=False),sa.Column('name',sa.String(120),nullable=False),sa.Column('ciphertext',sa.Text(),nullable=False),sa.Column('active',sa.Integer(),nullable=False),sa.Column('created_at',sa.String(),nullable=False))
    op.create_index('ix_credentials_workspace_id','credentials',['workspace_id'])

def downgrade():
    op.drop_index('ix_credentials_workspace_id',table_name='credentials')
    op.drop_table('credentials')
