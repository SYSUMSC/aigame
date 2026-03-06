# 出题与打包方法

## 适用范围

本文档面向出题人、评测脚本维护者、赛事运营同学，说明如何在 `evaluate_example/` 下创建题目、打包上传并完成本地自测。

更完整的样例与细节，可继续看：`evaluate_example/README.md`

## 推荐目录结构

在 `evaluate_example/` 下新建一个英文目录名的题目文件夹：

```text
evaluate_example/
  task_name/
    judge/
    data/
    test_submit/
    problem.yml
    desc.md
```

含义：

- `judge/`：评测脚本与隐藏评测资源
- `data/`：给选手下载的数据集，可选
- `test_submit/`：示例提交
- `problem.yml`：题目元信息
- `desc.md`：详细题面

## 出题建议

### 类型一：结果上传类

适合训练耗时长、线上不适合跑完整训练的题目。

推荐方式：

- 选手线下训练
- 线上上传 `csv` / `json` 结果文件
- `judge.py` 读取结果并和参考答案对比打分

这类题目通常更稳定，也更适合比赛大规模并发。

### 类型二：代码执行类

适合单次运行很快、资源边界明确的题目。

推荐方式：

- 选手上传代码压缩包
- 评测端在沙箱内执行
- `judge.py` 校验结果并计算得分

这类题目要特别注意：

- 运行时长
- 依赖控制
- 资源上限
- 超时与异常输出

## `problem.yml` 建议字段

至少包含：

```yaml
title: "示例题目"
shortDescription: "一句话简介"
startTime: "2024-01-01T00:00:00Z"
endTime: "2024-01-31T23:59:59Z"
score: 100
```

建议：

- 时间使用 ISO8601
- 保证 `startTime < endTime`
- 详细题面写在 `desc.md`，不要塞回 YAML

## `judge.py` 建议

建议提供统一入口：

```python
def evaluate(submission_path: str, judge_data_path: str, python_executable_path: str | None = None) -> dict:
    return {"score": 100.0, "logs": "ok"}
```

建议遵循这些原则：

- 不依赖外网
- 不依赖运行时临时下载资源
- 日志清晰但不要过大
- 失败时返回便于定位的错误信息
- 对文件格式、字段缺失、非法值做显式校验

## 本地自测建议

### 直接调用 `judge.py`

```bash
cd /proj/aigame/evaluate_example/task_name
python - <<'PY'
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('judge', Path('judge')/'judge.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print(m.evaluate(submission_path='test_submit', judge_data_path='judge'))
PY
```

### 用评测服务联调

```bash
cd /proj/aigame/evaluateapp
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

然后再用：

```bash
python3 /proj/aigame/evaluate_example/test_evaluate.py --base-url http://127.0.0.1:8000
```

## 打包方法

推荐统一使用打包脚本：

```bash
cd /proj/aigame/evaluate_example
python3 pack.py task_name
```

或者批量：

```bash
cd /proj/aigame/evaluate_example
python3 pack.py --all --root .
```

打包后通常会得到：

- `judge.zip`
- `test_submit.zip`
- `data.zip`（可选）
- `task_name.zip`

## 后台上传建议

管理后台常见对应关系：

- 评测脚本：上传 `judge.zip`
- 示例提交：上传 `test_submit.zip`
- 数据集：上传 `data.zip`（如果有）
- 批量导入：上传最终的 `task_name.zip`

如果你是通过批量导入方式建题，建议优先上传最终总包，这样字段、题面和资源更不容易漏。

## 出题前自检清单

- `problem.yml` 字段完整
- `desc.md` 题面清晰
- `judge.py` 能在本地自测通过
- `test_submit/` 真的能跑通
- 结果上传格式与题面一致
- 资源文件都在包内，不依赖临时下载
- 用 `pack.py` 打出的最终包能被后台顺利识别

## 经验建议

- 能做成“结果上传类”的题，优先不要做成“在线训练类”。
- 如果一定要执行代码，尽量让输入输出协议简单、稳定、易复现。
- 先准备好一份最小样例提交，再写后台上传与联调流程，效率更高。
- 新题上线前，最好配一条最小 E2E 或至少跑一遍提交流程冒烟。
