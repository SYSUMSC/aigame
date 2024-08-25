# 路径说明
```
- app #python fastapi后端与admin(采用layuiadmin非前后端分离)
- frontend #用户端 前后端分离
```

# 格式化import
```
python -m isort .
```

fastcrud文档：https://igorbenav.github.io/fastcrud/

SQLModel文档：https://sqlmodel.fastapi.org.cn/

接口说明，返回json，有字段code 0正常，1异常,msg中文消息,data=数据（可能没有）,count数据总长度，是分页前的总长度（可能没有）

错误返回的http码仍是200，只是code变为1，msg为异常原因，禁止使用返回接口raise HTTPException(status_code=404, detail="错误")

后台对于一个表，通常有的操作有

- 新增，修改（传入id），根据ModelSchema字段进行添加

- 删除（传入id），批量删除（传入ids，`,`分割）

- 查询
    post参数根据ModelSearchSchema的字段进行查询，如果是int则=匹配，如果是str则like % %匹配
    get参数为page，limit

# 杂


在我电脑的conda上不知道为啥需要指定才能安装到特定环境的路径
```
pip install -r requirements.txt --target D:\ProgramData\miniconda3\envs\newaigame\Lib\site-packages
```
