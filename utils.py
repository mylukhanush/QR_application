"""
Utility functions for QR code generation
"""
import qrcode
from io import BytesIO
import base64


class QRCodeGenerator:
    """
    Handles QR code generation for the application
    - ONE registration QR code pointing to registration endpoint
    - ONE entry QR code pointing to entry verification endpoint
    - QR codes are permanent and never expire
    - Multiple users can scan the same QR code
    """

    @staticmethod
    def generate_qr_code(data, version=1, error_correction='M'):
        """
        Generate a QR code from given data
        
        Args:
            data (str): The data to encode in the QR code (URL)
            version (int): QR code version (1-40, where higher = larger)
            error_correction (str): Error correction level ('L', 'M', 'Q', 'H')
        
        Returns:
            PIL.Image: QR code image object
        """
        qr = qrcode.QRCode(
            version=version,
            error_correction=getattr(qrcode.constants, f'ERROR_CORRECT_{error_correction}'),
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color='black', back_color='white')
        return img

    @staticmethod
    def image_to_base64(image):
        """
        Convert PIL Image to base64 string for embedding in HTML
        
        Args:
            image (PIL.Image): Image object
        
        Returns:
            str: Base64 encoded image string
        """
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f'data:image/png;base64,{img_base64}'

    @staticmethod
    def generate_registration_qr(app_url):
        """
        Generate permanent registration QR code
        - Points to the registration form endpoint
        - Never expires
        - Multiple users can scan it
        
        Args:
            app_url (str): Base URL of the application
        
        Returns:
            str: Base64 encoded QR code image
        """
        registration_url = f'{app_url}/register'
        img = QRCodeGenerator.generate_qr_code(registration_url)
        return QRCodeGenerator.image_to_base64(img)

    @staticmethod
    def generate_entry_qr(app_url):
        """
        Generate permanent entry/check-in QR code
        - Points to the entry verification endpoint
        - Never expires
        - Multiple users can scan it
        
        Args:
            app_url (str): Base URL of the application
        
        Returns:
            str: Base64 encoded QR code image
        """
        entry_url = f'{app_url}/entry'
        img = QRCodeGenerator.generate_qr_code(entry_url)
        return QRCodeGenerator.image_to_base64(img)
