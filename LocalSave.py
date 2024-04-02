from PIL import Image
import piexif
from mutagen.mp4 import MP4
import os
import shutil
import re
from dotenv import load_dotenv

class LocalSave:

    def __init__(self, source='.', dest='./media') -> None:
        self.source = source
        self.dest = dest
        load_dotenv()
        self.lon = float(os.getenv('LOCAL_LON'))
        self.lat = float(os.getenv('LOCAL_LAT'))
        self.tag = os.getenv('LOCAL_TAG')

        # Prepare GPS data
        self.gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: 'N' if self.lat >= 0 else 'S',
            piexif.GPSIFD.GPSLatitude: self._convert_to_degrees(self.lat),
            piexif.GPSIFD.GPSLongitudeRef: 'E' if self.lon >= 0 else 'W',
            piexif.GPSIFD.GPSLongitude: self._convert_to_degrees(self.lon),
        }

    def move(self):
        files = [file for file in os.listdir(self.source) if file.endswith('.jpg') or file.endswith('.mp4')]
        for file in files:
            title = re.search(r'^\d{8}_\d{6}_(.*?)\d*\.(jpg|mp4)$', file).group(1)
            datetime = re.search(r'(^\d{8}_\d{6})_(.*?)\d*\.(jpg|mp4)$', file).group(1)
            destfile = os.path.join(self.dest, file)
            tags = f'{self.tag}, {title}'
            
            if file.endswith('.jpg'):
                exif_dict = {"GPS": self.gps_ifd}
                exif_dict['0th'] = {piexif.ImageIFD.DateTime: datetime}
                exif_dict['Exif'] = {piexif.ExifIFD.UserComment: tags.encode('utf-8')}
                exif_bytes = piexif.dump(exif_dict)
                
                img = Image.open(file)
                img.save(file, "jpeg", exif=exif_bytes)

            elif file.endswith('.mp4'):
                video = MP4(file)
                # Read metadata
                print(video.tags)
                # Modify or add metadata
                video['\xa9nam'] = title
                video['\xa9ART'] = title
                video['\xa9alb'] = 'BirdBuddy'
                video['\xa9day'] = datetime[:4]
                video['desc'] = tags
                video['\xa9gen'] = 'Vogel'
                video.save()

            shutil.move(file, destfile)


    def _convert_to_degrees(self, value):
        """
        Helper function to convert decimal degrees into degrees, minutes, and seconds
        """
        is_positive = value >= 0
        value = abs(value)
        d = int(value)
        m = int((value - d) * 60)
        s = (value - d - m/60) * 3600.00

        # Ensure seconds are represented as a fraction (the EXIF standard expects integers)
        # The multiplication and division by 100 is to manage the decimal part of the seconds
        s = int(s * 100)

        # Return a tuple of tuples (degrees, minutes, seconds), each represented as a fraction
        return [(d, 1), (m, 1), (s, 100)]




