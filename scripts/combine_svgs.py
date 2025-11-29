#!/usr/bin/env python3
"""
SVG Combiner Script for Multi-page Draw.io Conversion

This script combines multiple SVG files vertically into a single SVG file.
It directly manipulates SVG XML for better compatibility and simpler dependencies.

Usage:
    python3 combine_svgs.py <output_file> <input_file1> <input_file2> ...

Requirements:
    - Python 3 (standard library only)
"""

import sys
import os
import xml.etree.ElementTree as ET
import re


def parse_dimension(dim_str):
    """Parse dimension string and convert to pixels."""
    if not dim_str:
        return 100.0
    
    # Remove any whitespace
    dim_str = dim_str.strip()
    
    # Handle different units
    if dim_str.endswith('px'):
        return float(dim_str[:-2])
    elif dim_str.endswith('pt'):
        return float(dim_str[:-2]) * 1.333333  # 1pt = 1.333px
    elif dim_str.endswith('in'):
        return float(dim_str[:-2]) * 96  # 1in = 96px
    elif dim_str.endswith('mm'):
        return float(dim_str[:-2]) * 3.779528  # 1mm = 3.779px
    elif dim_str.endswith('cm'):
        return float(dim_str[:-2]) * 37.79528  # 1cm = 37.795px
    else:
        # Try to parse as number (assume pixels)
        try:
            return float(dim_str)
        except ValueError:
            return 100.0


def get_svg_dimensions(svg_file):
    """Extract width and height from SVG file."""
    try:
        tree = ET.parse(svg_file)
        root = tree.getroot()
        
        # Get dimensions from root element
        width = root.get('width', '100')
        height = root.get('height', '100')
        
        # Parse viewBox if width/height are not available or are percentages
        if '%' in width or '%' in height or not width or not height:
            viewbox = root.get('viewBox', '')
            if viewbox:
                parts = viewbox.split()
                if len(parts) >= 4:
                    width = parts[2]
                    height = parts[3]
        
        return parse_dimension(width), parse_dimension(height)
    except Exception as e:
        print(f"Warning: Could not parse dimensions from {svg_file}: {e}")
        return 400.0, 300.0  # Default dimensions


def read_svg_content(svg_file):
    """Read SVG file and return the content inside the root SVG element."""
    try:
        tree = ET.parse(svg_file)
        root = tree.getroot()
        
        # Get all child elements of the SVG root
        content_elements = list(root)
        
        # Also preserve any text content and attributes that might be important
        return root, content_elements
    except Exception as e:
        print(f"Error reading SVG file {svg_file}: {e}")
        return None, None


def combine_svgs(output_file, input_files, spacing=20):
    """
    Combine multiple SVG files vertically into a single SVG.
    
    Args:
        output_file: Path to output SVG file
        input_files: List of input SVG file paths
        spacing: Vertical spacing between SVGs in pixels
    """
    if not input_files:
        print("Error: No input files provided")
        return False
    
    try:
        # Calculate total dimensions and collect SVG data
        svg_data = []
        total_height = 0
        max_width = 0
        
        for svg_file in input_files:
            if not os.path.exists(svg_file):
                print(f"Warning: File {svg_file} does not exist, skipping")
                continue
                
            width, height = get_svg_dimensions(svg_file)
            root, content = read_svg_content(svg_file)
            
            if root is None or content is None:
                print(f"Warning: Could not read content from {svg_file}, skipping")
                continue
            
            svg_data.append({
                'file': svg_file,
                'width': width,
                'height': height,
                'y_offset': total_height,
                'root': root,
                'content': content
            })
            
            max_width = max(max_width, width)
            total_height += height + spacing
            print(f"Added {svg_file}: {width}x{height} at y-offset {total_height - height - spacing}")
        
        # Remove the last spacing
        if svg_data:
            total_height -= spacing
        
        if not svg_data:
            print("Error: No valid SVG files found")
            return False
        
        # Create the combined SVG
        # Start with SVG root element
        combined_svg = ET.Element('svg')
        combined_svg.set('xmlns', 'http://www.w3.org/2000/svg')
        combined_svg.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
        combined_svg.set('width', str(int(max_width)))
        combined_svg.set('height', str(int(total_height)))
        combined_svg.set('viewBox', f'0 0 {int(max_width)} {int(total_height)}')
        
        # Add each SVG's content in a group with appropriate translation
        for svg_info in svg_data:
            # Create a group for this SVG's content
            group = ET.SubElement(combined_svg, 'g')
            group.set('transform', f'translate(0, {svg_info["y_offset"]})')
            
            # Copy all content from the original SVG
            for element in svg_info['content']:
                group.append(element)
        
        # Write the combined SVG to file
        tree = ET.ElementTree(combined_svg)
        ET.indent(tree, space="  ", level=0)  # Pretty print
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        
        print(f"Successfully created combined SVG: {output_file}")
        print(f"Final dimensions: {int(max_width)}x{int(total_height)} pixels")
        return True
        
    except Exception as e:
        print(f"Error combining SVGs: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 combine_svgs.py <output_file> <input_file1> [input_file2] ...")
        sys.exit(1)
    
    output_file = sys.argv[1]
    input_files = sys.argv[2:]
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    success = combine_svgs(output_file, input_files)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()