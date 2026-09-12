from datetime import datetime, timezone

from diffwatch.daos.plan_dao import PlanDAO
from diffwatch.models.plan_model import Plan


def make_plan(name: str = "Test plan") -> Plan:
	return Plan(
		name=name,
		price_cents=990,
		max_active_monitors=5,
		min_check_freq_minutes=5,
		max_notifications_per_day=100,
		created_at=datetime.now(timezone.utc),
	)


def test_create_plan(db_conn):
	dao = PlanDAO(db_conn)
	plan_id = dao.create(make_plan(name="Create test plan"))

	assert plan_id is not None


def test_get_by_id(db_conn):
	dao = PlanDAO(db_conn)
	plan = make_plan(name="Get test plan")
	plan_id = dao.create(plan)

	result = dao.get_by_id(plan_id)

	assert result is not None
	assert result.id == plan_id
	assert result.name == plan.name
	
def test_get_by_id_returns_none_for_unknown_plan(db_conn):
	dao = PlanDAO(db_conn)

	result = dao.get_by_id(999)

	assert result is None


def test_get_all_returns_plans_ordered_by_id(db_conn):
	dao = PlanDAO(db_conn)
	first_id = dao.create(make_plan(name="List test plan 1"))
	second_id = dao.create(make_plan(name="List test plan 2"))

	results = dao.get_all()
	result_ids = {plan.id for plan in results}
	assert first_id in result_ids
	assert second_id in result_ids
