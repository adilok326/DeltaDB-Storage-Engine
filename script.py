import time
from src.engine import DeltaDB

print("--- Starting Massive Bulk Input Simulation ---")
db = DeltaDB(max_wal_entries=50)

start_time = time.time()
print("\n[SIMULATION] Injecting 40 rapid SET operations...")

for i in range(1, 41):
    db.set(f"user_session_{i}", f"token_xyz_789_{i*5}")

print("\n[SIMULATION] Fetching records dynamically...")
db.get("user_session_15")
db.get("user_session_30")
print("\n[SIMULATION] Injecting 20 rapid DEL operations...")
for i in range(1, 21):
    db.delete(f"user_session_{i}")

duration = time.time() - start_time
print(f"\n[SUCCESS] Stress test complete! Processed 62 operations in {duration:.4f} seconds.")
