"""added unique constraints

Revision ID: dded3119c1fe
Revises: 0341b154f79a
Create Date: 2023-10-04 14:29:26.688065

"""
from dataclasses import dataclass
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Session

import mealie.db.migration_types
from alembic import op
from mealie.db.models._model_base import SqlAlchemyBase

# revision identifiers, used by Alembic.
revision = "dded3119c1fe"
down_revision = "0341b154f79a"
branch_labels = None
depends_on = None


@dataclass
class TableMeta:
    tablename: str
    pk_1: str
    pk_2: str

    @classmethod
    def composite_pk(self, pk_1_val: Any, pk_2_val: Any) -> str:
        return "$$".join([pk_1_val, pk_2_val])


def _is_postgres():
    return op.get_context().dialect.name == "postgresql"


def _remove_duplicates_from_m2m_table(session: Session, table_meta: TableMeta):
    if _is_postgres():
        default_pk = "CTID"
    else:
        default_pk = "ROWID"

    # some of these tables are missing defined unique pks, so we have to rely on the database default pk
    query = sa.text(
        f"""
        DELETE FROM {table_meta.tablename}
        WHERE EXISTS (
            SELECT 1 FROM {table_meta.tablename} t2
            WHERE {table_meta.tablename}.{table_meta.pk_1} = t2.{table_meta.pk_1}
            AND {table_meta.tablename}.{table_meta.pk_2} = t2.{table_meta.pk_2}
            AND {table_meta.tablename}.{default_pk} > t2.{default_pk}
        )
        """
    )

    session.execute(query)
    session.commit()


def _remove_duplicates_from_m2m_tables(table_metas: list[TableMeta]):
    bind = op.get_bind()
    session = Session(bind=bind)

    for table_meta in table_metas:
        _remove_duplicates_from_m2m_table(session, table_meta)


def upgrade():
    _remove_duplicates_from_m2m_tables(
        [
            # M2M
            TableMeta("cookbooks_to_categories", "cookbook_id", "category_id"),
            TableMeta("cookbooks_to_tags", "cookbook_id", "tag_id"),
            TableMeta("cookbooks_to_tools", "cookbook_id", "tool_id"),
            TableMeta("group_to_categories", "group_id", "category_id"),
            TableMeta("plan_rules_to_categories", "group_plan_rule_id", "category_id"),
            TableMeta("plan_rules_to_tags", "plan_rule_id", "tag_id"),
            TableMeta("recipes_to_categories", "recipe_id", "category_id"),
            TableMeta("recipes_to_tags", "recipe_id", "tag_id"),
            TableMeta("recipes_to_tools", "recipe_id", "tool_id"),
            TableMeta("users_to_favorites", "user_id", "recipe_id"),
            TableMeta("shopping_lists_multi_purpose_labels", "shopping_list_id", "label_id"),
            # Foods/Units/Labels
            TableMeta("ingredient_foods", "name", "group_id"),
            TableMeta("ingredient_units", "name", "group_id"),
            TableMeta("multi_purpose_labels", "name", "group_id"),
        ]
    )

    # ### commands auto generated by Alembic - please adjust! ###
    # we use batch_alter_table here because otherwise this fails on sqlite

    # M2M
    with op.batch_alter_table("cookbooks_to_categories") as batch_op:
        batch_op.create_unique_constraint("cookbook_id_category_id_key", ["cookbook_id", "category_id"])

    with op.batch_alter_table("cookbooks_to_tags") as batch_op:
        batch_op.create_unique_constraint("cookbook_id_tag_id_key", ["cookbook_id", "tag_id"])

    with op.batch_alter_table("cookbooks_to_tools") as batch_op:
        batch_op.create_unique_constraint("cookbook_id_tool_id_key", ["cookbook_id", "tool_id"])

    with op.batch_alter_table("group_to_categories") as batch_op:
        batch_op.create_unique_constraint("group_id_category_id_key", ["group_id", "category_id"])

    with op.batch_alter_table("plan_rules_to_categories") as batch_op:
        batch_op.create_unique_constraint("group_plan_rule_id_category_id_key", ["group_plan_rule_id", "category_id"])

    with op.batch_alter_table("plan_rules_to_tags") as batch_op:
        batch_op.create_unique_constraint("plan_rule_id_tag_id_key", ["plan_rule_id", "tag_id"])

    with op.batch_alter_table("recipes_to_categories") as batch_op:
        batch_op.create_unique_constraint("recipe_id_category_id_key", ["recipe_id", "category_id"])

    with op.batch_alter_table("recipes_to_tags") as batch_op:
        batch_op.create_unique_constraint("recipe_id_tag_id_key", ["recipe_id", "tag_id"])

    with op.batch_alter_table("recipes_to_tools") as batch_op:
        batch_op.create_unique_constraint("recipe_id_tool_id_key", ["recipe_id", "tool_id"])

    with op.batch_alter_table("users_to_favorites") as batch_op:
        batch_op.create_unique_constraint("user_id_recipe_id_key", ["user_id", "recipe_id"])

    with op.batch_alter_table("shopping_lists_multi_purpose_labels") as batch_op:
        batch_op.create_unique_constraint("shopping_list_id_label_id_key", ["shopping_list_id", "label_id"])

    # Foods/Units/Labels
    with op.batch_alter_table("ingredient_foods") as batch_op:
        batch_op.create_unique_constraint("ingredient_foods_name_group_id_key", ["name", "group_id"])

    with op.batch_alter_table("ingredient_units") as batch_op:
        batch_op.create_unique_constraint("ingredient_units_name_group_id_key", ["name", "group_id"])

    with op.batch_alter_table("multi_purpose_labels") as batch_op:
        batch_op.create_unique_constraint("multi_purpose_labels_name_group_id_key", ["name", "group_id"])

    op.create_index(
        op.f("ix_shopping_lists_multi_purpose_labels_created_at"),
        "shopping_lists_multi_purpose_labels",
        ["created_at"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    # M2M
    op.drop_constraint("user_id_recipe_id_key", "users_to_favorites", type_="unique")
    op.drop_index(
        op.f("ix_shopping_lists_multi_purpose_labels_created_at"), table_name="shopping_lists_multi_purpose_labels"
    )
    op.drop_constraint("recipe_id_tool_id_key", "recipes_to_tools", type_="unique")
    op.drop_constraint("recipe_id_tag_id_key", "recipes_to_tags", type_="unique")
    op.drop_constraint("recipe_id_category_id_key", "recipes_to_categories", type_="unique")
    op.drop_constraint("plan_rule_id_tag_id_key", "plan_rules_to_tags", type_="unique")
    op.drop_constraint("group_plan_rule_id_category_id_key", "plan_rules_to_categories", type_="unique")
    op.drop_constraint("group_id_category_id_key", "group_to_categories", type_="unique")
    op.drop_constraint("cookbook_id_tool_id_key", "cookbooks_to_tools", type_="unique")
    op.drop_constraint("cookbook_id_tag_id_key", "cookbooks_to_tags", type_="unique")
    op.drop_constraint("cookbook_id_category_id_key", "cookbooks_to_categories", type_="unique")
    op.drop_constraint("shopping_list_id_label_id_key", "shopping_lists_multi_purpose_labels", type_="unique")

    # Foods/Units/Labels
    op.drop_constraint("multi_purpose_labels_name_group_id_key", "multi_purpose_labels", type_="unique")
    op.drop_constraint("ingredient_units_name_group_id_key", "ingredient_units", type_="unique")
    op.drop_constraint("ingredient_foods_name_group_id_key", "ingredient_foods", type_="unique")
    # ### end Alembic commands ###
