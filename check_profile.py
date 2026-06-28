import json
log = r'C:\Users\Aswin A\.gemini\antigravity-ide\brain\8de8ad3f-3cbf-4d93-abe5-b35331aee40f\.system_generated\logs\transcript.jsonl'
for line in open(log, 'r', encoding='utf-8'):
    if 'profile.py' in line and 'write_to_file' in line:
        try:
            data = json.loads(line)
            for tc in data.get('tool_calls', []):
                if tc['name'] == 'write_to_file':
                    args = tc['args']
                    if not isinstance(args, dict): args = json.loads(args) if isinstance(args, str) else args
                    if 'profile.py' in args.get('TargetFile', ''):
                        content = args.get('CodeContent', '')
                        if content.startswith('\"'): content = content[1:-1].encode().decode('unicode_escape')
                        print('Length of profile.py in write_to_file:', len(content))
        except Exception:
            pass
