from PIL import Image, ExifTags
import io

class MetadataService:
    def __init__(self):
        # Known software signatures that indicate high probability of fraud
        self.suspicious_software = ["photoshop", "canva", "lightroom", "gimp"]

    def extract_anomalies(self, image_bytes: bytes) -> int:
        """
        Reads image EXIF data.
        Returns the number of detected anomalies.
        """
        anomalies = 0
        try:
            image = Image.open(io.BytesIO(image_bytes))
            exif_data = image.getexif()
            
            if not exif_data:
                # No EXIF data is common for screenshots, so it's not an anomaly by itself
                return 0

            # Iterate through EXIF tags
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                
                # Check the "Software" tag
                if tag_name == "Software" and isinstance(value, str):
                    software_lower = value.lower()
                    if any(suspicious in software_lower for suspicious in self.suspicious_software):
                        # Huge red flag: image was manipulated in an editor
                        print(f"Metadata Anomaly: Suspicious software detected -> {value}")
                        anomalies += 2  # High penalty
                        
        except Exception as e:
            print(f"Metadata Extraction Warning: {e}")
            
        return anomalies
