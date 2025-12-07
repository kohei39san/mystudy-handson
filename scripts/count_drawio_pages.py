#!/usr/bin/env python3
"""Count the number of pages in a Draw.io file."""
import sys
import xml.etree.ElementTree as ET

if len(sys.argv) != 2:
    print("1")
    sys.exit(0)

try:
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()
    diagrams = root.findall("diagram")
    print(len(diagrams) if diagrams else 1)
except:
    print("1")
