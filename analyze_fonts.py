#!/usr/bin/env python3
"""Analyze fonts in PRICE.PDF"""

from PyPDF2 import PdfReader
import json

def analyze_pdf_fonts(pdf_path):
    """Extract font information from PDF"""
    reader = PdfReader(pdf_path)
    
    fonts_info = []
    
    for page_num, page in enumerate(reader.pages):
        print(f"\n=== Page {page_num + 1} ===")
        
        # Get the page's resources
        if "/Resources" in page:
            resources = page["/Resources"]
            
            # Check for fonts in resources
            if "/Font" in resources:
                fonts = resources["/Font"]
                print(f"Found {len(fonts)} font(s) on this page:")
                
                for font_name, font_obj in fonts.items():
                    font_info = {}
                    font_info['name'] = font_name
                    
                    # Try to get the actual font object
                    if hasattr(font_obj, 'get_object'):
                        font_dict = font_obj.get_object()
                    else:
                        font_dict = font_obj
                    
                    # Extract font details
                    if "/BaseFont" in font_dict:
                        base_font = str(font_dict["/BaseFont"])
                        font_info['base_font'] = base_font
                        print(f"  - {font_name}: {base_font}")
                        
                        # Try to determine font family and style
                        if "Helvetica" in base_font:
                            font_info['family'] = 'Helvetica'
                            if "Bold" in base_font:
                                font_info['style'] = 'Bold'
                            elif "Oblique" in base_font or "Italic" in base_font:
                                font_info['style'] = 'Italic'
                            else:
                                font_info['style'] = 'Regular'
                        elif "Times" in base_font:
                            font_info['family'] = 'Times'
                        elif "Courier" in base_font:
                            font_info['family'] = 'Courier'
                    
                    if "/Subtype" in font_dict:
                        font_info['subtype'] = str(font_dict["/Subtype"])
                        print(f"    Subtype: {font_dict['/Subtype']}")
                    
                    if "/Encoding" in font_dict:
                        font_info['encoding'] = str(font_dict["/Encoding"])
                        print(f"    Encoding: {font_dict['/Encoding']}")
                    
                    fonts_info.append(font_info)
        
        # Try to extract text with positioning to guess font sizes
        try:
            text = page.extract_text()
            if text:
                print(f"\nSample text from page: {text[:200]}...")
        except:
            pass
    
    return fonts_info

if __name__ == "__main__":
    pdf_path = "PRICE.PDF"
    print(f"Analyzing fonts in {pdf_path}...")
    
    fonts = analyze_pdf_fonts(pdf_path)
    
    print("\n=== Summary of Fonts Found ===")
    unique_fonts = {}
    for font in fonts:
        if 'base_font' in font:
            base = font['base_font']
            if base not in unique_fonts:
                unique_fonts[base] = font
    
    for base_font, info in unique_fonts.items():
        print(f"\nFont: {base_font}")
        if 'family' in info:
            print(f"  Family: {info['family']}")
        if 'style' in info:
            print(f"  Style: {info['style']}")
    
    # Save to JSON for reference
    with open('price_pdf_fonts.json', 'w') as f:
        json.dump(fonts, f, indent=2)
    print(f"\nFont information saved to price_pdf_fonts.json")