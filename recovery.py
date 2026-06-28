import json, os

log_path = r'C:\Users\Aswin A\.gemini\antigravity-ide\brain\8de8ad3f-3cbf-4d93-abe5-b35331aee40f\.system_generated\logs\transcript.jsonl'
files = {}

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if 'tool_calls' in data:
                for tc in data['tool_calls']:
                    if tc['name'] == 'write_to_file':
                        args = tc['args']
                        if not isinstance(args, dict):
                            args = json.loads(args) if isinstance(args, str) else args
                        
                        path = args.get('TargetFile', '').strip('"')
                        content = args.get('CodeContent', '')
                        if content.startswith('"') and content.endswith('"'):
                            content = content[1:-1].encode().decode('unicode_escape')
                        if path:
                            files[path] = content
        except Exception as e:
            pass

print('Found files:', len(files))
for k, v in files.items():
    print(k)
    try:
        os.makedirs(os.path.dirname(k), exist_ok=True)
        with open(k, 'w', encoding='utf-8') as out:
            out.write(v)
    except Exception as e:
        print("Failed to write", k, e)
