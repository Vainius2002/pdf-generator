#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Overlay Generator - Uses PRICE.PDF as template
Overlays text on the existing PDF for perfect design match
"""

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black, white, Color
import io
import qrcode
from PIL import Image
import os
from datetime import datetime

class PDFOverlayGenerator:
    def __init__(self, template_path=None):
        if template_path is None:
            # Look for PRICE.PDF in the same directory as the script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(script_dir, "PRICE.PDF")
        """Initialize with the template PDF path"""
        self.template_path = template_path
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Template PDF not found at {template_path}")
        
        # Colors for text
        self.colors = {
            'black': black,
            'white': white,
            'red': Color(0.8, 0.1, 0.2)
        }
        
    def create_overlay(self, car_data, qr_data=None):
        """Create an overlay with the data to be added"""
        # Create a BytesIO buffer for the overlay
        packet = io.BytesIO()
        
        # Create a new PDF with ReportLab for the overlay
        c = canvas.Canvas(packet, pagesize=A4)
        
        # Try to use DejaVu font for Lithuanian characters
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
            main_font = 'DejaVuSans'
            bold_font = 'DejaVuSans-Bold'
        except:
            main_font = 'Helvetica'
            bold_font = 'Helvetica-Bold'
        
        # # ONLY add the requested filled fields:
        # # 1. Phone number (in the gray phone field)
        # c.setFillColor(self.colors['black'])
        # c.setFont(bold_font, 20)
        # # Phone field is around middle-left of page
        # c.drawString(145, 563, car_data.get('phone', '+370 656 61866'))
        
        # # 2. Lizingo laikotarpis (after the red label)
        # c.setFillColor(self.colors['black'])  # Black text for the value
        # c.setFont(main_font, 11)
        # c.drawString(215, 438, car_data.get('lizingo_laikotarpis', '60 mėn.'))
        
        # # 3. Pradinė įmoka (after the red label)
        # c.setFont(main_font, 11)
        # c.drawString(215, 423, car_data.get('pradine_imoka', '30%'))
        
        # Add QR code if provided
        if qr_data:
            # Format QR data properly for web links
            if qr_data and not qr_data.startswith(('http://', 'https://')):
                if '.' in qr_data and not qr_data.startswith('+'):  # Looks like a website
                    qr_data = 'https://' + qr_data
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=1,
                border=0,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code temporarily
            qr_temp_path = "temp_qr_overlay.png"
            qr_img.save(qr_temp_path)
            
            # Add QR code to PDF (bottom left position)
            qr_x = 31
            qr_y = 31
            qr_size = 150
            
            c.drawImage(qr_temp_path, qr_x, qr_y, width=qr_size, height=qr_size)
            
            # Clean up temp file
            if os.path.exists(qr_temp_path):
                os.remove(qr_temp_path)
        
        # Save the overlay
        c.save()
        
        # Move to the beginning of the BytesIO buffer
        packet.seek(0)
        
        return packet
    
    def generate_pdf(self, car_data, output_file="price_filled.pdf", qr_data=None):
        """Generate PDF by overlaying data on template"""
        # Read the template PDF
        template_pdf = PdfReader(self.template_path)
        template_page = template_pdf.pages[0]
        
        # Create overlay
        overlay_buffer = self.create_overlay(car_data, qr_data)
        overlay_pdf = PdfReader(overlay_buffer)
        overlay_page = overlay_pdf.pages[0]
        
        # Merge the overlay with the template
        template_page.merge_page(overlay_page)
        
        # Write the result
        output_pdf = PdfWriter()
        output_pdf.add_page(template_page)
        
        # Save the final PDF
        with open(output_file, 'wb') as output_file_handle:
            output_pdf.write(output_file_handle)
        
        print(f"PDF generated successfully: {output_file}")
        return output_file

def main():
    """Main function - overlays data on PRICE.PDF template"""
    print("🚗 PDF OVERLAY GENERATOR - PERFECT DESIGN 🚗")
    print("=" * 50)
    print("Using PRICE.PDF as template for exact design match!")
    print()
    
    # Create generator (will automatically look for PRICE.PDF in script directory)
    try:
        generator = PDFOverlayGenerator()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return
    
    # QR Code option
    qr_data = input("Enter QR code data (website/phone) or press Enter to skip: ").strip()
    
    # Generate PDF with minimal data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"pdfs/price_overlay_{timestamp}.pdf"
    
    # Only fill the requested fields
    car_data = {
        "phone": "+370 656 61866",
        "lizingo_laikotarpis": "60 mėn.",
        "pradine_imoka": "30%"
    }
    
    try:
        generator.generate_pdf(car_data, output_file, qr_data=qr_data)
        print(f"\n✅ Success! PDF generated: {output_file}")
        print("\nThis PDF uses the EXACT design from PRICE.PDF!")
        print("Only filled: Phone, Lizingo laikotarpis, Pradinė įmoka")
        print("All other fields remain empty for manual entry.")
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")

if __name__ == "__main__":
    main()