#!/usr/bin/env python3
"""
Production System Validation Test
Tests all core components for production readiness
"""

import os
import sys
import time
import json
import traceback
from typing import Dict, Any, List

def test_file_structure():
    """Test that all required files are present for production."""
    print("🔍 Testing Production File Structure")
    print("=" * 50)

    required_files = [
        'README.md',
        'requirements.txt',
        'setup.py',
        'Dockerfile',
        'docker-compose.yml',
        '.gitignore',
        'bsee/__init__.py',
        'bsee_ai/__init__.py',
        'bsee_ai/utils/simple_scorer.py',
        'test_ai_integration.py'
    ]

    required_dirs = [
        'bsee',
        'bsee_ai',
        'config',
        'data',
        'docs',
        'gui',
        'scripts',
        'tests'
    ]

    missing_files = []
    missing_dirs = []

    # Check files
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path:<35} ({size:,} bytes)")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path:<35} (MISSING)")

    # Check directories
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✅ {dir_path:<35} (directory)")
        else:
            missing_dirs.append(dir_path)
            print(f"❌ {dir_path:<35} (MISSING)")

    if missing_files or missing_dirs:
        print(f"\n❌ Missing {len(missing_files)} files and {len(missing_dirs)} directories")
        return False
    else:
        print(f"\n✅ All {len(required_files)} files and {len(required_dirs)} directories present")
        return True


def test_core_imports():
    """Test that all core modules can be imported."""
    print("\n🔍 Testing Core Module Imports")
    print("=" * 50)

    imports_to_test = [
        ('bsee_ai.utils.simple_scorer', 'SimpleHomogeneityScorer'),
        ('bsee_ai', '__version__' if hasattr(__import__('bsee_ai'), '__version__') else 'bsee_ai'),
    ]

    successful_imports = 0
    failed_imports = []

    for module_name, item_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[item_name])
            if hasattr(module, item_name):
                print(f"✅ {module_name}.{item_name}")
                successful_imports += 1
            else:
                print(f"❌ {module_name}.{item_name} (item not found)")
                failed_imports.append(f"{module_name}.{item_name}")
        except ImportError as e:
            print(f"❌ {module_name}.{item_name} ({str(e)})")
            failed_imports.append(f"{module_name}.{item_name}")
        except Exception as e:
            print(f"❌ {module_name}.{item_name} ({str(e)})")
            failed_imports.append(f"{module_name}.{item_name}")

    print(f"\n📊 Import Results: {successful_imports}/{len(imports_to_test)} successful")
    return len(failed_imports) == 0


def test_homogeneity_scorer():
    """Test the homogeneity scorer functionality."""
    print("\n🔍 Testing Homogeneity Scorer")
    print("=" * 50)

    try:
        from bsee_ai.utils.simple_scorer import SimpleHomogeneityScorer

        scorer = SimpleHomogeneityScorer()

        # Test with different data types
        test_cases = [
            (b'A' * 100, 'repetitive'),
            (bytes([i % 256 for i in range(100)]), 'sequential'),
            (b'Hello World! ' * 8, 'text'),
            (b'', 'empty')
        ]

        for data, description in test_cases:
            try:
                score = scorer.calculate_score(data)
                analysis = scorer.analyze_data(data)
                print(f"✅ {description:<12} Score: {score:.4f}, Characteristics: {analysis['characteristics']}")
            except Exception as e:
                print(f"❌ {description:<12} Error: {str(e)}")
                return False

        print("✅ Homogeneity scorer working correctly")
        return True

    except Exception as e:
        print(f"❌ Homogeneity scorer test failed: {str(e)}")
        return False


def test_configuration_files():
    """Test configuration files are valid."""
    print("\n🔍 Testing Configuration Files")
    print("=" * 50)

    config_files = [
        'requirements.txt',
        'setup.py',
        'Dockerfile'
    ]

    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                if config_file == 'requirements.txt':
                    with open(config_file, 'r') as f:
                        requirements = f.read().strip().split('\n')
                        valid_requirements = [r for r in requirements if r.strip() and not r.strip().startswith('#')]
                        print(f"✅ {config_file:<20} ({len(valid_requirements)} packages)")

                elif config_file == 'setup.py':
                    # Simple syntax check
                    with open(config_file, 'r') as f:
                        content = f.read()
                        compile(content, config_file, 'exec')
                        print(f"✅ {config_file:<20} (valid syntax)")

                elif config_file == 'Dockerfile':
                    with open(config_file, 'r') as f:
                        lines = f.readlines()
                        print(f"✅ {config_file:<20} ({len(lines)} lines)")

            except Exception as e:
                print(f"❌ {config_file:<20} Error: {str(e)}")
                return False
        else:
            print(f"❌ {config_file:<20} (MISSING)")
            return False

    return True


