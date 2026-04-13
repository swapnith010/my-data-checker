import pandas as pd

def analyze_file(path):
    try:
        # Use low_memory=True and only read the first 50,000 rows to save RAM
        if path.endswith('.xlsx') or path.endswith('.xls'):
            df = pd.read_excel(path)
        else:
            # chunksize can be used for even bigger files, but let's limit total rows for Free Tier
            df = pd.read_csv(path, nrows=50000, low_memory=True)
            
        rows, cols = df.shape
        null_counts = int(df.isnull().sum().sum())
        
        error_list = []
        if null_counts > 0:
            error_list.append(f"Detected {null_counts} missing values.")
        
        # Skip duplicate check for very large files to save memory
        if rows < 10000:
            dupes = int(df.duplicated().sum())
            if dupes > 0:
                error_list.append(f"Found {dupes} duplicate rows.")
                null_counts += dupes

        quality = max(0, 100 - (null_counts / (rows * cols + 1) * 100))

        return {
            "rows": rows,
            "cols": cols,
            "errors": null_counts,
            "quality": round(quality, 2),
            "error_list": error_list
        }
    except Exception as e:
        return {"rows": 0, "cols": 0, "errors": "Limit Exceeded", "quality": 0, "error_list": ["File too large for free tier or " + str(e)]}