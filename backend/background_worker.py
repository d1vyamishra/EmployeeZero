import time
import sys
import os
from main import run_automation

# Ensure backend path is configured correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Cooldown time between scans (set to 30 seconds for local live testing)
CHECK_INTERVAL_SECONDS = 30 

def start_infinite_worker():
    print("🚀 BPO-Killer-Agent Background Worker is now LIVE...")
    print(f"📡 Monitoring channels and Supabase every {CHECK_INTERVAL_SECONDS} seconds.\n")
    
    loop_count = 1
    while True:
        try:
            print(f"🔄 [Cycle #{loop_count}] Executing automation tasks...")
            
            # Fire the unified inbound and outbound sequence cleanly
            run_automation()
            
            print(f"😴 Cycle #{loop_count} complete. Worker sleeping for {CHECK_INTERVAL_SECONDS}s...")
            loop_count += 1
            time.sleep(CHECK_INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            print("\n🛑 Background Worker stopped manually by user.")
            break
        except Exception as e:
            print(f"❌ Error encountered in worker loop: {e}")
            print(f"⏳ Retrying in {CHECK_INTERVAL_SECONDS} seconds...")
            time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    start_infinite_worker()