"""
导出 KOL 报告到 Excel / Google Sheets / CSV
"""
import os, json, csv
import pandas as pd

def export_to_csv(df, filename="kol_report.csv"):
    """导出为 CSV 文件"""
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"CSV saved: {filename}")

def export_to_excel(df, filename="kol_report.xlsx"):
    """导出为 Excel 文件"""
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="KOL Ranking", index=False)
        # 添加统计表
        stats = df["spectrum_category"].value_counts().reset_index()
        stats.columns = ["Category", "Count"]
        stats.to_excel(writer, sheet_name="Category Stats", index=False)
    print(f"Excel saved: {filename}")

def export_to_google_sheets(df, sheet_name="KOL Report"):
    """导出到 Google Sheets"""
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.create(sheet_name)
        worksheet = sheet.get_worksheet(0)
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"Google Sheet created: {sheet.url}")
    except ImportError:
        print("gspread not installed. Install with: pip install gspread oauth2client")

if __name__ == "__main__":
    # 示例使用
    df = pd.DataFrame({
        "username": ["test1", "test2"],
        "kol_score": [88, 72],
        "spectrum_category": ["Star KOL", "Rising Star"],
    })
    export_to_csv(df)
    export_to_excel(df)
