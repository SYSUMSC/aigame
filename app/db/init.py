from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.schemas.user import User
from app.schemas.team import Team
from app.schemas.problem_type import ProblemType
from app.schemas.problem import Problem
from app.schemas.competition import Competition
from app.schemas.config import Config
from app.core.security import get_password_hash
from datetime import datetime, timedelta, timezone

# 生成一些固定的测试比赛，题目分类，题目，初始用户用于测试
async def init_test_data(session: AsyncSession):
    # 检查是否已经有数据存在
    existing_user = await session.execute(select(User).where(User.username == "admin"))
    if existing_user.first():
        print("Test data already exists.")
        return

    # 生成测试用户
    test_user = User(
        username="admin",
        email="test_user@example.com",
        name="Test User",
        student_id="20220001",
        password=get_password_hash("123456"),
        is_active=True
    )
    session.add(test_user)

    # 生成测试团队
    test_team = Team(
        name="Test Team",
        captain_id=None,  # 稍后在数据库提交后，设置队长为test_user
        status="active",
        invite_code="INV123"
    )
    session.add(test_team)

    # 生成题目分类
    problem_type1 = ProblemType(
        name="Math",
        description="Mathematics problems"
    )
    problem_type2 = ProblemType(
        name="Programming",
        description="Programming challenges"
    )
    session.add_all([problem_type1, problem_type2])

    # 生成比赛
    test_competition = Competition(
        name="Test Competition",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc) + timedelta(days=7),
        status=1,
        description="A competition for testing purposes."
    )
    session.add(test_competition)

    # 生成题目
    test_problem1 = Problem(
        name="Math Problem 1",
        problem_type_id=1,  # Math
        content="Solve this equation: 2x + 3 = 7",
        score=10,
        difficulty=1,
        port=8080,
        status=1,
        competition_id=1
    )

    test_problem2 = Problem(
        name="Programming Problem 1",
        problem_type_id=2,  # Programming
        content="Write a program that prints 'Hello, World!'",
        score=20,
        difficulty=1,
        port=8081,
        status=1,
        competition_id=1
    )

    session.add_all([test_problem1, test_problem2])

    # 提交并获取ID，设置队长为test_user
    await session.commit()
    test_team.captain_id = test_user.id
    await session.commit()

    print("Test data generated successfully.")
