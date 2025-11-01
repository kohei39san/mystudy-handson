#!/usr/bin/env python3
"""
Validation script for Redmine MCP Server
Tests basic functionality without requiring a real Redmine server
"""

import sys
import os
import importlib.util
import traceback

def test_imports():
    """Test that all modules can be imported correctly"""
    print("🔍 Testing module imports...")
    
    # Add src to path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    sys.path.insert(0, src_path)
    
    try:
        # Test config import
        print("  ✓ Testing config module...")
        import config
        print(f"    Base URL: {config.config.base_url}")
        
        # Test scraper import
        print("  ✓ Testing redmine_scraper module...")
        import redmine_scraper
        scraper = redmine_scraper.RedmineScraper()
        print(f"    Scraper initialized: {type(scraper).__name__}")
        
        # Test MCP server import
        print("  ✓ Testing redmine_mcp_server module...")
        import redmine_mcp_server
        print(f"    MCP server module loaded: {redmine_mcp_server.__name__}")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration system"""
    print("\n🔧 Testing configuration system...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        import config
        
        cfg = config.config
        
        # Test basic configuration values
        assert hasattr(cfg, 'base_url'), "Missing base_url"
        assert hasattr(cfg, 'login_url'), "Missing login_url"
        assert hasattr(cfg, 'projects_url'), "Missing projects_url"
        assert hasattr(cfg, 'session_timeout'), "Missing session_timeout"
        
        print(f"  ✓ Base URL: {cfg.base_url}")
        print(f"  ✓ Login URL: {cfg.login_url}")
        print(f"  ✓ Projects URL: {cfg.projects_url}")
        print(f"  ✓ Session timeout: {cfg.session_timeout}s")
        print(f"  ✓ Debug mode: {cfg.debug}")
        
        print("✅ Configuration system working!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        traceback.print_exc()
        return False

def test_scraper_initialization():
    """Test scraper can be initialized"""
    print("\n🕷️  Testing scraper initialization...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        import redmine_scraper
        
        scraper = redmine_scraper.RedmineScraper()
        
        # Test basic properties
        assert hasattr(scraper, 'session'), "Missing session"
        assert hasattr(scraper, 'is_authenticated'), "Missing is_authenticated"
        assert hasattr(scraper, 'last_activity'), "Missing last_activity"
        
        print(f"  ✓ Session initialized: {type(scraper.session).__name__}")
        print(f"  ✓ Authentication status: {scraper.is_authenticated}")
        print(f"  ✓ Session validation method: {callable(scraper.is_session_valid)}")
        
        print("✅ Scraper initialization successful!")
        return True
        
    except Exception as e:
        print(f"❌ Scraper initialization failed: {e}")
        traceback.print_exc()
        return False

def test_mcp_server_structure():
    """Test MCP server structure"""
    print("\n🖥️  Testing MCP server structure...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        import redmine_mcp_server
        
        # Test server class exists
        assert hasattr(redmine_mcp_server, 'RedmineMCPServer'), "Missing RedmineMCPServer class"
        
        # Try to initialize server (but don't run it)
        server = redmine_mcp_server.RedmineMCPServer()
        
        assert hasattr(server, 'server'), "Missing server attribute"
        assert hasattr(server, 'scraper'), "Missing scraper attribute"
        
        print(f"  ✓ Server class: {type(server).__name__}")
        print(f"  ✓ MCP server: {type(server.server).__name__}")
        print(f"  ✓ Scraper: {type(server.scraper).__name__}")
        
        print("✅ MCP server structure valid!")
        return True
        
    except Exception as e:
        print(f"❌ MCP server structure test failed: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    base_dir = os.path.dirname(__file__)
    required_files = [
        'README.md',
        'requirements.txt',
        'src/config.py',
        'src/redmine_scraper.py',
        'src/redmine_mcp_server.py',
        'src/__init__.py',
        'examples/mcp-config.json',
        '.env.example',
        'install.sh',
        'run.sh',
        'test_server.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present!")
        return True

def main():
    """Run all validation tests"""
    print("🚀 Redmine MCP Server Validation")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Scraper Initialization", test_scraper_initialization),
        ("MCP Server Structure", test_mcp_server_structure),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Validation Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All validation tests passed! The server should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())