import os, subprocess, time, requests
from pyngrok import ngrok

APP = "/content/streamlit_app.py"  # your app path
PORT = 8501                                   # change if you prefer another port

# Ensure your module folder is on PYTHONPATH for the separate Streamlit process
env = os.environ.copy()
env["PYTHONPATH"] = "/content/EmpathyBot:" + env.get("PYTHONPATH","")

# Start Streamlit (background), log to file
LOG = "/content/streamlit.log"
proc = subprocess.Popen(
    ["streamlit","run",APP,"--server.address","0.0.0.0","--server.port",str(PORT),
     "--browser.gatherUsageStats","false"],
    env=env, stdout=open(LOG,"w"), stderr=subprocess.STDOUT, text=True
)
print(f"Streamlit starting (PID {proc.pid}) → logs at {LOG}")

# Wait until Streamlit is healthy
health = f"http://127.0.0.1:{PORT}/_stcore/health"
for _ in range(120):
    try:
        r = requests.get(health, timeout=1)
        if r.ok and r.text.strip().lower() == "ok":
            print(f"✅ Streamlit is UP on 127.0.0.1:{PORT}")
            break
    except Exception:
        pass
    time.sleep(1)
else:
    print("❌ Streamlit didn't become healthy. Last log lines:")
    print(open(LOG).read()[-2000:])

# Close any previous tunnels on this runtime (safety)
for t in ngrok.get_tunnels():
    ngrok.disconnect(t.public_url)

# Open tunnel to the correct upstream
public = ngrok.connect(addr=f"http://127.0.0.1:{PORT}", proto="http")
print("🌐 Public URL:", public.public_url)
