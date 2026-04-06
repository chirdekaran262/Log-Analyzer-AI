#!/usr/bin/env python3
"""
ShopForge - Dummy E-Commerce Log Generator
==========================================
Simulates a real production e-commerce application.
Automatically writes logs to the logs/ folder with timestamped filenames.

Usage:
    python shopforge_log_generator.py

Log Files Created:
    logs/app_YYYY-MM-DD.log       → All logs (main log)
    logs/access_YYYY-MM-DD.log    → HTTP access logs
    logs/error_YYYY-MM-DD.log     → WARN + ERROR + CRITICAL only
    logs/security_YYYY-MM-DD.log  → Auth + attack events
"""

import logging
import os
import random
import time
import json
import uuid
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
LOG_DIR = "logs"
LOG_INTERVAL_MIN = 0.5   # seconds between log events (min)
LOG_INTERVAL_MAX = 1.5   # seconds between log events (max)
CRITICAL_CHANCE  = 0.04  # 4%  chance of CRITICAL event
ERROR_CHANCE     = 0.12  # 12% chance of ERROR event
WARN_CHANCE      = 0.20  # 20% chance of WARN event

os.makedirs(LOG_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# LOG FILE SETUP  (timestamped filenames)
# ─────────────────────────────────────────────
today = datetime.now().strftime("%Y-%m-%d")

LOG_FILES = {
    "app":      os.path.join(LOG_DIR, f"app_{today}.log"),
    "access":   os.path.join(LOG_DIR, f"access_{today}.log"),
    "error":    os.path.join(LOG_DIR, f"error_{today}.log"),
    "security": os.path.join(LOG_DIR, f"security_{today}.log"),
}

# Custom log format  →  same format as real industry logs
LOG_FORMAT = "%(asctime)s.%(msecs)03d  [%(levelname)-8s]  %(name)-22s  %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def make_handler(filepath, level=logging.DEBUG):
    """Create a rotating file handler (max 10 MB, keep 5 backups)."""
    h = RotatingFileHandler(filepath, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
    h.setLevel(level)
    h.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    return h


def make_console_handler():
    """Coloured console output so you can watch logs live."""
    COLOURS = {
        "DEBUG":    "\033[36m",   # cyan
        "INFO":     "\033[32m",   # green
        "WARNING":  "\033[33m",   # yellow
        "ERROR":    "\033[31m",   # red
        "CRITICAL": "\033[1;31m", # bold red
    }
    RESET = "\033[0m"

    class ColouredFormatter(logging.Formatter):
        def format(self, record):
            colour = COLOURS.get(record.levelname, "")
            record.levelname = f"{colour}{record.levelname:<8}{RESET}"
            return super().format(record)

    h = logging.StreamHandler()
    h.setLevel(logging.DEBUG)
    h.setFormatter(ColouredFormatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    return h


# ─── Build loggers ───────────────────────────
def get_logger(name, extra_handlers=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(make_handler(LOG_FILES["app"]))       # everything → app.log
    logger.addHandler(make_handler(LOG_FILES["error"], logging.WARNING))  # WARN+ → error.log
    logger.addHandler(make_console_handler())
    if extra_handlers:
        for h in extra_handlers:
            logger.addHandler(h)
    logger.propagate = False
    return logger


access_extra   = [make_handler(LOG_FILES["access"])]
security_extra = [make_handler(LOG_FILES["security"])]

loggers = {
    "api-gateway":           get_logger("api-gateway",           access_extra),
    "product-service":       get_logger("product-service"),
    "cart-service":          get_logger("cart-service"),
    "payment-service":       get_logger("payment-service"),
    "user-service":          get_logger("user-service",          security_extra),
    "order-service":         get_logger("order-service"),
    "search-service":        get_logger("search-service"),
    "notification-service":  get_logger("notification-service"),
    "inventory-service":     get_logger("inventory-service"),
}


# ─────────────────────────────────────────────
# FAKE DATA
# ─────────────────────────────────────────────
USERS = [
    {"id": "usr_4821", "name": "Priya Sharma",   "ip": "103.21.58.14",    "role": "customer"},
    {"id": "usr_1093", "name": "Rohan Mehta",    "ip": "49.37.201.95",    "role": "customer"},
    {"id": "usr_2210", "name": "Ananya Singh",   "ip": "117.96.44.201",   "role": "customer"},
    {"id": "usr_3305", "name": "Vikram Nair",    "ip": "182.64.12.88",    "role": "premium"},
    {"id": "usr_7734", "name": "Anonymous",      "ip": "185.220.101.47",  "role": "guest"},
    {"id": "usr_0001", "name": "Admin",          "ip": "10.0.0.1",        "role": "admin"},
]

PRODUCTS = [
    {"id": "P001", "name": "Running Shoes",   "price": 2499,  "stock": 14},
    {"id": "P002", "name": "Cotton T-Shirt",  "price": 499,   "stock": 82},
    {"id": "P003", "name": "Wireless Earbuds","price": 1899,  "stock": 3},
    {"id": "P004", "name": "Smart Watch",     "price": 8999,  "stock": 0},
    {"id": "P005", "name": "Backpack",        "price": 1299,  "stock": 27},
    {"id": "P006", "name": "Sunglasses",      "price": 799,   "stock": 45},
    {"id": "P007", "name": "Laptop Stand",    "price": 1599,  "stock": 2},
    {"id": "P008", "name": "Water Bottle",    "price": 349,   "stock": 100},
]

PAGES        = ["/", "/products", "/cart", "/checkout", "/account", "/orders", "/wishlist"]
SEARCH_TERMS = ["shoes", "laptop", "t-shirt", "earbuds", "watch", "bag", "charger", "headphones"]
GATEWAYS     = ["razorpay", "payu", "stripe"]
COURIERS     = ["BlueDart", "Delhivery", "DTDC", "Ekart"]
HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
BAD_IPS      = ["91.108.4.55", "45.83.64.12", "178.128.23.99", "185.176.27.44", "103.77.192.11"]

def rand_user():     return random.choice(USERS)
def rand_product():  return random.choice(PRODUCTS)
def rand_order():    return f"ORD-{random.randint(100000, 999999)}"
def rand_txn():      return f"TXN{random.randint(1000000, 9999999)}"
def rand_req():      return f"req_{uuid.uuid4().hex[:10]}"
def rand_trace():    return uuid.uuid4().hex[:16]
def rand_ms(lo, hi): return random.randint(lo, hi)


def kv(**kwargs) -> str:
    """Format extra fields as key=value pairs (like logfmt)."""
    return "  " + "  ".join(
        f'{k}={json.dumps(v) if isinstance(v, (dict, list)) else v}'
        for k, v in kwargs.items()
    )


# ─────────────────────────────────────────────
# EVENT SIMULATORS
# ─────────────────────────────────────────────

# ── INFO events ──────────────────────────────
def evt_page_view():
    u = rand_user()
    page = random.choice(PAGES)
    loggers["api-gateway"].info(
        f"HTTP GET {page} 200" +
        kv(user=u["id"], ip=u["ip"], latency_ms=rand_ms(30,200),
           req=rand_req(), trace=rand_trace(), ua="Mozilla/5.0")
    )

def evt_search():
    u = rand_user()
    term = random.choice(SEARCH_TERMS)
    results = random.randint(0, 50)
    loggers["search-service"].info(
        f"Search executed query='{term}' results={results}" +
        kv(user=u["id"], ip=u["ip"], latency_ms=rand_ms(20,140), req=rand_req())
    )

def evt_login():
    u = rand_user()
    loggers["user-service"].info(
        f"User login successful" +
        kv(user=u["id"], name=u["name"], ip=u["ip"],
           method="password", mfa=False, latency_ms=rand_ms(80,220), req=rand_req())
    )

def evt_logout():
    u = rand_user()
    loggers["user-service"].info(
        f"User logout" +
        kv(user=u["id"], ip=u["ip"], session_duration_s=random.randint(120, 7200), req=rand_req())
    )

def evt_add_to_cart():
    u = rand_user()
    p = rand_product()
    loggers["cart-service"].info(
        f"Item added to cart product='{p['name']}'" +
        kv(user=u["id"], product_id=p["id"], price=p["price"], qty=1,
           req=rand_req(), trace=rand_trace())
    )

def evt_payment_success():
    u = rand_user()
    amount = random.randint(299, 15000)
    loggers["payment-service"].info(
        f"Payment processed successfully amount=₹{amount}" +
        kv(user=u["id"], gateway=random.choice(GATEWAYS), txn=rand_txn(),
           currency="INR", latency_ms=rand_ms(300,900), req=rand_req())
    )
    loggers["order-service"].info(
        f"Order created order={rand_order()}" +
        kv(user=u["id"], items=random.randint(1, 5), amount=amount)
    )
    loggers["notification-service"].info(
        f"Order confirmation email dispatched" +
        kv(user=u["id"], email=f"{u['name'].lower().replace(' ','.')}@email.com")
    )

def evt_order_track():
    u = rand_user()
    loggers["order-service"].info(
        f"Order tracking requested order={rand_order()}" +
        kv(user=u["id"], status="shipped", courier=random.choice(COURIERS),
           eta_days=random.randint(1, 5), req=rand_req())
    )

def evt_product_view():
    u = rand_user()
    p = rand_product()
    loggers["product-service"].info(
        f"Product detail viewed product='{p['name']}'" +
        kv(user=u["id"], product_id=p["id"], price=p["price"],
           latency_ms=rand_ms(15, 90), req=rand_req())
    )

def evt_wishlist():
    u = rand_user()
    p = rand_product()
    loggers["product-service"].info(
        f"Product added to wishlist product='{p['name']}'" +
        kv(user=u["id"], product_id=p["id"], req=rand_req())
    )

# ── WARN events ──────────────────────────────
def evt_slow_query():
    ms = rand_ms(3000, 9000)
    loggers["product-service"].warning(
        f"Slow database query detected duration_ms={ms}" +
        kv(query="SELECT * FROM products WHERE category=?",
           threshold_ms=2000, table="products", db_host="db-primary.internal")
    )

def evt_high_memory():
    used = random.randint(750, 960)
    loggers["api-gateway"].warning(
        f"High memory usage detected used_mb={used}/1024" +
        kv(percent=round(used/1024*100,1), pod="api-gateway-7d9f4b",
           threshold_mb=800)
    )

def evt_rate_limit():
    u = rand_user()
    rps = random.randint(85, 99)
    loggers["api-gateway"].warning(
        f"Rate limit threshold approaching requests_per_min={rps}/100" +
        kv(ip=u["ip"], user=u["id"], endpoint="/api/products", limit=100)
    )

def evt_low_stock():
    p = rand_product()
    stock = random.randint(1, 5)
    loggers["inventory-service"].warning(
        f"Low inventory alert product='{p['name']}' stock={stock}" +
        kv(product_id=p["id"], reorder_point=10, warehouse="MUM-WH1")
    )

def evt_session_expiry():
    u = rand_user()
    loggers["user-service"].warning(
        f"Session nearing expiry" +
        kv(user=u["id"], ip=u["ip"],
           expires_in_s=random.randint(60, 300),
           session=f"sess_{uuid.uuid4().hex[:16]}")
    )

def evt_deprecated_api():
    u = rand_user()
    loggers["api-gateway"].warning(
        f"Deprecated API endpoint called /api/v1/products" +
        kv(user=u["id"], migrate_to="/api/v2/products",
           deprecated_since="2024-01-01", req=rand_req())
    )

# ── ERROR events ─────────────────────────────
def evt_payment_fail():
    u = rand_user()
    amount = random.randint(299, 15000)
    loggers["payment-service"].error(
        f"Payment processing failed amount=₹{amount}" +
        kv(user=u["id"], gateway=random.choice(GATEWAYS),
           reason="insufficient_funds", error_code="PAYMENT_DECLINED",
           req=rand_req())
    )

def evt_db_error():
    loggers["product-service"].error(
        f"Database connection failed" +
        kv(host="db-primary.internal", port=5432,
           error="ECONNREFUSED", retry=random.randint(1, 3), db="shopforge_prod")
    )

def evt_404():
    u = rand_user()
    pid = f"P{random.randint(900,999)}"
    loggers["api-gateway"].error(
        f"HTTP GET /api/products/{pid} 404 Not Found" +
        kv(user=u["id"], ip=u["ip"], referer="/products", req=rand_req())
    )

def evt_500():
    loggers["order-service"].error(
        f"Internal server error order={rand_order()}" +
        kv(status=500, exception="NullPointerException",
           stack="at OrderController.process(OrderController.java:142)",
           req=rand_req())
    )

def evt_timeout():
    loggers["api-gateway"].error(
        f"Upstream request timeout upstream=payment-service" +
        kv(timeout_ms=5000, elapsed_ms=5001,
           method="POST", path="/api/payment/charge", req=rand_req())
    )

def evt_cart_sync_error():
    u = rand_user()
    loggers["cart-service"].error(
        f"Cart synchronization failed" +
        kv(user=u["id"], cache_key=f"cart:{u['id']}",
           redis_error="READONLY", fallback="database", req=rand_req())
    )

# ── CRITICAL events ───────────────────────────
def evt_brute_force():
    bad_ip = f"185.220.101.{random.randint(1,254)}"
    u = random.choice(USERS)
    for _ in range(random.randint(3, 6)):
        loggers["user-service"].critical(
            f"BRUTE FORCE DETECTED — multiple failed login attempts" +
            kv(ip=bad_ip, target_user=u["id"],
               attempts=random.randint(8, 20), window_s=60,
               geo="RU", action="account_locked", req=rand_req())
        )

def evt_sql_injection():
    bad_ip = random.choice(BAD_IPS)
    loggers["api-gateway"].critical(
        f"SQL INJECTION ATTEMPT — blocked by WAF" +
        kv(ip=bad_ip, endpoint="/api/products/search",
           payload="' OR '1'='1'; DROP TABLE users; --",
           waf_rule="SQLI-001", action="blocked", geo="CN", req=rand_req())
    )

def evt_xss():
    bad_ip = random.choice(BAD_IPS)
    loggers["api-gateway"].critical(
        f"XSS ATTEMPT — sanitized and logged" +
        kv(ip=bad_ip, endpoint="/api/reviews",
           payload="<script>document.cookie</script>",
           waf_rule="XSS-002", severity="HIGH", action="sanitized", req=rand_req())
    )

def evt_mass_checkout():
    bad_ip = random.choice(BAD_IPS)
    p = rand_product()
    loggers["order-service"].critical(
        f"BOT DETECTED — mass automated checkout" +
        kv(ip=bad_ip, orders_per_minute=random.randint(45, 120),
           threshold=10, product_id=p["id"], suspected_bot=True,
           action="IP_blocked_72h", req=rand_req())
    )

def evt_unauthorized_access():
    u = random.choice(USERS)
    loggers["user-service"].critical(
        f"UNAUTHORIZED ACCESS — admin endpoint reached by non-admin" +
        kv(user=u["id"], role=u["role"], ip=u["ip"],
           endpoint="/api/admin/users", method="DELETE",
           status=403, action="blocked_and_flagged", req=rand_req())
    )

def evt_data_exfil():
    bad_ip = random.choice(BAD_IPS)
    loggers["api-gateway"].critical(
        f"DATA EXFILTRATION ATTEMPT — abnormal bulk export request" +
        kv(ip=bad_ip, endpoint="/api/users/export",
           records_requested=random.randint(50000, 200000),
           data_type="PII", action="blocked_security_team_alerted", req=rand_req())
    )


# ─────────────────────────────────────────────
# EVENT POOL  (weighted distribution)
# ─────────────────────────────────────────────
INFO_EVENTS = [
    evt_page_view, evt_page_view, evt_page_view,   # most common
    evt_search, evt_search,
    evt_product_view, evt_product_view,
    evt_add_to_cart,
    evt_payment_success,
    evt_order_track,
    evt_wishlist,
    evt_login,
    evt_logout,
]

WARN_EVENTS = [
    evt_slow_query,
    evt_high_memory,
    evt_rate_limit,
    evt_low_stock,
    evt_session_expiry,
    evt_deprecated_api,
]

ERROR_EVENTS = [
    evt_payment_fail,
    evt_db_error,
    evt_404,
    evt_500,
    evt_timeout,
    evt_cart_sync_error,
]

CRITICAL_EVENTS = [
    evt_brute_force,
    evt_sql_injection,
    evt_xss,
    evt_mass_checkout,
    evt_unauthorized_access,
    evt_data_exfil,
]


def pick_event():
    r = random.random()
    if r < CRITICAL_CHANCE:
        return random.choice(CRITICAL_EVENTS)
    elif r < CRITICAL_CHANCE + ERROR_CHANCE:
        return random.choice(ERROR_EVENTS)
    elif r < CRITICAL_CHANCE + ERROR_CHANCE + WARN_CHANCE:
        return random.choice(WARN_EVENTS)
    else:
        return random.choice(INFO_EVENTS)


# ─────────────────────────────────────────────
# STARTUP BANNER
# ─────────────────────────────────────────────
def print_banner():
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    CYAN   = "\033[36m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

    print(f"""
{BOLD}{GREEN}
 ╔══════════════════════════════════════════════════════╗
 ║        ShopForge — Dummy Log Generator v1.0          ║
 ║        E-Commerce Log Simulation for ML/SIEM         ║
 ╚══════════════════════════════════════════════════════╝
{RESET}
{CYAN} Log files created in:  ./{LOG_DIR}/{RESET}

{YELLOW}   app_{today}.log       ← all logs (main)
   access_{today}.log    ← HTTP access logs
   error_{today}.log     ← WARN / ERROR / CRITICAL
   security_{today}.log  ← auth & attack events{RESET}

{GREEN} Generating logs... Press Ctrl+C to stop.{RESET}
{BOLD}{"─"*56}{RESET}
""")


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────
def main():
    print_banner()

    # Seed startup logs
    loggers["api-gateway"].info(
        f"Application started — ShopForge v2.4.1" +
        kv(env="production", region="ap-south-1",
           pid=os.getpid(), log_dir=LOG_DIR)
    )
    loggers["user-service"].info(
        "Auth service online" + kv(jwt_secret="[REDACTED]", token_ttl_s=3600)
    )
    loggers["product-service"].info(
        "Product catalogue loaded" + kv(products=len(PRODUCTS), db="db-primary.internal")
    )

    event_count = 0
    try:
        while True:
            event_fn = pick_event()
            event_fn()
            event_count += 1

            # Print file sizes every 20 events
            if event_count % 20 == 0:
                sizes = {k: _file_size(v) for k, v in LOG_FILES.items()}
                print(f"\n  📁 Log sizes → " +
                      "  ".join(f"{k}: {s}" for k, s in sizes.items()) + "\n")

            delay = random.uniform(LOG_INTERVAL_MIN, LOG_INTERVAL_MAX)
            time.sleep(delay)

    except KeyboardInterrupt:
        print(f"\n\n  ✅ Stopped. {event_count} log events written to ./{LOG_DIR}/\n")
        for name, path in LOG_FILES.items():
            print(f"     {name:12s} → {path}  ({_file_size(path)})")
        print()


def _file_size(path):
    try:
        size = os.path.getsize(path)
        if size < 1024:       return f"{size} B"
        elif size < 1048576:  return f"{size//1024} KB"
        else:                 return f"{size//1048576} MB"
    except FileNotFoundError:
        return "0 B"


if __name__ == "__main__":
    main()
