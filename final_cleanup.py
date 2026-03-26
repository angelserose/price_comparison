import shutil
import os
import stat

def remove_readonly(func, path, exc):
    """Error handler for Windows read-only files."""
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR | stat.S_IREAD)
        func(path)
    else:
        raise

root = r"D:\SCET\S4\DBMS\ARSHA\price-comparison-project02-main"

# Delete nested folder
nested = os.path.join(root, "price-comparison-project02-main")
if os.path.exists(nested):
    try:
        shutil.rmtree(nested, onerror=remove_readonly)
        print(f"✓ Deleted: price-comparison-project02-main/")
    except Exception as e:
        print(f"✗ Error deleting nested: {e}")
else:
    print(f"✓ Nested folder already deleted")

# Delete frontend folder
frontend = os.path.join(root, "frontend")
if os.path.exists(frontend):
    try:
        shutil.rmtree(frontend, onerror=remove_readonly)
        print(f"✓ Deleted: frontend/")
    except Exception as e:
        print(f"✗ Error deleting frontend: {e}")
else:
    print(f"✓ Frontend folder already deleted")

print("\n" + "="*60)
print("✓ PROJECT STRUCTURE CLEANUP COMPLETE!")
print("="*60)

dirs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
print(f"\nRemaining folders: {len(dirs)}")
for folder in sorted(dirs):
    print(f"  ✓ {folder}/")
