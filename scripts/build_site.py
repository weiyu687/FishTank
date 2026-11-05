"""Build the knowledge library without executing notebook code."""
from pathlib import Path
import html
import json
import shutil
import os
import re
import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
GROUPS = [('01-python', 'Python', '常用标准库与 NumPy 数组计算'), ('02-langchain', 'LangChain', 'Deep Agents、工具扩展与记忆实验'), ('03-machinelearning', '机器学习', 'PyTorch 教程、强化学习与生成模型'), ('04-agent-interview', 'Agent 开发面试', '原理、RAG、记忆、工程可靠性与系统设计')]

def write_page(path, title, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    base = os.path.relpath(DOCS, path.parent).replace('\\', '/')
    path.write_text(f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · FishTank</title>
<link rel="stylesheet" href="{base}/assets/library.css">
<script>window.MathJax={{tex:{{inlineMath:[['$','$'],['\\\\(','\\\\)']]}}}};</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script></head>
<body><header><a href="{base}/index.html">🐟 FishTank</a><nav><a href="{base}/01-python/index.html">Python</a><a href="{base}/02-langchain/index.html">LangChain</a><a href="{base}/03-machinelearning/index.html">机器学习</a><a href="{base}/04-agent-interview/index.html">Agent 面试</a></nav></header>
<main><h1>{html.escape(title)}</h1>{body}</main><footer>FishTank · 学习、实验与持续积累</footer></body></html>''', encoding='utf-8')

def render(text):
    return markdown.markdown(text, extensions=['fenced_code', 'tables', 'toc', 'md_in_html'])

def main():
    cards = []
    count = 0
    for folder, label, description in GROUPS:
        items = []
        for source in sorted((ROOT / folder).rglob('*')):
            if not source.is_file() or 'generative-models' in source.parts or '__pycache__' in source.parts:
                continue
            relative = source.relative_to(ROOT)
            target = DOCS / relative
            if source.suffix not in ('.md', '.ipynb'):
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                continue
            text = source.read_text(encoding='utf-8')
            title = str(source.relative_to(ROOT / folder)).replace('\\', ' / ')
            if source.suffix == '.md':
                match = re.search(r'^#+\s+(.+)', text, re.M)
                if match:
                    title = match.group(1)
                text = re.sub(r'(\]\([^):]+)\.(md|ipynb)([)#])', r'\1.html\3', text)
                body = render(text)
            else:
                notebook = json.loads(text)
                parts = ['<p class="intro">实验笔记 · 代码仅展示，浏览页面不会执行。</p>']
                for cell in notebook.get('cells', []):
                    content = ''.join(cell.get('source', []))
                    parts.append(render(content) if cell['cell_type'] == 'markdown' else '<pre><code>' + html.escape(content) + '</code></pre>')
                    for output in cell.get('outputs', []):
                        plain = output.get('text', output.get('data', {}).get('text/plain', []))
                        if plain:
                            parts.append('<pre class="output">' + html.escape(''.join(plain)) + '</pre>')
                        png = output.get('data', {}).get('image/png')
                        if png:
                            parts.append('<img alt="实验输出" src="data:image/png;base64,' + ''.join(png) + '">')
                body = '\n'.join(parts)
            target = target.with_suffix('.html')
            source_url = 'https://github.com/weiyu687/FishTank/blob/main/' + relative.as_posix()
            write_page(target, title, '<p><a href="' + source_url + '">查看源文件</a></p>' + body)
            items.append(f'<li><a href="{target.relative_to(DOCS / folder).as_posix()}">{html.escape(title)}</a><small>{html.escape(str(source.relative_to(ROOT / folder)))}</small></li>')
            count += 1
        if folder == '03-machinelearning':
            items.append('<li><a href="../generative-models/index.html">生成模型数学基础</a><small>概率 → VAE → Diffusion → Flow Matching · 八章完整课程</small></li>')
        write_page(DOCS / folder / 'index.html', label, f'<p class="intro">{description}</p><ul class="entries">' + ''.join(items) + '</ul>')
        cards.append(f'<a class="card" href="{folder}/index.html"><h2>{label}</h2><p>{description}</p><span>{len(items)} 个学习入口 →</span></a>')
    write_page(DOCS / 'index.html', '在知识的海洋里，持续探索。', '<p class="intro">FishTank 个人知识库 · 从 Python 基础到智能体，再到机器学习理论与实验。</p><div class="grid">' + ''.join(cards) + '</div><section><h2>学习路线</h2><p>Python 语言与工具 → LangChain 应用实践 → 强化学习基础与实验 / 生成模型数学基础</p><p>各章节收录原始笔记和实验代码，可通过“查看源文件”继续阅读或下载。</p></section>')
    (DOCS / '.nojekyll').touch()
    print(f'Published {count} notes and notebooks; preserved generative-models pages.')

if __name__ == '__main__':
    main()
