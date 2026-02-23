#!/usr/bin/env python3
"""
PDF Libraries Availability Check
Quick test to verify PDF manipulation libraries are installed and working.
"""

import sys
from pathlib import Path

def check_pypdf():
    """Check if pypdf library is available."""
    print("=" * 60)
    print("Checking pypdf library...")
    print("=" * 60)

    try:
        import pypdf
        print(f"✅ pypdf is installed")
        print(f"   Version: {pypdf.__version__}")
        print(f"   Location: {pypdf.__file__}")

        # Test basic functionality
        from pypdf import PdfReader, PdfWriter, PdfMerger
        print(f"✅ Core classes importable:")
        print(f"   - PdfReader: {PdfReader}")
        print(f"   - PdfWriter: {PdfWriter}")
        print(f"   - PdfMerger: {PdfMerger}")

        # Try to create a simple PDF
        from io import BytesIO
        from pypdf import PdfWriter

        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)

        buffer = BytesIO()
        writer.write(buffer)
        pdf_bytes = buffer.getvalue()

        print(f"✅ Can create PDF: {len(pdf_bytes)} bytes")

        return True

    except ImportError as e:
        print(f"❌ pypdf is NOT installed")
        print(f"   Error: {e}")
        print(f"\n   Install with: pip install pypdf")
        return False
    except Exception as e:
        print(f"❌ pypdf error: {e}")
        return False


def check_reportlab():
    """Check if reportlab library is available."""
    print("\n" + "=" * 60)
    print("Checking reportlab library...")
    print("=" * 60)

    try:
        import reportlab
        print(f"✅ reportlab is installed")
        print(f"   Version: {reportlab.__version__}")
        print(f"   Location: {reportlab.__file__}")

        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        print(f"✅ Core modules importable:")
        print(f"   - canvas: {canvas}")
        print(f"   - pagesizes: {letter}")

        # Test basic functionality
        from io import BytesIO

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, "Test PDF")
        c.save()

        pdf_bytes = buffer.getvalue()
        print(f"✅ Can create PDF: {len(pdf_bytes)} bytes")

        return True

    except ImportError as e:
        print(f"❌ reportlab is NOT installed")
        print(f"   Error: {e}")
        print(f"\n   Install with: pip install reportlab")
        return False
    except Exception as e:
        print(f"❌ reportlab error: {e}")
        return False


def check_integration_module():
    """Check if the PDF manipulation integration module can be imported."""
    print("\n" + "=" * 60)
    print("Checking PDF Manipulation Integration Module...")
    print("=" * 60)

    # Add Backend to path if needed
    backend_path = Path(__file__).parent / "vibe-pdf-platform" / "Backend"
    if backend_path.exists() and str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
        print(f"Added to path: {backend_path}")

    try:
        from app.integrations.pdf_manipulation import (
            PDFManipulationMCPClient,
            PDFManipulationConfig,
            PageNumberPosition,
            PageNumberFormat,
            CompressionQuality,
        )
        print(f"✅ Module imports successful")
        print(f"   Classes available:")
        print(f"   - PDFManipulationMCPClient: {PDFManipulationMCPClient}")
        print(f"   - PDFManipulationConfig: {PDFManipulationConfig}")
        print(f"   - PageNumberPosition: {PageNumberPosition}")
        print(f"   - PageNumberFormat: {PageNumberFormat}")
        print(f"   - CompressionQuality: {CompressionQuality}")

        # Check if pypdf is available from the module's perspective
        from app.integrations import pdf_manipulation
        if hasattr(pdf_manipulation, 'PYPDF_AVAILABLE'):
            if pdf_manipulation.PYPDF_AVAILABLE:
                print(f"✅ PYPDF_AVAILABLE = True (pypdf is accessible)")
            else:
                print(f"❌ PYPDF_AVAILABLE = False (pypdf NOT accessible)")

        return True

    except ImportError as e:
        print(f"❌ Module import failed")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Module error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all checks."""
    print("\n")
    print("=" * 60)
    print("PDF LIBRARIES AVAILABILITY CHECK")
    print("=" * 60)

    results = {
        "pypdf": check_pypdf(),
        "reportlab": check_reportlab(),
        "integration": check_integration_module(),
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for name, status in results.items():
        symbol = "✅" if status else "❌"
        status_text = "PASS" if status else "FAIL"
        print(f"{symbol} {name:20s}: {status_text}")

    all_passed = all(results.values())
    print("\n" + "=" * 60)

    if all_passed:
        print("✅ ALL CHECKS PASSED - PDF manipulation is ready!")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - See errors above")
        print("\nRecommendations:")

        if not results.get("pypdf"):
            print("  1. Install pypdf: pip install pypdf")

        if not results.get("reportlab"):
            print("  2. Install reportlab: pip install reportlab")

        if not results.get("integration"):
            print("  3. Check module path and dependencies")

        return 1


if __name__ == "__main__":
    sys.exit(main())
