"""add_performance_and_career_constraints

Revision ID: 62f0a79eaa45
Revises: ace91d80022d
Create Date: 2026-11-26 21:49:05.984508

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62f0a79eaa45'
down_revision: Union[str, Sequence[str], None] = 'ace91d80022d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema safely on both fresh and existing historical databases."""
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # 1. career_recommendations
    uqs = [u['name'] for u in insp.get_unique_constraints('career_recommendations')]
    if 'uq_user_career_recommendation' not in uqs:
        try:
            bind.execute(sa.text("DELETE FROM career_recommendations WHERE id NOT IN (SELECT MIN(id) FROM career_recommendations GROUP BY user_id, career_role_id)"))
        except Exception:
            pass
        with op.batch_alter_table('career_recommendations', schema=None) as batch_op:
            batch_op.create_unique_constraint('uq_user_career_recommendation', ['user_id', 'career_role_id'])

    # 2. career_skill_requirements
    uqs = [u['name'] for u in insp.get_unique_constraints('career_skill_requirements')]
    if 'uq_career_role_skill_req' not in uqs:
        try:
            bind.execute(sa.text("DELETE FROM career_skill_requirements WHERE id NOT IN (SELECT MIN(id) FROM career_skill_requirements GROUP BY career_role_id, skill_id)"))
        except Exception:
            pass
        with op.batch_alter_table('career_skill_requirements', schema=None) as batch_op:
            batch_op.create_unique_constraint('uq_career_role_skill_req', ['career_role_id', 'skill_id'])

    # 3. questions
    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.alter_column('question_type',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=50),
               existing_nullable=True)

    # 4. quizzes
    with op.batch_alter_table('quizzes', schema=None) as batch_op:
        if bind.engine.name != 'sqlite':
            batch_op.drop_constraint('fk_quizzes_note_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_quizzes_note_id', 'notes', ['note_id'], ['id'], ondelete='SET NULL')

    # 5. roadmap_milestones
    rm_cols = [c['name'] for c in insp.get_columns('roadmap_milestones')]
    with op.batch_alter_table('roadmap_milestones', schema=None) as batch_op:
        if 'stage' in rm_cols:
            batch_op.drop_column('stage')
        if 'recommended_resources_json' in rm_cols:
            batch_op.drop_column('recommended_resources_json')

    # 6. skill_gaps
    uqs = [u['name'] for u in insp.get_unique_constraints('skill_gaps')]
    if 'uq_user_career_skill_gap' not in uqs:
        try:
            bind.execute(sa.text("DELETE FROM skill_gaps WHERE id NOT IN (SELECT MIN(id) FROM skill_gaps GROUP BY user_id, career_role_id, skill_id)"))
        except Exception:
            pass
        with op.batch_alter_table('skill_gaps', schema=None) as batch_op:
            batch_op.create_unique_constraint('uq_user_career_skill_gap', ['user_id', 'career_role_id', 'skill_id'])

    # 7. subject_skill_mappings
    ssm_cols = [c['name'] for c in insp.get_columns('subject_skill_mappings')]
    with op.batch_alter_table('subject_skill_mappings', schema=None) as batch_op:
        if 'real_world_application' in ssm_cols:
            batch_op.drop_column('real_world_application')
        if 'project_example' in ssm_cols:
            batch_op.drop_column('project_example')

    # 8. topic_performances
    uqs = [u['name'] for u in insp.get_unique_constraints('topic_performances')]
    if 'uq_user_topic_performance' not in uqs:
        try:
            bind.execute(sa.text("DELETE FROM topic_performances WHERE id NOT IN (SELECT MIN(id) FROM topic_performances GROUP BY user_id, topic_id)"))
        except Exception:
            pass
        with op.batch_alter_table('topic_performances', schema=None) as batch_op:
            batch_op.create_unique_constraint('uq_user_topic_performance', ['user_id', 'topic_id'])

    # 9. user_skills
    uqs = [u['name'] for u in insp.get_unique_constraints('user_skills')]
    if 'uq_user_skill' not in uqs:
        try:
            bind.execute(sa.text("DELETE FROM user_skills WHERE id NOT IN (SELECT MIN(id) FROM user_skills GROUP BY user_id, skill_id)"))
        except Exception:
            pass
        with op.batch_alter_table('user_skills', schema=None) as batch_op:
            batch_op.create_unique_constraint('uq_user_skill', ['user_id', 'skill_id'])


def downgrade() -> None:
    """Downgrade schema safely."""
    bind = op.get_bind()
    insp = sa.inspect(bind)

    with op.batch_alter_table('user_skills', schema=None) as batch_op:
        uqs = [u['name'] for u in insp.get_unique_constraints('user_skills')]
        if 'uq_user_skill' in uqs:
            batch_op.drop_constraint('uq_user_skill', type_='unique')

    with op.batch_alter_table('topic_performances', schema=None) as batch_op:
        uqs = [u['name'] for u in insp.get_unique_constraints('topic_performances')]
        if 'uq_user_topic_performance' in uqs:
            batch_op.drop_constraint('uq_user_topic_performance', type_='unique')

    ssm_cols = [c['name'] for c in insp.get_columns('subject_skill_mappings')]
    with op.batch_alter_table('subject_skill_mappings', schema=None) as batch_op:
        if 'project_example' not in ssm_cols:
            batch_op.add_column(sa.Column('project_example', sa.TEXT(), nullable=True))
        if 'real_world_application' not in ssm_cols:
            batch_op.add_column(sa.Column('real_world_application', sa.TEXT(), nullable=True))

    with op.batch_alter_table('skill_gaps', schema=None) as batch_op:
        uqs = [u['name'] for u in insp.get_unique_constraints('skill_gaps')]
        if 'uq_user_career_skill_gap' in uqs:
            batch_op.drop_constraint('uq_user_career_skill_gap', type_='unique')

    rm_cols = [c['name'] for c in insp.get_columns('roadmap_milestones')]
    with op.batch_alter_table('roadmap_milestones', schema=None) as batch_op:
        if 'recommended_resources_json' not in rm_cols:
            batch_op.add_column(sa.Column('recommended_resources_json', sa.TEXT(), nullable=True))
        if 'stage' not in rm_cols:
            batch_op.add_column(sa.Column('stage', sa.VARCHAR(length=50), server_default=sa.text("'Beginner'"), nullable=True))

    with op.batch_alter_table('quizzes', schema=None) as batch_op:
        if bind.engine.name != 'sqlite':
            batch_op.drop_constraint('fk_quizzes_note_id', type_='foreignkey')
            batch_op.create_foreign_key('fk_quizzes_note_id', 'notes', ['note_id'], ['id'])

    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.alter_column('question_type',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)

    with op.batch_alter_table('career_skill_requirements', schema=None) as batch_op:
        uqs = [u['name'] for u in insp.get_unique_constraints('career_skill_requirements')]
        if 'uq_career_role_skill_req' in uqs:
            batch_op.drop_constraint('uq_career_role_skill_req', type_='unique')

    with op.batch_alter_table('career_recommendations', schema=None) as batch_op:
        uqs = [u['name'] for u in insp.get_unique_constraints('career_recommendations')]
        if 'uq_user_career_recommendation' in uqs:
            batch_op.drop_constraint('uq_user_career_recommendation', type_='unique')
