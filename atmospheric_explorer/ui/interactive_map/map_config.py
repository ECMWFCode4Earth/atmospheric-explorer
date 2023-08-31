"""\
Mappings and configs for the interactive map.
"""

from enum import StrEnum


class MapLevels(StrEnum):
    """Levels for the interactive map"""

    CONTINENTS = "Continents"
    ORGANIZATIONS = "Organizations"
    COUNTRIES = "Countries"
    COUNTRIES_SUB = "Sub-national divisions"


map_level_shapefile_mapping = {
    MapLevels.CONTINENTS: "CONTINENT",
    MapLevels.ORGANIZATIONS: "SUBUNIT",
    MapLevels.COUNTRIES: "ADMIN",
    MapLevels.COUNTRIES_SUB: "SUBUNIT",
}


organizations = {
    "European Union (27)": [
        "Austria",
        "Bornholm",
        "Brussels Capital Region",
        "Bulgaria",
        "Corsica",
        "Croatia",
        "Cyprus",
        "Czechia",
        "Denmark",
        "Estonia",
        "Finland",
        "Flemish Region",
        "France",
        "Germany",
        "Greece",
        "Hungary",
        "Ireland",
        "Italy",
        "Latvia",
        "Lithuania",
        "Luxembourg",
        "Malta",
        "Netherlands",
        "Pantelleria",
        "Poland",
        "Portugal",
        "Romania",
        "Sardinia",
        "Sicily",
        "Slovakia",
        "Slovenia",
        "Spain",
        "Sweden",
        "Walloon Region",
    ],
    "EEA": [
        "Austria",
        "Bornholm",
        "Brussels Capital Region",
        "Bulgaria",
        "Corsica",
        "Croatia",
        "Cyprus",
        "Czechia",
        "Denmark",
        "Estonia",
        "Finland",
        "Flemish Region",
        "France",
        "Germany",
        "Greece",
        "Hungary",
        "Ireland",
        "Italy",
        "Latvia",
        "Lithuania",
        "Luxembourg",
        "Malta",
        "Netherlands",
        "Pantelleria",
        "Poland",
        "Portugal",
        "Romania",
        "Sardinia",
        "Sicily",
        "Slovakia",
        "Slovenia",
        "Spain",
        "Sweden",
        "Walloon Region",
        "Iceland",
        "Norway",
        "Liechtenstein",
    ],
}
