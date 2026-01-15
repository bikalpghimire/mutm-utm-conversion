from xml.etree.ElementTree import Element, SubElement, ElementTree


def export_to_kml(
    filepath: str,
    names,
    lats,
    lons,
    crs_name: str = "WGS84"
):
    """
    Export point data to a KML file.

    Parameters
    ----------
    filepath : str
        Output .kml file path
    names : iterable
        Point names / IDs
    lats : iterable
        Latitudes in decimal degrees
    lons : iterable
        Longitudes in decimal degrees
    crs_name : str
        Source CRS name for description
    """

    kml = Element("kml", xmlns="http://www.opengis.net/kml/2.2")
    doc = SubElement(kml, "Document")

    name = SubElement(doc, "name")
    name.text = "Coordinate Export"

    desc = SubElement(doc, "description")
    desc.text = f"Exported from {crs_name}"

    for i, (pt, lat, lon) in enumerate(zip(names, lats, lons)):
        placemark = SubElement(doc, "Placemark")

        pname = SubElement(placemark, "name")
        pname.text = str(pt) if pt else f"Point {i + 1}"

        pdesc = SubElement(placemark, "description")
        pdesc.text = f"Latitude: {lat}\nLongitude: {lon}"

        point = SubElement(placemark, "Point")
        coords = SubElement(point, "coordinates")

        # KML order is lon,lat[,alt]
        coords.text = f"{lon},{lat},0"

    ElementTree(kml).write(
        filepath,
        encoding="utf-8",
        xml_declaration=True
    )
