#!/usr/bin/env python3
"""
PDF Libraries Availability Check - Simple Version
"""

import sys

def check_libraries():
    """Check PDF library availability."""

    print("=" * 60)
    print("PDF LIBRARIES AVAILABILITY CHECK")
    print("=" * 60)
    print()

    # Check pypdf
    print("1. Checking pypdf...")
    try:
        import pypdf
        print(f"   [OK] pypdf version {pypdf.__version__}")
        from pypdf import PdfReader, PdfWriter, PdfMerger
        print(f"   [OK] Core classes importable")
        pypdf_ok = True
    except ImportError as e:
        print(f"   [FAIL] pypdf not installed: {e}")
        print(f"   Install: pip install pypdf")
        pypdf_ok = False
    print()

    # Check reportlab
    print("2. Checking reportlab...")
    try:
        import reportlab
        print(f"   [OK] reportlab version {reportlab.__version__}")
        from reportlab.pdfgen import canvas
        print(f"   [OK] Canvas module importable")
        reportlab_ok = True
    except ImportError as e:
        print(f"   [FAIL] reportlab not installed: {e}")
        print(f"   Install: pip install reportlab")
        reportlab_ok = False
    print()

    # Check integration module
    print("3. Checking PDF manipulation integration...")
    try:
        from pathlib import Path
        backend_path = Path(__file__).parent / "vibe-pdf-platform" / "Backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))

        from app.integrations.pdf_manipulation import (
            PDFManipulationMCPClient,
            PDFManipulationConfig,
        )
        print(f"   [OK] Integration module imports successfully")

        # Check PYPDF_AVAILABLE flag
        from app.integrations import pdf_manipulation
        if hasattr(pdf_manipulation, 'PYPDF_AVAILABLE'):
            status = "OK" if pdf_manipulation.PYPDF_AVAILABLE else "FAIL"
            print(f"   [{status}] PYPDF_AVAILABLE = {pdf_manipulation.PYPDF_AVAILABLE}")

        integration_ok = True
    except Exception as e:
        print(f"   [FAIL] Integration error: {e}")
        integration_ok = False
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"pypdf:        {'[OK]' if pypdf_ok else '[FAIL]'}")
    print(f"reportlab:    {'[OK]' if reportlab_ok else '[FAIL]'}")
    print(f"integration:  {'[OK]' if integration_ok else '[FAIL]'}")
    print()

    all_ok = pypdf_ok and reportlab_ok and integration_ok

    if all_ok:
        print("RESULT: ALL CHECKS PASSED")
        return 0
    else:
        print("RESULT: SOME CHECKS FAILED")
        print()
        print("RECOMMENDED ACTIONS:")
        if not pypdf_ok:
            print("  - pip install pypdf")
        if not reportlab_ok:
            print("  - pip install reportlab")
        if not integration_ok:
            print("  - Check integration module dependencies")
        return 1


if __name__ == "__main__":
    sys.exit(check_libraries())
