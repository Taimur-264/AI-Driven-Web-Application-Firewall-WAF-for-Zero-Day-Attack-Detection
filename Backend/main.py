import time
import urllib.parse
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import shap
import numpy as np

app = FastAPI(title="AI-Driven WAF with XAI", version="2.7")

# ==========================================
# 0. CORS CONFIGURATION
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

# ==========================================
# 1. AI MODEL & XAI EXPLAINER LOADING
# ==========================================
try:
    vectorizer = joblib.load("vectorizer.pkl")
    rf_model = joblib.load("rf_model.pkl")
    explainer = shap.TreeExplainer(rf_model)
    feature_names = vectorizer.get_feature_names_out()
    AI_ENABLED = True
    print("✅ AI Models and SHAP Explainer Loaded Successfully.")
except Exception as e:
    AI_ENABLED = False
    print(f"⚠️ AI/XAI Models not found. Running in Rule-Based mode only. Error: {e}")

# ==========================================
# 2. GLOBAL STORAGE & RULES
# ==========================================
ATTACK_PATTERNS = {
    "<script>": "OWASP A03: XSS",
    "alert(": "OWASP A03: XSS",
    "union select": "OWASP A03: SQL Injection",
    "or '1'='1": "OWASP A03: SQL Injection",
    "../": "OWASP A01: Path Traversal",
    "/etc/passwd": "OWASP A01: Path Traversal"
}

threat_logs = []
ip_tracking = {}
RATE_LIMIT_WINDOW = 5.0  
RATE_LIMIT_MAX_REQUESTS = 15

def check_bot_traffic(client_ip: str):
    current_time = time.time()
    if client_ip not in ip_tracking:
        ip_tracking[client_ip] = []
    ip_tracking[client_ip] = [t for t in ip_tracking[client_ip] if current_time - t < RATE_LIMIT_WINDOW]
    ip_tracking[client_ip].append(current_time)
    if len(ip_tracking[client_ip]) > RATE_LIMIT_MAX_REQUESTS:
        return True
    return False

# ==========================================
# 3. WAF MIDDLEWARE (The Interceptor)
# ==========================================
@app.middleware("http")
async def waf_core_engine(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    # CRITICAL FIX: Extract spoofed IP from headers for realistic simulation
    client_ip = request.headers.get("x-forwarded-for", request.client.host).split(",")[0].strip()
    
    raw_url = str(request.url)
    decoded_url = urllib.parse.unquote(raw_url).lower()

    safe_endpoints = ["/token", "/logs", "/api/v1/stats"]
    if any(safe_path in decoded_url for safe_path in safe_endpoints):
        return await call_next(request)

    status = "ALLOWED"
    attack_type = "None"
    xai_reason = ""

    # LAYER 1: Bot Detection Check
    if check_bot_traffic(client_ip):
        status = "BLOCKED"
        attack_type = "AI: Automated Bot Traffic Detected"

    # LAYER 2: Rule-Based OWASP Check
    if status == "ALLOWED":
        for pattern, rule_name in ATTACK_PATTERNS.items():
            if pattern in decoded_url:
                status = "BLOCKED"
                attack_type = rule_name
                break

    # LAYER 3: AI & XAI Zero-Day Check
    if status == "ALLOWED" and AI_ENABLED:
        try:
            features = vectorizer.transform([decoded_url])
            prediction = rf_model.predict(features)[0]
            
            dense_features = features.toarray()
            shap_vals = explainer.shap_values(dense_features)

            if isinstance(shap_vals, list): instance_shap = shap_vals[1][0]
            elif len(shap_vals.shape) == 3: instance_shap = shap_vals[0, :, 1]
            else: instance_shap = shap_vals[0]

            top_indices = np.argsort(np.abs(instance_shap))[-3:]
            evidence = []
            for i in reversed(top_indices):
                if dense_features[0][i] > 0: 
                    evidence.append(f"'{feature_names[i]}' ({'increased risk' if instance_shap[i] > 0 else 'decreased risk'})")
            
            xai_reason = " | ".join(evidence) if evidence else "Anomalous structure"

            if prediction == 1:
                status = "BLOCKED"
                attack_type = f"AI Anomaly - Evidence: {xai_reason}"
        except Exception as e:
            print(f"XAI Processing Error: {e}")
            if 'prediction' in locals() and prediction == 1:
                status = "BLOCKED"
                attack_type = "AI: Anomaly Detected (XAI Translation Failed)"

    # Final Action: Log and Block
    if status == "BLOCKED":
        log_entry = {
            "id": len(threat_logs) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": client_ip,
            "payload": decoded_url,
            "reason": attack_type 
        }
        threat_logs.insert(0, log_entry) 
        
        print(f"🚨 BLOCKED [{client_ip}] Reason: {attack_type} | Payload: {decoded_url}")
        
        return JSONResponse(
            status_code=403, 
            content={"detail": "Blocked by WAF", "reason": attack_type},
            headers={"Access-Control-Allow-Origin": "*"}
        )

    return await call_next(request)

# ==========================================
# 4. API ENDPOINTS
# ==========================================
@app.get("/search")
async def search(q: str = ""):
    return {"message": "Search successful", "query": q, "status": "Clean Traffic"}

@app.get("/logs")
async def get_logs():
    return threat_logs

@app.get("/api/v1/stats")
async def get_stats():
    return {
        "logs": threat_logs,
        "total_threats_blocked": len(threat_logs)
    }

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/token")
async def login(credentials: LoginRequest):
    if credentials.username == "admin" and credentials.password == "admin123":
        return {"access_token": "fyp_phase2_master_token_123", "token_type": "bearer", "message": "Login Successful"}
    raise HTTPException(status_code=401, detail="Invalid Username or Password")