import pandas as pd

def analyze_file(path):
    try:
        # Load file (limiting rows to prevent Render RAM crash)
        if path.endswith('.xlsx') or path.endswith('.xls'):
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path, nrows=5000, low_memory=True)
            
        rows, cols = df.shape
        error_list = []
        
        # 1. FIND MISSING VALUES (Detailed Location)
        null_mask = df.isnull().stack()
        null_locations = null_mask[null_mask]
        for row_idx, col_name in null_locations.index:
            error_list.append(f"Row {row_idx + 2}: Column '{col_name}' is empty.")

        # 2. FIND DUPLICATES
        dupe_count = int(df.duplicated().sum())
        if dupe_count > 0:
            error_list.append(f"Found {dupe_count} duplicate rows in this dataset.")

        # Calculate Quality Score (Penalty based on error volume)
        total_errors = len(error_list)
        quality = max(0, 100 - (total_errors / (rows + 1) * 100))

        return {
            "rows": rows,
            "cols": cols,
            "errors": total_errors,
            "quality": round(quality, 2),
            "error_list": error_list[:150] # Show up to 150 specific errors
        }
    except Exception as e:
        return {"rows": 0, "cols": 0, "errors": "Scan Error", "quality": 0, "error_list": [str(e)]}