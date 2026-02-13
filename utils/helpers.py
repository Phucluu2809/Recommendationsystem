def time_bucket(year: int) -> str:
    if year >= 2024:
        return "recent"
    elif year >= 2022:
        return "mid"
    return "old"
