#!/usr/bin/env python3
"""Analyze text sizes and positions in PRICE.PDF using pdfplumber"""

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("pdfplumber not installed. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "pdfplumber"])
    import pdfplumber

def analyze_text_details(pdf_path):
    """Extract detailed text information including size and position"""
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            print(f"\n=== Page {page_num + 1} ===")
            print(f"Page size: {page.width} x {page.height}")
            
            # Extract characters with their properties
            chars = page.chars
            
            # Group by unique font and size combinations
            font_sizes = {}
            
            for char in chars:
                if 'fontname' in char and 'size' in char:
                    font_key = f"{char['fontname']} - Size: {char['size']:.1f}"
                    if font_key not in font_sizes:
                        font_sizes[font_key] = {
                            'count': 0,
                            'sample_text': [],
                            'positions': []
                        }
                    font_sizes[font_key]['count'] += 1
                    
                    # Collect sample text
                    if len(font_sizes[font_key]['sample_text']) < 5:
                        font_sizes[font_key]['sample_text'].append(char['text'])
                    
                    # Collect position info for first few instances
                    if len(font_sizes[font_key]['positions']) < 3:
                        font_sizes[font_key]['positions'].append({
                            'x': round(char['x0'], 1),
                            'y': round(page.height - char['top'], 1),  # Convert to PDF coordinates
                            'text': char['text']
                        })
            
            print("\nFont and Size Combinations Found:")
            for font_key, info in sorted(font_sizes.items()):
                print(f"\n{font_key}")
                print(f"  Character count: {info['count']}")
                print(f"  Sample: {''.join(info['sample_text'][:20])}")
                if info['positions']:
                    print(f"  Sample positions:")
                    for pos in info['positions'][:3]:
                        print(f"    ({pos['x']}, {pos['y']}): '{pos['text']}'")
            
            # Look for specific text we're interested in
            print("\n=== Looking for specific fields ===")
            text = page.extract_text()
            
            # Find phone field area
            if "+370" in text or "TEL" in text.upper() or "PHONE" in text.upper():
                print("Found phone-related text")
                for char in chars:
                    if '+' in char.get('text', '') or '370' in char.get('text', ''):
                        print(f"  Phone char: '{char.get('text')}' at ({char.get('x0', 0):.1f}, {page.height - char.get('top', 0):.1f}) size: {char.get('size', 0):.1f}")
            
            # Find Lizingo fields
            if "Lizingo" in text or "lizingo" in text:
                print("Found Lizingo-related text")
                for char in chars:
                    text_lower = char.get('text', '').lower()
                    if any(word in text_lower for word in ['l', 'i', 'z', 'n', 'g', 'o']):
                        # This is crude but helps find the area
                        if char.get('y0', 0) > 400 and char.get('y0', 0) < 450:  # Approximate area
                            pass  # Could print details if needed
            
            # Try to find text at specific positions we're writing to
            print("\n=== Text at our writing positions ===")
            target_positions = [
                (140, 560, "Phone"),
                (215, 438, "Lizingo laikotarpis"),
                (215, 423, "Pradinė įmoka")
            ]
            
            for target_x, target_y, field_name in target_positions:
                print(f"\nNear {field_name} position ({target_x}, {target_y}):")
                for char in chars:
                    char_x = char.get('x0', 0)
                    char_y = page.height - char.get('top', 0)
                    
                    # Check if character is near our target position
                    if abs(char_x - target_x) < 50 and abs(char_y - target_y) < 20:
                        print(f"  Found: '{char.get('text')}' at ({char_x:.1f}, {char_y:.1f})")
                        print(f"    Font: {char.get('fontname')}, Size: {char.get('size', 0):.1f}")

if __name__ == "__main__":
    pdf_path = "PRICE.PDF"
    print(f"Analyzing text details in {pdf_path}...")
    
    analyze_text_details(pdf_path)