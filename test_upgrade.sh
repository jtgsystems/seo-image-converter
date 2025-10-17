#!/bin/bash
# Quick test script for Qwen2.5-VL upgrade
# Run this to verify the upgrade works correctly

echo "========================================="
echo "SEO Image Converter - Upgrade Test"
echo "Testing Qwen2.5-VL Integration"
echo "========================================="
echo ""

# Check if Ollama is running
echo "1. Checking Ollama service..."
if pgrep -x "ollama" > /dev/null; then
    echo "   ✓ Ollama is running"
else
    echo "   ✗ Ollama is NOT running"
    echo "   Starting Ollama..."
    ollama serve &
    sleep 3
fi
echo ""

# Check if model is available
echo "2. Checking Qwen2.5-VL model..."
if ollama list | grep -q "qwen2.5vl:7b"; then
    echo "   ✓ qwen2.5vl:7b is installed"
else
    echo "   ✗ Model not found"
    echo "   Installing qwen2.5vl:7b..."
    ollama pull qwen2.5vl:7b
fi
echo ""

# Check Python dependencies
echo "3. Checking Python dependencies..."
python3 -c "import sys; sys.path.insert(0, 'src'); from ai_analyzer import AIImageAnalyzer" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ Python modules OK"
else
    echo "   ✗ Missing dependencies"
    echo "   Installing requirements..."
    pip3 install -r requirements.txt --quiet
fi
echo ""

# Verify configuration
echo "4. Verifying configuration..."
if grep -q "qwen2.5vl:7b" src/ai_analyzer.py; then
    echo "   ✓ Model updated in code"
else
    echo "   ✗ Code not updated"
fi

if [ -f "config.yaml" ]; then
    echo "   ✓ config.yaml exists"
else
    echo "   ⚠ config.yaml not found (will use defaults)"
fi
echo ""

# Test the analyzer
echo "5. Testing AI Analyzer..."
python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, 'src')
from ai_analyzer import AIImageAnalyzer

try:
    analyzer = AIImageAnalyzer()
    print(f"   ✓ Analyzer initialized")
    print(f"   Model: {analyzer.model}")
    print(f"   Timeout: {analyzer.timeout}s")

    if analyzer.is_ollama_available():
        print(f"   ✓ Ollama service is accessible")
        print(f"   ✓ Model is ready for use")
    else:
        print(f"   ✗ Cannot connect to Ollama")

except Exception as e:
    print(f"   ✗ Error: {e}")
PYTHON_TEST

echo ""
echo "========================================="
echo "Test Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Test with sample image:"
echo "   python main.py --cli /path/to/test/images"
echo ""
echo "2. Launch GUI:"
echo "   python main.py"
echo ""
echo "3. Check detailed feedback:"
echo "   cat ~/Desktop/SEO-Image-Converter-Feedback.md"
echo ""
