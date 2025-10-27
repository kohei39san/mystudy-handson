#!/usr/bin/env python3
"""
Test URL generation for search_issues functionality
"""

import os
import sys
from urllib.parse import quote

def test_url_generation():
    """Test URL generation logic for tracker_id=1"""
    
    base_url = "http://localhost:3000"
    kwargs = {"tracker_id": "1"}
    
    # Build search URL with Redmine filter format (same logic as in search_issues)
    search_params = ["set_filter=1", "sort=id:desc"]
    
    # Add filter parameters in Redmine format
    if kwargs.get('tracker_id'):
        search_params.extend([
            "f[]=tracker_id",
            "op[tracker_id]==",
            f"v[tracker_id][]={kwargs['tracker_id']}"
        ])
    
    # Add empty filter field
    search_params.append("f[]=")
    
    # Add column configuration
    search_params.extend([
        "c[]=tracker",
        "c[]=status", 
        "c[]=priority",
        "c[]=subject",
        "c[]=assigned_to",
        "c[]=updated_on"
    ])
    
    # Add grouping and other parameters
    search_params.extend(["group_by=", "t[]="])
    
    # Build issues URL
    issues_url = f"{base_url}/issues"
    
    # URL encode the parameters
    if search_params:
        encoded_params = []
        for param in search_params:
            if '=' in param:
                key, value = param.split('=', 1)
                encoded_params.append(f"{quote(key, safe='[]')}={quote(value, safe='')}")
            else:
                encoded_params.append(quote(param, safe='[]'))
        issues_url += "?" + "&".join(encoded_params)
    
    print("Generated URL:")
    print(issues_url)
    print()
    
    # Compare with expected format
    expected_params = [
        "set_filter=1",
        "sort=id%3Adesc",
        "f%5B%5D=tracker_id", 
        "op%5Btracker_id%5D=%3D",
        "v%5Btracker_id%5D%5B%5D=1",
        "f%5B%5D=",
        "c%5B%5D=tracker",
        "c%5B%5D=status",
        "c%5B%5D=priority", 
        "c%5B%5D=subject",
        "c%5B%5D=assigned_to",
        "c%5B%5D=updated_on",
        "group_by=",
        "t%5B%5D="
    ]
    
    expected_url = f"{base_url}/issues?" + "&".join(expected_params)
    
    print("Expected URL (from your example):")
    print(expected_url)
    print()
    
    print("Key issue found:")
    print("Current: op[tracker_id]= (empty operator)")
    print("Expected: op[tracker_id]== (equals operator)")
    
    return issues_url, expected_url

if __name__ == "__main__":
    test_url_generation()