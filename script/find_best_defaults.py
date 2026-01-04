import requests
import random
import time

API_URL = "http://127.0.0.1:8080"
TRIALS = 100

def get_features():
    try:
        resp = requests.get(f"{API_URL}/ai/features", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Error fetching features: {e}")
    return None

def generate_random_technicals(names):
    techs = {}
    for name in names:
        lname = name.lower()
        if "rsi" in lname:
            # User suggests standard RSI range (0-100)
            techs[name] = random.uniform(20.0, 90.0)
        elif "ema_10" in lname:
            # Assuming Ratio price/ema
            techs[name] = random.uniform(0.8, 1.3)
        elif "ema_50" in lname:
            # Assuming Diff (percent)
            techs[name] = random.uniform(-0.1, 0.1)
        elif "macd" in lname:
            # MACD Value
            techs[name] = random.uniform(-0.5, 0.5)
        else:
            techs[name] = random.uniform(-1.0, 1.0)
    return techs

def generate_random_features(names):
    # Same logic as technicals for now, assuming similar feature set (RSI, EMA, etc.)
    vals = []
    for name in names:
        lname = name.lower()
        val = 0.0
        if "rsi" in lname:
            val = random.uniform(20.0, 80.0)
        elif "ema_10" in lname:
            val = random.uniform(0.8, 1.25)
        elif "ema_50" in lname:
            val = random.uniform(-0.1, 0.1)
        elif "macd" in lname:
            val = random.uniform(-0.5, 0.5)
        else:
            val = random.uniform(0.0, 1.0)
        vals.append(val)
    return vals

def main():
    feat_meta = get_features()
    if not feat_meta:
        print("Could not get feature metadata. Using hardcoded defaults.")
        model_names = ["ema_10", "ema_50", "rsi", "macd"]
        hist_names = [f"Feature {i}" for i in range(4)]
    else:
        model_names = feat_meta.get("model_features", [])
        hist_names = feat_meta.get("history_features", [])

    print(f"Model Features: {model_names}")
    print(f"History Features: {hist_names}")
    
    best_model_ret = -999.0
    best_model_inputs = None
    
    best_hist_ret = -999.0
    best_hist_inputs = None
    
    # Try 100 combinations
    for i in range(TRIALS):
        techs = generate_random_technicals(model_names)
        hist_vals = generate_random_features(hist_names)
        
        payload = {
            "prompt": "bullish momentum",
            "feature_values": hist_vals,
            "technicals": techs
        }
        
        try:
            resp = requests.post(f"{API_URL}/ai/signal_analysis", json=payload, timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                
                # Check Model Return
                ret_m = data.get("expected_return_from_model", 0.0)
                try: ret_m = float(ret_m)
                except: ret_m = 0.0
                
                if ret_m > best_model_ret:
                    best_model_ret = ret_m
                    best_model_inputs = techs
                    
                # Check History Return
                ret_h = data.get("expected_return_from_history", 0.0)
                try: ret_h = float(ret_h)
                except: ret_h = 0.0
                
                if ret_h > best_hist_ret:
                    best_hist_ret = ret_h
                    best_hist_inputs = hist_vals # List
                    
                print(f"Trial {i+1}: Mod: {ret_m:.5f}, Hist: {ret_h:.5f}")
            else:
                print(f"Trial {i+1} failed: {resp.status_code}")
        except Exception as e:
            print(f"Trial {i+1} error: {e}")
            
    print("-" * 30)
    print(f"MAX MODEL RETURN: {best_model_ret}")
    if best_model_inputs:
        for k, v in best_model_inputs.items():
            print(f"  {k}: {v:.4f}")
            
    print(f"\nMAX HISTORY RETURN: {best_hist_ret}")
    if best_hist_inputs:
        for i, val in enumerate(best_hist_inputs):
            name = hist_names[i] if i < len(hist_names) else f"Feat {i}"
            print(f"  {name}: {val:.4f}")


if __name__ == "__main__":
    main()
