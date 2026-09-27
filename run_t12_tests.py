"""Quick script to run T12 tests and show summary"""
import subprocess
import sys

print("Running T12 Core Round-Trip Tests...")
print("=" * 70)

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_core_roundtrip.py", "-v", "--tb=short"],
    capture_output=True,
    text=True,
    timeout=180
)

# Print last 50 lines
lines = result.stdout.split('\n')
for line in lines[-50:]:
    print(line)

print()
print("Exit code:", result.returncode)
