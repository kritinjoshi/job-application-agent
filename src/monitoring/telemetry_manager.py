import os
import json
import datetime

class TelemetryManager:
    # Resolve the data file relative to this script (src/telemetry/...)
    DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "usage_history.json")
    
    @staticmethod
    def log_request(model, input_tokens, output_tokens, status_code=200):
        os.makedirs(os.path.dirname(TelemetryManager.DATA_FILE), exist_ok=True)
        
        history = []
        if os.path.exists(TelemetryManager.DATA_FILE):
            try:
                with open(TelemetryManager.DATA_FILE, "r") as f:
                    history = json.load(f)
            except Exception:
                pass
                
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "status": status_code
        }
        
        history.append(entry)
        if len(history) > 500:
            history = history[-500:]
            
        with open(TelemetryManager.DATA_FILE, "w") as f:
            json.dump(history, f, indent=2)

    @staticmethod
    def get_summary_stats():
        if not os.path.exists(TelemetryManager.DATA_FILE):
            return "No usage history recorded yet."
            
        try:
            with open(TelemetryManager.DATA_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            return "Failed to read usage history."
            
        now = datetime.datetime.now()
        one_day_ago = now - datetime.timedelta(days=1)
        one_minute_ago = now - datetime.timedelta(minutes=1)
        
        daily_entries = [e for e in history if datetime.datetime.fromisoformat(e["timestamp"]) > one_day_ago]
        recent_entries = [e for e in history if datetime.datetime.fromisoformat(e["timestamp"]) > one_minute_ago]
        
        daily_requests = len(daily_entries)
        daily_tokens = sum(e["total_tokens"] for e in daily_entries)
        minute_rpm = len(recent_entries)
        last_model = history[-1]["model"] if history else "N/A"
        
        summary = f"""
AI USAGE TELEMETRY REPORT:
-----------------------------------
Requests in last 1 min (RPM): {minute_rpm}
Requests in last 24h (RPD): {daily_requests} 
Total Tokens consumed (Last 24h): {daily_tokens:,}
Last Model Used: {last_model}
-----------------------------------
"""
        return summary
