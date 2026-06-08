import time
# If your engine is sitting directly in the folder, use this import line:
from src.engine import DeltaDB

print("--- Starting Massive Bulk Input Simulation ---")
# Initializing database with a higher compaction threshold (50 entries)
db = DeltaDB(max_wal_entries=50)

start_time = time.time()

# 1. Simulate 40 rapid user registrations
print("\n[SIMULATION] Injecting 40 rapid SET operations...")
for i in range(1, 41):
    db.set(f"user_session_{i}", f"token_xyz_789_{i*5}")

# 2. Simulate rapid data updates and reads
print("\n[SIMULATION] Fetching records dynamically...")
db.get("user_session_15")
db.get("user_session_30")

# 3. Simulate mass deletions (Tombstones)
print("\n[SIMULATION] Injecting 20 rapid DEL operations...")
for i in range(1, 21):
    db.delete(f"user_session_{i}")

duration = time.time() - start_time
print(f"\n[SUCCESS] Stress test complete! Processed 62 operations in {duration:.4f} seconds.")