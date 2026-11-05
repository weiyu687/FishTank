"""Isolated file-memory probe. Online read/write require a configured model."""
import argparse
import os
import re
import uuid
from importlib.metadata import version
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['seed', 'read', 'write'], required=True)
    parser.add_argument('--user', required=True)
    parser.add_argument('--root', type=Path, default=Path.home() / '.fishtank-memory-lab')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,40}', args.user):
        parser.error('user must contain only letters, numbers, underscore or hyphen')
    root = args.root.expanduser().resolve() / args.user
    root.mkdir(parents=True, exist_ok=True)
    path = root / 'AGENTS.md'
    if args.mode == 'seed':
        marker = 'LAB-' + uuid.uuid4().hex
        path.write_text('# Experimental user memory\nPreferred marker: ' + marker + '\n', encoding='utf-8')
        print('Seeded:', path, '\nExpected marker:', marker)
        return
    from deepagents import create_deep_agent
    from deepagents.backends import FilesystemBackend
    from langgraph.checkpoint.memory import InMemorySaver
    for package in ['deepagents', 'langgraph']:
        print(package, version(package))
    model = os.environ.get('DEEPAGENT_MODEL')
    if not model:
        parser.error('Set DEEPAGENT_MODEL and the provider API key locally')
    if not path.exists():
        path.write_text('# Experimental user memory\nNo preference recorded.\n', encoding='utf-8')
    before = path.read_text(encoding='utf-8')
    prompt = 'What is my preferred marker? If it is unknown, say unknown. Do not invent one.'
    if args.mode == 'write':
        marker = 'LAB-' + uuid.uuid4().hex
        prompt = f'My new preferred marker is {marker}. Update /AGENTS.md, replacing the old preference. Preserve other notes.'
        print('Expected new marker:', marker)
    agent = create_deep_agent(
        model=model,
        backend=FilesystemBackend(root_dir=str(root), virtual_mode=True),
        memory=['/AGENTS.md'],
        checkpointer=InMemorySaver(),
        system_prompt='Use only this experimental user memory. Never invent missing preferences.',
    )
    result = agent.invoke(
        {'messages': [{'role': 'user', 'content': prompt}]},
        {'configurable': {'thread_id': uuid.uuid4().hex}, 'recursion_limit': 40},
    )
    for message in result['messages']:
        for call in getattr(message, 'tool_calls', []):
            print('Tool:', call['name'], call['args'])
    print('Answer:', result['messages'][-1].content)
    after = path.read_text(encoding='utf-8')
    print('Memory file:', path, '\nChanged:', before != after, '\nCurrent memory:', after)


if __name__ == '__main__':
    main()
