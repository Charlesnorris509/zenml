"""Simplify model version links [ec6307720f92].

Revision ID: ec6307720f92
Revises: 0.70.0
Create Date: 2024-11-06 16:16:43.344569

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ec6307720f92"
down_revision = "0.70.0"
branch_labels = None
depends_on = None


def _migrate_artifact_type() -> None:
    """Migrate the artifact type."""
    meta = sa.MetaData()
    meta.reflect(
        bind=op.get_bind(),
        only=("artifact_version", "model_versions_artifacts"),
    )
    artifact_version_table = sa.Table("artifact_version", meta)
    model_versions_artifacts = sa.Table("model_versions_artifacts", meta)

    connection = op.get_bind()

    query = sa.select(
        model_versions_artifacts.c.artifact_version_id,
        model_versions_artifacts.c.is_model_artifact,
        model_versions_artifacts.c.is_deployment_artifact,
    )
    result = connection.execute(query)

    updated = set()
    updates = []
    for (
        artifact_version_id,
        is_model_artifact,
        is_deployment_artifact,
    ) in result:
        if artifact_version_id in updated:
            # If an artifact was a model artifact in one model version, and a
            # deployment artifact in another model version, we only update it
            # once.
            continue

        if is_model_artifact:
            updated.add(artifact_version_id)
            updates.append(
                {"id_": artifact_version_id, "type": "ModelArtifact"}
            )
        elif is_deployment_artifact:
            updated.add(artifact_version_id)
            updates.append(
                {"id_": artifact_version_id, "type": "ServiceArtifact"}
            )

    if updates:
        connection.execute(
            sa.update(artifact_version_table).where(
                artifact_version_table.c.id == sa.bindparam("id_")
            ),
            updates,
        )


def upgrade() -> None:
    """Upgrade database schema and/or data, creating a new revision."""
    # ### commands auto generated by Alembic - please adjust! ###

    _migrate_artifact_type()

    with op.batch_alter_table(
        "model_versions_artifacts", schema=None
    ) as batch_op:
        batch_op.drop_constraint(
            "fk_model_versions_artifacts_workspace_id_workspace",
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            "fk_model_versions_artifacts_user_id_user", type_="foreignkey"
        )
        batch_op.drop_constraint(
            "fk_model_versions_artifacts_model_id_model", type_="foreignkey"
        )
        batch_op.drop_column("user_id")
        batch_op.drop_column("model_id")
        batch_op.drop_column("is_deployment_artifact")
        batch_op.drop_column("workspace_id")
        batch_op.drop_column("is_model_artifact")

    with op.batch_alter_table("model_versions_runs", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_model_versions_runs_model_id_model", type_="foreignkey"
        )
        batch_op.drop_constraint(
            "fk_model_versions_runs_workspace_id_workspace", type_="foreignkey"
        )
        batch_op.drop_constraint(
            "fk_model_versions_runs_user_id_user", type_="foreignkey"
        )
        batch_op.drop_column("model_id")
        batch_op.drop_column("workspace_id")
        batch_op.drop_column("user_id")

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade database schema and/or data back to the previous revision.

    Raises:
        NotImplementedError: Downgrade is not supported for this migration.
    """
    raise NotImplementedError("Downgrade is not supported for this migration.")