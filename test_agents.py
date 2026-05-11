"""Run: python test_agents.py — tests the full agent pipeline with a sample diff."""
from agents import run_review

SAMPLE_DIFF = """
### app.py
```
+ import os
+ password = os.getenv("PASSWORD", "hardcoded_secret_123")
+
+ def get_users(db, user_input):
+     query = f"SELECT * FROM users WHERE name = '{user_input}'"
+     return db.execute(query)
+
+ def process_items(items):
+     result = []
+     for i in range(len(items)):
+         result = result + [items[i] * 2]
+     return result
```
"""

print("Running agents... this may take a few seconds.\n")
comment = run_review(SAMPLE_DIFF)
print(comment)
