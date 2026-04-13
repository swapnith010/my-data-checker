import pandas as pd

def analyze_file(path):
    try:
        # Load file (limiting rows to prevent Render crash)
        if path.endswith('.xlsx') or path.endswith('.xls'):
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path, nrows=5000, low_memory=True)
            
        rows, cols = df.shape
        error_list = []
        
        # --- 1. FIND MISSING VALUES ---
        null_mask = df.isnull().stack()
        null_locations = null_mask[null_mask]
        for row_idx, col_name in null_locations.index:
            error_list.append(f"Row {row_idx + 2}: Column '{col_name}' is empty.")

        # --- 2. FIND DUPLICATES ---
        duplicates = df.duplicated(keep=False)
        duplicate_rows = df[duplicates]
        if not duplicate_rows.empty:
            error_list.append(f"Found {len(duplicate_rows)} rows that are exact duplicates of others.")

        # --- 3. DATA TYPE CHECK (Optional but useful) ---
        # Example: Checks if numeric columns contain non-numeric text
        for col in df.select_dtypes(include=['number']).columns:
            # We already checked for nulls, so we check for 'None' or invalid entries
            if df[col].astype(str).str.contains(r'[?#@]', regex=True).any():
                error_list.append(f"Column '{col}': Contains suspicious symbols or junk characters.")

        # Calculate Quality Score
        # Penalty is based on number of unique errors found
        total_errors = len(error_list)
        quality = max(0, 100 - (total_errors / (rows + 1) * 100))

        return {
            "rows": rows,
            "cols": cols,
            "errors": total_errors,
            "quality": round(quality, 2),
            "error_list": error_list[:150] # Show up to 150 errors
        }
    except Exception as e:
        return {"rows": 0, "cols": 0, "errors": "Scan Error", "quality": 0, "error_list": [str(e)]}