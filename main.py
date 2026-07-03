from src.engine import DeltaDB

if __name__ == "__main__":
    db = DeltaDB(max_wal_entries=5)
    print("--- DeltaDB Storage Engine (v2.0 Production-Ready) ---")
    print("Commands: SET <key> <val> | GET <key> | DEL <key> | SNAPSHOT | EXIT\n")
    
    while True:
        try:
            tokens = input("DeltaDB> ").strip().split(" ", 2)
            cmd = tokens[0].upper()
            
            if cmd == "EXIT":
                break
            elif cmd == "SNAPSHOT":
                db.create_snapshot()
            elif cmd == "SET" and len(tokens) == 3:
                db.set(tokens[1], tokens[2])
            elif cmd == "GET" and len(tokens) == 2:
                db.get(tokens[1])
            elif cmd == "DEL" and len(tokens) == 2:
                db.delete(tokens[1])
            else:
                print("[ERROR] Command syntax mismatch.")
        except Exception as e:
            print(f"[ERROR] Operational failure: {e}")
