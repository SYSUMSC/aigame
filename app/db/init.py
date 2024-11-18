from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.schemas.user import User
from app.schemas.team import Team
from app.schemas.problem_type import ProblemType
from app.schemas.problem import Problem
from app.schemas.competition import Competition
from app.schemas.announcement import Announcement
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
    test_user2 = User(
        username="test",
        email="test_user2@example.com",
        name="Test User 2",
        student_id="20220002",
        password=get_password_hash("123456"),
        is_active=True
    )
    session.add(test_user2)

    # 生成测试团队
    test_team = Team(
        name="Test Team 1",
        captain_id=None,  # 稍后在数据库提交后，设置队长为test_user
        status="active",
        invite_code="INV1"
    )
    session.add(test_team)
    test_team2 = Team(
        name="Test Team 2",
        captain_id=None,  # 稍后在数据库提交后，设置队长为test_user
        status="active",
        invite_code="INV2"
    )
    session.add(test_team2)

    # 生成题目分类
    problem_type1 = ProblemType(
        name="AI Programming",
        description="Programming problems related to Artificial Intelligence"
    )
    session.add(problem_type1)

    # 生成比赛
    test_competition = Competition(
        name="AI Programming Competition",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc) + timedelta(days=7),
        status=1,
        description="A competition for testing AI programming problems."
    )
    session.add(test_competition)

    # 生成题目
    ai_problems = [
        # 难度1：旅行
        Problem(
            name="决策树分类器实现",
            problem_type_id=1,  # AI Programming
            content="使用Python实现一个简单的决策树分类器，并使用鸢尾花数据集进行测试。",
            score=10,
            difficulty=1,
            port=8080,
            status=1,
            competition_id=1
        ),
        Problem(
            name="K近邻分类器实现",
            problem_type_id=1,  # AI Programming
            content="使用Python实现一个简单的K近邻（KNN）分类器，并使用鸢尾花数据集进行测试。",
            score=10,
            difficulty=1,
            port=8081,
            status=1,
            competition_id=1
        ),
        # 难度2：经典
        Problem(
            name="多层感知机神经网络实现",
            problem_type_id=1,  # AI Programming
            content="使用Python实现一个多层感知机（MLP）神经网络，并使用MNIST手写数字数据集进行训练和测试。",
            score=20,
            difficulty=2,
            port=8082,
            status=1,
            competition_id=1
        ),
        Problem(
            name="支持向量机分类器实现",
            problem_type_id=1,  # AI Programming
            content="使用Python实现一个支持向量机（SVM）分类器，并使用乳腺癌数据集进行测试。",
            score=20,
            difficulty=2,
            port=8083,
            status=1,
            competition_id=1
        ),
        # 难度3：专家
        Problem(
            name="卷积神经网络实现",
            problem_type_id=1,  # AI Programming
            content="使用Python实现一个卷积神经网络（CNN），并使用CIFAR-10图像数据集进行训练和测试。",
            score=30,
            difficulty=3,
            port=8084,
            status=1,
            competition_id=1
        ),
        Problem(
            name="递归神经网络实现",
            problem_type_id=1,  # AI Programming
            content="使用Python实现一个递归神经网络（RNN），并使用IMDB电影评论数据集进行情感分析。",
            score=30,
            difficulty=3,
            port=8085,
            status=1,
            competition_id=1
        )
    ]
    session.add_all(ai_problems)
    # 提交并获取ID，设置队长为test_user
    await session.commit()

    # 再次查询提交后的用户和团队数据，设置队长ID
    updated_user = await session.execute(select(User).where(User.username == "admin"))
    test_user = updated_user.scalar_one()

    updated_user2 = await session.execute(select(User).where(User.username == "test"))
    test_user2 = updated_user2.scalar_one()

    # 查询提交后的 team 数据，确保获取正确的 team id
    updated_team = await session.execute(select(Team).where(Team.name == "Test Team 1"))
    test_team = updated_team.scalar_one()

    updated_team2 = await session.execute(select(Team).where(Team.name == "Test Team 2"))
    test_team2 = updated_team2.scalar_one()

    # 设置队长ID
    test_team.captain_id = test_user.id
    test_team2.captain_id = test_user2.id
    test_user.team_id = test_team.id
    test_user2.team_id = test_team2.id
    await session.commit()

    # 生成公告
    test_announcements = [
        Announcement(
            id=1,
            title="Welcome to AI Programming Competition",
            content="(USTC 校内) 参加 Hackergame 2024 的同学可以在「青春科大」平台报名获取学时。\n 只要完成签到题目（50 分） 即可获取 2.0 二课学时；其他分数（100，200，400，600，800，1000）的学时需要额外提交解答文档（writeup） 到 sec-class@ustclug.org ，详见二课平台各子项目通知。\n（子项目可重复报名，例如 1000 分+ 的选手可以报名所有子项目，并获取全部 24 个二课学时）\n题解提交截止时间：11.09 12:00 二课报名截止时间：11.16 12:00",
            date="2024-11-09 12:00:00"
        )
    ]
    session.add(test_announcements)
    await session.commit()

    print("Test data generated successfully.")
