from src.ui.patch_review import extract_patched_code

orig = """def add(a, b):
    return a + b
    
def sub(a, b):
    return a - b
"""

patch = """--- a/math.py
+++ b/math.py
@@ -1,5 +1,5 @@
 def add(a, b):
-    return a + b
+    return a + b + 0
     
 def sub(a, b):
     return a - b
"""

res = extract_patched_code(orig, patch)
print("PATCHED CODE:")
print(res)
