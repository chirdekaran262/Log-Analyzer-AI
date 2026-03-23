# AI Log Analyzer - Usage Guide

## Two Ways to Analyze Logs

### 1?? **Upload Method** (Manual)
- Go to `http://localhost:8000`
- Click on the **Upload Log File** card
- Drag & drop or click to select a `.log`, `.txt`, or `.out` file
- Click **Analyze** button
- View results on the dashboard

### 2?? **Path Method** (Automatic) ? NEW
- Go to `http://localhost:8000`
- Click on the **Analyze from Path** card
- Enter the folder or file path:
  ```
  C:\path\to\logs
  C:\another\project\logs\app.log
  ```
- Click **Analyze Folder/File** button
- Results load automatically

---

## Command Line Usage

### Analyze Single Log File
```powershell
python analyze_logs.py "C:\path\to\logfile.log"
```

### Analyze Entire Folder
```powershell
python analyze_logs.py "C:\path\to\logs"
```

### Example
```powershell
python analyze_logs.py "C:\Users\KARAN\OneDrive\Desktop\ai-log-analyzer\logs"
```

---

## API Endpoints

### Upload Endpoint
```
POST /analyze
Form data: file (multipart)
```

### Path Analysis Endpoint  
```
GET /analyze-path?path=C:\path\to\logs
```

**Example:**
```
http://localhost:8000/analyze-path?path=C:\Users\KARAN\Projects\app\logs
```

---

## What Gets Analyzed

? **Log Statistics**
- Total logs parsed
- Error count & ratio
- Warning count & ratio
- Critical events
- Failed login attempts
- Unique IP addresses

? **Rule-Based Alerts**
- High error rates
- Brute-force attacks
- Warning storms
- Critical events

? **ML Anomaly Detection**
- Unsupervised anomaly scoring
- Anomaly ratio
- Average anomaly score
- Uses pre-trained model

? **Risk Assessment**
- ?? LOW | ?? MEDIUM | ?? HIGH | ?? CRITICAL

---

## Starting the Server

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open: `http://localhost:8000`

---

## Log File Formats Supported

- TIMESTAMP LEVEL MESSAGE
  ```
  2026-03-02 10:30:45 INFO User login success
  ```

- [TIMESTAMP] [LEVEL] MESSAGE
  ```
  [2026-03-02 10:30:45] [ERROR] Database connection failed
  ```

- ISO Format
  ```
  2026-03-02T10:30:45Z ERROR Some error
  ```

---

## Tips

?? **Folder Analysis** - Automatically processes all `.log`, `.txt`, and `.out` files  
?? **Model Reuse** - Your trained ML model is saved and reused for all analyses  
?? **Fast Processing** - CLI method is fastest for batch operations  
?? **No Manual Steps** - Just provide path and get instant results!
