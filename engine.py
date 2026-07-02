import os
import json
import time

class DeltaDB:
    def __init__(self, data_dir="data", max_wal_entries=5):
        self.memory_store = {}
        self.data_dir = data_dir
        self.max_wal_entries = max_wal_entries
        
        self.wal_path = os.path.join(data_dir, "wal.txt")
        self.snapshot_path = os.path.join(data_dir, "snapshot.json")
        self.wal_entry_count = 0
        os.makedirs(data_dir, exist_ok=True)
        
        # System Boot Protocol: Load Snapshot first, then replay WAL
        self._load_snapshot()
        self._replay_wal()

    def set(self, key, value):
        start = time.perf_counter()
        
        # 1. Append to WAL (Durability)
        self._append_to_wal("SET", key, value)
        
        # 2. Commit to Memory
        self.memory_store[key] = value
        
        latency = (time.perf_counter() - start) * 1000
        print(f"[SUCCESS] SET [{key} -> {value}] in {latency:.4f}ms")
        
        self._check_compaction_trigger()

    def get(self, key):
        start = time.perf_counter()
        value = self.memory_store.get(key, None)
        latency = (time.perf_counter() - start) * 1000
        
        if value is None:
            print(f"[NOT FOUND] Key '{key}' does not exist ({latency:.4f}ms)")
            return None
        
        print(f"[FETCH] {key} = {value} ($O(1)$ memory read in {latency:.4f}ms)")
        return value

    def delete(self, key):
        start = time.perf_counter()
        if key not in self.memory_store:
            print(f"[ERROR] Cannot delete non-existent key '{key}'")
            return False
            
        # 1. Append a "Tombstone" to WAL to log the deletion
        self._append_to_wal("DEL", key, "")
        
        # 2. Remove from active memory
        del self.memory_store[key]
        
        latency = (time.perf_counter() - start) * 1000
        print(f"[SUCCESS] DEL [{key}] (Tombstone logged in {latency:.4f}ms)")
        
        self._check_compaction_trigger()
        return True

    def _append_to_wal(self, op, key, val):
        # Using flush() ensures data hits the disk physical layer immediately
        with open(self.wal_path, "a") as f:
            f.write(f"{op},{key},{val}\n")
            f.flush() 
        self.wal_entry_count += 1

    def create_snapshot(self):
        """LOG COMPACTION: Dumps current memory state and wipes the bloated WAL."""
        start = time.perf_counter()
        print("\n[COMPACTION] Triggered! Compacting engine logs...")
        
        # Atomic Write: Write to temp first, then rename to avoid corruption
        temp_snapshot = self.snapshot_path + ".tmp"
        with open(temp_snapshot, "w") as f:
            json.dump(self.memory_store, f)
            f.flush()
        
        if os.path.exists(self.snapshot_path):
            os.remove(self.snapshot_path)
        os.rename(temp_snapshot, self.snapshot_path)
        
        # Clear the WAL log because snapshot represents the definitive state
        if os.path.exists(self.wal_path):
            os.remove(self.wal_path)
            
        self.wal_entry_count = 0
        latency = (time.perf_counter() - start) * 1000
        print(f"[COMPACTION] Log compaction completed in {latency:.4f}ms. WAL cleared.\n")

    def _load_snapshot(self):
        if os.path.exists(self.snapshot_path):
            print("[STARTUP] Loading base state from snapshot.json...")
            with open(self.snapshot_path, "r") as f:
                self.memory_store = json.load(f)

    def _replay_wal(self):
        if not os.path.exists(self.wal_path):
            return
        
        print("[STARTUP] Replaying WAL mutations for crash recovery...")
        with open(self.wal_path, "r") as f:
            for line in f:
                if line.strip():
                    self.wal_entry_count += 1
                    op, key, val = line.strip().split(",", 2)
                    if op == "SET":
                        self.memory_store[key] = val
                    elif op == "DEL":
                        self.memory_store.pop(key, None)
        print(f"[STARTUP] System fully recovered. Active keys in memory: {len(self.memory_store)}\n")

    def _check_compaction_trigger(self):
        if self.wal_entry_count >= self.max_wal_entries:
            self.create_snapshot()
