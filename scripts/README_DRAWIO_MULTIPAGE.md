# Draw.io Multi-page SVG Conversion

This document describes the enhanced GitHub Actions workflow that supports converting multi-page Draw.io files to combined SVG files.

## Overview

The `.github/workflows/drawio-to-svg.yml` workflow has been enhanced to support multi-page Draw.io files. When a Draw.io file contains multiple pages, all pages are exported individually and then combined vertically into a single SVG file.

## Features

- **Multi-page Support**: Automatically detects and processes all pages in a Draw.io file
- **Backward Compatibility**: Single-page Draw.io files continue to work as before
- **Vertical Combination**: Multiple pages are arranged vertically with configurable spacing
- **Same Output Filename**: Output files maintain the same naming convention (filename.svg)
- **Robust Error Handling**: Fallback mechanisms ensure conversion succeeds even if page detection fails
- **Clean Temporary Files**: All temporary files are automatically cleaned up
- **XML-based Page Detection**: Uses XML parsing to accurately detect the number of pages

## How It Works

### 1. Page Detection
The workflow uses Python XML parsing to detect the number of pages in a Draw.io file:
```python
import xml.etree.ElementTree as ET
tree = ET.parse(drawio_file)
root = tree.getroot()
diagrams = root.findall('diagram')
pages = len(diagrams) if diagrams else 1
```

### 2. Processing Logic
- **1 page found**: Uses direct single-page export method
- **Multiple pages found**: Exports each page individually and combines them using the Python script

### 3. SVG Combination
The `scripts/combine_svgs.py` script:
- Parses SVG dimensions from each individual page
- Creates a new SVG with combined dimensions
- Places each page in a group with appropriate vertical translation
- Maintains proper SVG structure and namespaces

## File Structure

```
.github/workflows/drawio-to-svg.yml    # Enhanced workflow
scripts/combine_svgs.py                # SVG combination script
scripts/test_combine_svgs.py           # Test script for validation
027.test-drawio/src/multi-page-test.drawio  # Test file with multiple pages
```

## Usage

The workflow automatically triggers when `.drawio` files are pushed to the repository. No manual intervention is required.

### Example: Multi-page Draw.io File
If you have a Draw.io file `diagram.drawio` with 3 pages:
1. The workflow detects 3 pages using XML parsing
2. The workflow exports: `page_0.svg`, `page_1.svg`, `page_2.svg`
3. The Python script combines them into: `diagram.svg`
4. The temporary page files are cleaned up
5. A PR is created with the new `diagram.svg`

## Technical Details

### Dependencies
- **Draw.io Desktop**: For exporting individual pages
- **Python 3**: For XML parsing and SVG combination (uses standard library only)
- **xvfb**: For headless Draw.io operation

### SVG Combination Algorithm
1. Parse dimensions from each SVG file (width, height, viewBox)
2. Calculate total height and maximum width
3. Create new SVG with combined dimensions
4. Add each page's content in a translated group
5. Write the combined SVG with proper XML structure

### Error Handling
- **Page detection failure**: Falls back to single-page export
- **Individual page export failure**: Skips failed pages, continues with successful ones
- **SVG combination failure**: Reports error and exits
- **File not found**: Skips missing files with warning

## Configuration

### Spacing Between Pages
The default spacing between pages is 20 pixels. This can be modified in the `combine_svgs.py` script:
```python
success = combine_svgs(output_file, input_files, spacing=20)  # Change spacing here
```

## Testing

Run the test script to validate the SVG combination functionality:
```bash
cd scripts
python3 test_combine_svgs.py
```

This creates test SVG files and verifies that they can be combined correctly.

## Troubleshooting

### Common Issues

1. **No pages detected**: 
   - Check if the Draw.io file is valid XML
   - Verify Draw.io desktop installation
   - Check workflow logs for export errors

2. **Combination fails**:
   - Verify Python 3 is available
   - Check individual SVG files are valid
   - Review error messages in workflow logs

3. **Output SVG is malformed**:
   - Check input SVG files for XML validity
   - Verify dimensions are parsed correctly
   - Test with simpler Draw.io files first

### Debug Mode
Add debug output to the workflow by modifying the conversion step to include more verbose logging.

## Migration from Single-page

Existing single-page Draw.io files require no changes and will continue to work exactly as before. The enhanced workflow is fully backward compatible.