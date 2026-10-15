from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "8ddb94fd9b48"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "challenges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("reward", sa.Integer(), nullable=False),
        sa.Column("flag_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_challenges_id"), "challenges", ["id"], unique=False)
    op.create_table(
        "indexed_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tx_hash", sa.String(length=66), nullable=False),
        sa.Column("block_number", sa.BigInteger(), nullable=False),
        sa.Column("log_index", sa.Integer(), nullable=False),
        sa.Column("event_name", sa.String(length=50), nullable=False),
        sa.Column("player_address", sa.String(length=42), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("reward", sa.Integer(), nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_indexed_events_block_number"),
        "indexed_events",
        ["block_number"],
        unique=False,
    )
    op.create_index(
        op.f("ix_indexed_events_challenge_id"),
        "indexed_events",
        ["challenge_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_indexed_events_id"), "indexed_events", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_indexed_events_player_address"),
        "indexed_events",
        ["player_address"],
        unique=False,
    )
    op.create_index(
        op.f("ix_indexed_events_tx_hash"), "indexed_events", ["tx_hash"], unique=True
    )
    op.create_table(
        "players",
        sa.Column("wallet_address", sa.String(length=42), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=True),
        sa.Column("auth_nonce", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("wallet_address"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(
        op.f("ix_players_wallet_address"), "players", ["wallet_address"], unique=False
    )
    op.create_table(
        "authorizations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("player_address", sa.String(length=42), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("nonce", sa.Integer(), nullable=False),
        sa.Column("deadline", sa.Integer(), nullable=False),
        sa.Column("signature", sa.String(length=132), nullable=False),
        sa.Column("is_claimed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["challenge_id"],
            ["challenges.id"],
        ),
        sa.ForeignKeyConstraint(
            ["player_address"],
            ["players.wallet_address"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "player_address", "challenge_id", name="uq_player_challenge_auth"
        ),
        sa.UniqueConstraint("player_address", "nonce", name="uq_player_nonce"),
    )
    op.create_index(
        op.f("ix_authorizations_challenge_id"),
        "authorizations",
        ["challenge_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_authorizations_id"), "authorizations", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_authorizations_player_address"),
        "authorizations",
        ["player_address"],
        unique=False,
    )
    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("player_address", sa.String(length=42), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["challenge_id"],
            ["challenges.id"],
        ),
        sa.ForeignKeyConstraint(
            ["player_address"],
            ["players.wallet_address"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_submissions_challenge_id"),
        "submissions",
        ["challenge_id"],
        unique=False,
    )
    op.create_index(op.f("ix_submissions_id"), "submissions", ["id"], unique=False)
    op.create_index(
        op.f("ix_submissions_player_address"),
        "submissions",
        ["player_address"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_submissions_player_address"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_id"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_challenge_id"), table_name="submissions")
    op.drop_table("submissions")
    op.drop_index(op.f("ix_authorizations_player_address"), table_name="authorizations")
    op.drop_index(op.f("ix_authorizations_id"), table_name="authorizations")
    op.drop_index(op.f("ix_authorizations_challenge_id"), table_name="authorizations")
    op.drop_table("authorizations")
    op.drop_index(op.f("ix_players_wallet_address"), table_name="players")
    op.drop_table("players")
    op.drop_index(op.f("ix_indexed_events_tx_hash"), table_name="indexed_events")
    op.drop_index(op.f("ix_indexed_events_player_address"), table_name="indexed_events")
    op.drop_index(op.f("ix_indexed_events_id"), table_name="indexed_events")
    op.drop_index(op.f("ix_indexed_events_challenge_id"), table_name="indexed_events")
    op.drop_index(op.f("ix_indexed_events_block_number"), table_name="indexed_events")
    op.drop_table("indexed_events")
    op.drop_index(op.f("ix_challenges_id"), table_name="challenges")
    op.drop_table("challenges")
