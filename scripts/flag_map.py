"""
FIFA TLA (3-letter code) → ISO 3166-1 alpha-2 mapping for flagcdn.com flags.
Used by download_flags.py and generate_page.py.
"""

TLA_TO_ISO: dict[str, str] = {
    # Host nations
    "USA": "us", "CAN": "ca", "MEX": "mx",
    # CONMEBOL
    "ARG": "ar", "BRA": "br", "COL": "co", "URU": "uy",
    "ECU": "ec", "PAR": "py", "CHI": "cl", "PER": "pe",
    "BOL": "bo", "VEN": "ve",
    # UEFA
    "ENG": "gb-eng", "GER": "de", "FRA": "fr", "ESP": "es",
    "POR": "pt", "NED": "nl", "ITA": "it", "CRO": "hr",
    "AUT": "at", "SUI": "ch", "SRB": "rs", "ALB": "al",
    "HUN": "hu", "POL": "pl", "DEN": "dk", "NOR": "no",
    "SCO": "gb-sct", "WAL": "gb-wls", "NIR": "gb-nir",
    "BEL": "be", "SWE": "se", "TUR": "tr", "GRE": "gr",
    "ROU": "ro", "SVK": "sk", "SVN": "si", "UKR": "ua",
    "CZE": "cz", "ISL": "is", "FIN": "fi", "IRL": "ie",
    "BIH": "ba", "MKD": "mk", "MNE": "me", "GEO": "ge",
    "AZE": "az", "ARM": "am", "LUX": "lu", "BUL": "bg",
    "ISR": "il",
    # CAF (Africa)
    "MAR": "ma", "SEN": "sn", "GHA": "gh", "CMR": "cm",
    "NGA": "ng", "CIV": "ci", "TUN": "tn", "EGY": "eg",
    "ALG": "dz", "RSA": "za", "ZAF": "za", "ETH": "et",
    "GNQ": "gq", "CGO": "cg", "ZIM": "zw", "GAB": "ga",
    "CPV": "cv", "COM": "km", "UGA": "ug", "ZAM": "zm",
    # AFC (Asia)
    "JPN": "jp", "KOR": "kr", "AUS": "au", "IRN": "ir",
    "KSA": "sa", "QAT": "qa", "CHN": "cn", "IRQ": "iq",
    "JOR": "jo", "UZB": "uz", "OMN": "om", "BHR": "bh",
    "PAL": "ps", "SYR": "sy", "KWT": "kw", "YEM": "ye",
    "THA": "th", "VIE": "vn", "IND": "in", "MYS": "my",
    "IDN": "id", "PHI": "ph",
    # CONCACAF
    "CRC": "cr", "HON": "hn", "GUA": "gt", "JAM": "jm",
    "PAN": "pa", "TRI": "tt", "CUB": "cu", "HAI": "ht",
    "DOM": "do", "ANT": "ag", "BLZ": "bz", "SLV": "sv",
    "NCA": "ni", "MTQ": "mq", "GLP": "gp", "CUW": "cw",
    # OFC
    "NZL": "nz", "FIJ": "fj", "PNG": "pg", "VAN": "vu",
}


def tla_to_iso(tla: str) -> str | None:
    """Return ISO alpha-2 code for given FIFA TLA, or None if unknown."""
    return TLA_TO_ISO.get(tla.upper())


def flag_url(tla: str, local_flags_dir: str | None = None) -> str:
    """
    Return URL or path for a country flag.
    Checks local file first (local_flags_dir/{ISO}.png), then falls back to flagcdn.com CDN.
    """
    import os
    iso = tla_to_iso(tla)
    if not iso:
        return ""

    if local_flags_dir:
        local_path = os.path.join(local_flags_dir, f"{iso.upper()}.png")
        if os.path.exists(local_path):
            return local_path

    return f"https://flagcdn.com/w160/{iso}.png"
