import pandas as pd

def analyze_file(path):
    try:
        # Detect file type
        if path.endswith('.xlsx') or path.endswith('.xls'):
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)
            
        rows, cols = df.shape
        null_counts = int(df.isnull().sum().sum())
        
        error_list = []
        if null_counts > 0:
            error_list.append(f"Detected {null_counts} missing values across all columns.")
        
        # Check for duplicates
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
        return {"rows": 0, "cols": 0, "errors": "N/A", "quality": 0, "error_list": [str(e)]}