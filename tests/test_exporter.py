
import json
from src.exporters.endnote import to_ris

def test_endnote_export_minimal():
    # minimal PFW-like work
    work = {
        "applicationNumberText": "14412875",
        "applicationMetaData": {
            "inventionTitle": "Sample Invention",
            "patentNumber": "US1234567B2",
            "filingDate": "2013-01-01",
            "grantDate": "2017-01-01",
            "examinerNameText": "DOE, JOHN",
            "groupArtUnitNumber": "1234"
        },
        "recordAttorney": {
            "attorneyBag": [
                {"firstName":"Jane","lastName":"Attorney","registrationNumber":"12,345"}
            ]
        },
        "correspondenceAddressBag": [
            {"nameLineOneText":"Law Firm LLP","addressLineOneText":"123 Main St","cityName":"Alexandria","geographicRegionCode":"VA","postalCode":"22314","countryName":"USA"}
        ]
    }
    ris = to_ris(work, "src/exporters/endnote_field_map.uspto_pfw.json")
    assert "TY  - PAT" in ris
    assert "TI  - Sample Invention" in ris
    assert "AN  - 14412875" in ris or "AN  - " in ris
