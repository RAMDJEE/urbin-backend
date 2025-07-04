from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def extract_gps_from_image(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if not exif_data:
            return None

        gps_info = {}
        for tag, value in exif_data.items():
            decoded = TAGS.get(tag)
            if decoded == "GPSInfo":
                for t in value:
                    sub_decoded = GPSTAGS.get(t)
                    gps_info[sub_decoded] = value[t]

        def dms_to_dd(d, m, s, ref):
            dd = d + m / 60.0 + s / 3600.0
            if ref in ["S", "W"]:
                dd *= -1
            return dd

        if "GPSLatitude" in gps_info and "GPSLatitudeRef" in gps_info \
           and "GPSLongitude" in gps_info and "GPSLongitudeRef" in gps_info:
            lat_dms = gps_info["GPSLatitude"]
            lon_dms = gps_info["GPSLongitude"]
            lat = dms_to_dd(lat_dms[0][0]/lat_dms[0][1],
                            lat_dms[1][0]/lat_dms[1][1],
                            lat_dms[2][0]/lat_dms[2][1],
                            gps_info["GPSLatitudeRef"])
            lon = dms_to_dd(lon_dms[0][0]/lon_dms[0][1],
                            lon_dms[1][0]/lon_dms[1][1],
                            lon_dms[2][0]/lon_dms[2][1],
                            gps_info["GPSLongitudeRef"])
            return (lat, lon)
        else:
            return None
    except Exception as e:
        print(f"Erreur EXIF GPS: {e}")
        return None
