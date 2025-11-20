from src.data_cleaner import build_clean_dataset, CLEANED_FILE

def test_build_clean_dataset_creates_file_and_rows():
    df = build_clean_dataset()
    assert len(df) > 0
    assert CLEANED_FILE.exists()
    assert {"name", "address", "city"}.issubset(df.columns)
