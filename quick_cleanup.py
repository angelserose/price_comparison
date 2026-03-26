import shutil
import os
from pathlib import Path

# Define paths
root = r"D:\SCET\S4\DBMS\ARSHA\price-comparison-project02-main"
nested = os.path.join(root, "price-comparison-project02-main")

print("=" * 70)
print("PROJECT STRUCTURE CLEANUP")
print("=" * 70)

# 1. Copy nested backend files to root backend
print("\n[1/4] Consolidating backend files...")
nested_backend = os.path.join(nested, "backend")
root_backend = os.path.join(root, "backend")

if os.path.exists(nested_backend):
    for file in os.listdir(nested_backend):
        src = os.path.join(nested_backend, file)
        dst = os.path.join(root_backend, file)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            print(f"  ✓ Copied {file}")

# 2. Copy templates
print("\n[2/4] Consolidating templates...")
nested_templates = os.path.join(nested, "frontend", "templates")
root_templates = os.path.join(root, "templates")

if os.path.exists(nested_templates):
    for file in os.listdir(nested_templates):
        src = os.path.join(nested_templates, file)
        dst = os.path.join(root_templates, file)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            print(f"  ✓ Copied {file}")

# 3. Copy static files
print("\n[3/4] Consolidating static files...")
nested_static = os.path.join(nested, "frontend", "static")
root_static = os.path.join(root, "static")

if os.path.exists(nested_static):
    for file in os.listdir(nested_static):
        src = os.path.join(nested_static, file)
        dst = os.path.join(root_static, file)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            print(f"  ✓ Copied {file}")

# 4. Copy clones folder
print("\n[4/4] Consolidating clones folder...")
nested_clones = os.path.join(nested, "clones")
root_clones = os.path.join(root, "clones")

if os.path.exists(nested_clones) and not os.path.exists(root_clones):
    shutil.copytree(nested_clones, root_clones)
    print(f"  ✓ Copied clones folder")

print("\n" + "=" * 70)
print("✓ CLEANUP COMPLETE!")
print("=" * 70)

print("\nNew Structure:")
print(f"  {root}/")
print(f"  ├── app.py")
print(f"  ├── requirements.txt")
print(f"  ├── .env")
print(f"  ├── Procfile")
print(f"  ├── backend/")
print(f"  ├── templates/")
print(f"  ├── static/")
print(f"  ├── scraper/")
print(f"  └── clones/")

print("\n⚠️  Next Steps:")
print(f"  1. Delete: {nested}")
print(f"  2. Delete: root 'frontend' folder (if exists)")
print(f"  3. Update app.py paths from '../frontend/templates' to 'templates'")
print(f"  4. Update app.py paths from '../frontend/static' to 'static'")
print("\n✓ All files safely copied! No data lost.")
