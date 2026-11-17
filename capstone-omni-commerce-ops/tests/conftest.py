"""In-memory test fixtures."""

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

@pytest.fixture
def retail_session(engine):
    from omnicommerceops.seed_data import seed_baseline
    with Session(engine) as seeded_session:
        seed_baseline(seeded_session)
        yield seeded_session


@pytest.fixture
def cola_case(retail_session):
    from sqlmodel import select
    from omnicommerceops.database_models import RoundCase
    return retail_session.exec(
        select(RoundCase).where(RoundCase.product_key == "PROD_COLA", RoundCase.round_number == 1)
    ).one()


@pytest.fixture
def planned_round_one(retail_session):
    from sqlmodel import select
    from omnicommerceops.database_models import RoundCase
    from omnicommerceops.planning_service import record_demand_plan
    for round_case in retail_session.exec(select(RoundCase).where(RoundCase.round_number == 1)).all():
        record_demand_plan(retail_session, round_case.id, 60, 0, "Baseline exercise", "demand_planner")
    return retail_session


@pytest.fixture
def engine():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    return test_engine
