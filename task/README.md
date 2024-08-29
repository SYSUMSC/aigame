# 赛题模板文档

赛题模板已给出，详情参考路径 [task/task-template](task-template)。

样例赛题已给出，详情参考路径 [task/task-0](task-0)。

其中，相关文件及文件夹解释如下：

- **task.md**：赛题信息文件，用于展示并介绍赛题内容。
- **rank.py**：赛题评分脚本，出题人必须实现 `cal_score() -> float` 函数。
- **asset/**：赛题静态资源存放处，比如 `task.md` 涉及到的图片等文件。
- **task-dataset**：赛题训练数据，具体组织形式出题人发挥。
- **test-dataset**：赛题评测数据，具体组织形式出题人发挥。
- **test-labels**：赛题评测标准，具体组织形式出题人发挥。
- **answer.json**：参赛者提交的评测内容。
- **example.json**：赛题提供的评测内容参考格式。
