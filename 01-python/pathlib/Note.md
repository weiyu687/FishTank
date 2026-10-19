## pathlib
提供表示文件系统路径的类，语义适用于不同操作系统

|functions \ attribute|link|
|:-:|:-:|
|Path()|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.Path)|
|.exists()|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.Path.exists)|
|.is_file()|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.Path.is_file)|
|.is_dir()|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.Path.is_dir)|
|.mkdir()|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.Path.mkdir)|
|.read_text()|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.Path.read_text)|
|.write_text()|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.Path.write_text)|
|.iterdir()|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.Path.iterdir)|
|.resolve()|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.Path.resolve)|
|.joinpath()|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.PurePath.joinpath)|
|.rmdir()|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.Path.rmdir)|
|.parents|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.PurePath.parents)|
|.parent|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.PurePath.parent)|
|.glob()|[doc](https://docs.python.org/zh-cn/3.9/library/pathlib.html#pathlib.Path.glob)|

### Path()
以当前系统的路径风格表示路径

```python
Path('setup.py')    # 相对路径
Path(".") / ".env"
```

> '/'用于Linux系统,"\\"用于Windows系统

### .exists()
判断此路径是否指向一个已存在的文件或目录，
返回Bool类型

```python
Path('.').exists()
```

### .is_file()
如果文件指向一个常规文件（或指向常规文件的符号链接）则返回 True，指向其他类型的文件则返回 False。

当路径不存在或者是一个破损的符号链接时也会返回 False；其他错误（例如权限错误）被传播。

```python
Path('.').is_file()
```

### .is_dir()
如果文件指向一个目录（或指向目录的符号链接）则返回 True，指向其他类型的文件则返回 False。

当路径不存在或者是一个破损的符号链接时也会返回 False；其他错误（例如权限错误）被传播。

```python
Path('.').is_dir()
```

### .mkdir()
创建目录。

Path.mkdir(mode=0o777, parents=False, exist_ok=False)

```python
Path('./test').mkdir()
```

如果*parents*为False，那么不考虑指定目录的父级目录，若目录不存在则创建该文件夹，若父级目录不存在则抛出FileNotFoundError。

如果*parents*为True，那么不存在的父级目录会被创建。

如果*exist_ok*为False，即目录存在不被允许，那么当指定目录已经存在时会抛出FileExistsError。如果*exist_ok*True，那么允许指定的目录已经存在。

### .read_text()
以字符串形式返回路径指向的文件的解码后文本内容。

### .write_text()
将文件以文本模式打开，写入 data 并关闭。

二者仅支持**text file**，比如：.txt、.md、.py、.json、.env、.csv、.ipynb等。
不支持其他类型文件，比如二进制文件，例如：.png/.jpg、.pdf、.zip、.pkl、.exe等。


```python
p = Path('my_text_file')
p.write_text('Text file contents', encoding="utf-8")
p.read_text(encoding="utf-8")
# 'Text file contents'
```

### .iterdir()
当路径指向一个目录时，产生该路径下的对象的路径，
返回类型是**迭代器generator**。

```python
p = Path('docs')
for child in p.iterdir():
    print(child)
# PosixPath('docs/conf.py')
# PosixPath('docs/_templates')
# PosixPath('docs/make.bat')
# PosixPath('docs/index.rst')
```

### .resolve()
将路径绝对化，解析任何符号链接。返回新的路径对象。

```python
p = Path('./')
p.resolve()
```

### .joinpath()
路径拼接。

```python
# 两种等价语法
Path('/etc').joinpath('init.d', 'apache2')

Path('/etc') / "init.d" / "apache2"
# '/etc/init.d/apache2'
```

### .rmdir()
移除此目录。此目录必须为空。

### .parents
提供访问此路径的逻辑祖先的不可变序列。返回类型是序列对象。
generator仅能遍历一次，比如使用for进行遍历，
序列对象可以多次下标访问，二者分别具有动态属性和静态属性。

```python
p = Path('c:/foo/bar/setup.py')

print(p.parents[0])
# Path('c:/foo/bar')

print(p.parents[1])
# Path('c:/foo')

print(p.parents[2])
# Path('c:/')
```

迭代器下标越小路径越接近输入路径。

### .parent
此路径的逻辑父路径。

```python
p = Path('/a/b/c/d')

print(p.parent)
# Path('/a/b/c')
```

### .glob()
解析相对于此路径的通配符 pattern，产生所有匹配的文件。返回类型是generator。