def test_documentation():
    """Test documentation completeness."""
    print("\n🔍 Testing Documentation")
    print("=" * 50)

    doc_files = [
        'README.md'
    ]

    doc_status = {}

    for doc_file in doc_files:
        if os.path.exists(doc_file):
            try:
                with open(doc_file, 'r') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    chars = len(content)
                    doc_status[doc_file] = {'lines': lines, 'chars': chars}
                    print(f"✅ {doc_file:<15} ({lines:,} lines, {chars:,} characters)")
            except Exception as e:
                print(f"❌ {doc_file:<15} Error: {str(e)}")
                return False
        else:
            print(f"❌ {doc_file:<15} (MISSING)")
            return False

    # Check README has key sections
    if 'README.md' in doc_status:
        try:
            with open('README.md', 'r') as f:
                readme_content = f.read().lower()

            required_sections = [
                'installation', 'usage', 'features', 'testing'
            ]

            missing_sections = []
            for section in required_sections:
                if section not in readme_content:
                    missing_sections.append(section)

            if missing_sections:
                print(f"⚠️  README missing sections: {', '.join(missing_sections)}")
            else:
                print("✅ README contains all required sections")

        except Exception as e:
            print(f"❌ Error analyzing README: {str(e)}")
            return False

    return True


def test_ai_integration():
    """Test the AI integration system."""
    print("\n🔍 Testing AI Integration System")
    print("=" * 50)

    try:
        from bsee_ai.utils.simple_scorer import SimpleHomogeneityScorer

        scorer = SimpleHomogeneityScorer()

        # Test with sample data
        test_data = b'HelloWorld' * 10 + b'\x00' * 20 + b'\xFF' * 20

        print("Testing data analysis...")
        analysis = scorer.analyze_data(test_data)
        print(f"✅ Data analysis complete - Score: {analysis['overall_score']:.4f}")

        print("Testing scoring system...")
        score = scorer.calculate_score(test_data)
        print(f"✅ Scoring complete - Score: {score:.4f}")

        # Test different data types
        data_types = [
            (b'A' * 50, 'uniform'),
            (bytes([i % 256 for i in range(50)]), 'varied'),
            (b'Hello' * 10, 'repetitive')
        ]

        for data, desc in data_types:
            score = scorer.calculate_score(data)
            print(f"✅ {desc:<10} data: {score:.4f}")

        print("✅ AI integration system working correctly")
        return True

    except Exception as e:
        print(f"❌ AI integration test failed: {str(e)}")
        traceback.print_exc()
        return False


def test_production_readiness():
    """Test overall production readiness."""
    print("\n🏭 Production Readiness Assessment")
    print("=" * 50)

    readiness_checks = [
        ("File Structure", test_file_structure),
        ("Core Imports", test_core_imports),
        ("Homogeneity Scorer", test_homogeneity_scorer),
        ("Configuration Files", test_configuration_files),
        ("Documentation", test_documentation),
        ("AI Integration", test_ai_integration)
    ]

    results = {}
    passed_checks = 0

    for check_name, check_func in readiness_checks:
        try:
            result = check_func()
            results[check_name] = result
            if result:
                passed_checks += 1
        except Exception as e:
            print(f"❌ {check_name} failed with exception: {str(e)}")
            results[check_name] = False

    print(f"\n📊 Production Readiness Summary")
    print("=" * 50)
    print(f"Passed: {passed_checks}/{len(readiness_checks)} checks")

    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")

    overall_ready = passed_checks == len(readiness_checks)
    if overall_ready:
        print(f"\n🎉 SYSTEM IS PRODUCTION READY!")
    else:
        print(f"\n⚠️  SYSTEM NEEDS {len(readiness_checks) - passed_checks} FIXES BEFORE PRODUCTION")

    return overall_ready


def generate_production_report():
    """Generate a production readiness report."""
    print("\n📋 Generating Production Report")
    print("=" * 50)

    report = {
        'timestamp': time.time(),
        'system_info': {
            'python_version': sys.version,
            'platform': sys.platform
        },
        'file_structure': {},
        'test_results': {},
        'recommendations': []
    }

    # Collect file information
    important_files = [
        'README.md', 'requirements.txt', 'setup.py', 'Dockerfile',
        'bsee_ai/__init__.py', 'bsee_ai/utils/simple_scorer.py',
        'test_ai_integration.py'
    ]

    for file_path in important_files:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            report['file_structure'][file_path] = {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'exists': True
            }
        else:
            report['file_structure'][file_path] = {'exists': False}

    # Add recommendations
    report['recommendations'] = [
        "Deploy using Docker: docker-compose up -d",
        "Monitor system performance in production",
        "Set up logging and monitoring",
        "Regular backup of AI learning models",
        "Test with various binary data types"
    ]

    # Save report
    with open('production_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("✅ Production report saved to production_report.json")
    return report


def main():
    """Main production validation function."""
    print("🚀 BSEE PRODUCTION SYSTEM VALIDATION")
    print("=" * 60)
    print("Validating system readiness for production deployment")
    print("=" * 60)

    try:
        # Run all production checks
        is_ready = test_production_readiness()

        # Generate production report
        report = generate_production_report()

        if is_ready:
            print("\n" + "="*60)
            print("✅ PRODUCTION VALIDATION SUCCESSFUL!")
            print("="*60)
            print("\n🎯 System is ready for production deployment!")
            print("📋 Production report generated")
            print("🐳 Use 'docker-compose up -d' to deploy")
            print("📊 Monitor system health and AI learning progress")

            return 0
        else:
            print("\n" + "="*60)
            print("❌ PRODUCTION VALIDATION FAILED!")
            print("="*60)
            print("\n🔧 Fix the issues above before deploying to production")
            print("📋 Review production_report.json for details")

            return 1

    except Exception as e:
        print(f"\n❌ Production validation failed: {str(e)}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)