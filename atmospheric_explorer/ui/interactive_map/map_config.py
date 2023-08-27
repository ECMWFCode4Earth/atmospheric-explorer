from enum import StrEnum


class MapLevels(StrEnum):
    CONTINENTS = "Continents"
    ORGANIZATIONS = "Organizations"
    COUNTRIES = "Countries"
    COUNTRIES_SUB = "Sub-national divisions"


map_level_shapefile_mapping = {
    MapLevels.CONTINENTS: "CONTINENT",
    MapLevels.ORGANIZATIONS: "ADMIN",
    MapLevels.COUNTRIES: "ADMIN",
    MapLevels.COUNTRIES_SUB: "SUBUNIT",
}


organizations = {
    "European Union (27)": [
        "Austria",
        "Belgium",
        "Bulgaria",
        "Croatia",
        "Cyprus",
        "Czechia",
        "Denmark",
        "Estonia",
        "Finland",
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
        "Poland",
        "Portugal",
        "Romania",
        "Slovakia",
        "Slovenia",
        "Spain",
        "Sweden",
    ],
    "EEA": [
        "Austria",
        "Belgium",
        "Bulgaria",
        "Croatia",
        "Cyprus",
        "Czechia",
        "Denmark",
        "Estonia",
        "Finland",
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
        "Poland",
        "Portugal",
        "Romania",
        "Slovakia",
        "Slovenia",
        "Spain",
        "Sweden",
        "Iceland",
        "Norway",
        "Liechtenstein",
    ],
}
