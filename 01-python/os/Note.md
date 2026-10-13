## os
提供与操作系统相关的功能

|functions \ attribute|link|
|:-:|:-:|
|os.getenv()|[doc](https://docs.python.org/zh-cn/3.9/library/os.html#os.getenv)|
|os.environ|[doc](https://docs.python.org/zh-cn/3.9/library/os.html#os.environ)|

### os.getenv()
获取环境变量

```python
api_key = os.getenv("MODEL_API_KEY")
```

### os.environ
环境变量字典，可以读、临时写环境变量

```python
os.environ["MODEL_API_KEY"] = "sk-..."
```

> os.getenv("key")与os.environ["key"]相比,
更推荐使用os.getenv("key")，
因为os.getenv("key")若key不存在返回None,
而os.environ["key"]若key不存在会抛出KeyError，适合强制校验

由于**Python3.4+**推荐**pathlib**,
所以关于os.path的相关内容不再记录,
相关操作详见pathlib

