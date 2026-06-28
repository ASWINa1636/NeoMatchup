try:
    from main import *
    print("SUCCESS: main.py imported successfully")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
