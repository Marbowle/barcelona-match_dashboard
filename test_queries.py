import queries

def main():
    try:
        df = queries.get_teams()
        print("✅ Zapytanie działa, zwrócono DataFrame")
        print("Kształt:", df.shape)
        print("Pierwsze 5 wierszy:")
        print(df.head())
    except Exception as e:
        print("❌ Błąd:", e)

if __name__ == "__main__":
    main()
