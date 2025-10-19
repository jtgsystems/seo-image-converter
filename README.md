# 🚀 SEO Image Converter - AI-Powered Image Optimization Tool

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Dear PyGui](https://img.shields.io/badge/GUI-Dear%20PyGui%202.1.0-green.svg)](https://github.com/hoffstadt/DearPyGui)
[![Ollama](https://img.shields.io/badge/AI-Ollama%2FQwen2.5--VL-orange.svg)](https://ollama.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/jtgsystems/seo-image-converter.svg)](https://github.com/jtgsystems/seo-image-converter/stargazers)

**Transform your website images with AI-powered SEO optimization and advanced compression for lightning-fast page loads and better search rankings.**

## 🎯 What is SEO Image Converter?

SEO Image Converter is a revolutionary **AI-powered image optimization tool** that combines cutting-edge **machine learning** with advanced **image compression** to boost your website's performance and search engine rankings. Using **Ollama/Qwen2.5-VL integration**, it automatically generates **SEO-friendly filenames** and optimizes images for web performance.

### 🏆 Why Choose SEO Image Converter?

- **🤖 AI-Powered SEO Naming**: Automatically generates descriptive, keyword-rich filenames using Qwen2.5-VL vision AI
- **⚡ Advanced Compression**: Supports WebP, PNG (Zopfli), and JPEG (MozJPEG) for maximum file size reduction
- **🎨 Modern GUI**: Beautiful, responsive interface built with Dear PyGui 2.1.0 (2025 latest)
- **🔄 Batch Processing**: Process hundreds of images simultaneously with parallel processing
- **💾 Smart Backup**: Automatic original file backup with timestamp organization
- **📊 Real-time Analytics**: Live progress tracking with compression statistics
- **🔧 Flexible Configuration**: YAML-based settings for custom optimization workflows

## 🚀 Key Features

### AI-Powered Image Analysis
- **Qwen2.5-VL Vision Model Integration**: Analyzes image content to generate contextually relevant filenames
- **SEO Keyword Generation**: Creates search-engine-optimized filenames automatically
- **Content Recognition**: Identifies objects, scenes, and concepts in images for better naming
- **Fallback Naming**: Smart fallback system when AI analysis is unavailable

### 🖼️ Advanced Image Optimization
- **Latest Compression**: WebP, PNG (Zopfli), JPEG (MozJPEG) with 20-30% better compression
- **Lossless Options**: Maintains image quality while reducing file size
- **Smart Resizing**: Optional dimension limits with quality preservation
- **Format Conversion**: Intelligent format selection based on image content

### ⚡ High Performance
- **Parallel Processing**: Utilizes 80% of CPU cores by default
- **GPU Acceleration**: Dear PyGui for smooth 60fps interface
- **Batch Operations**: Process thousands of images efficiently
- **Progress Tracking**: Real-time progress with detailed statistics

### 🎨 Modern GUI (Dear PyGui 2025)
- **GPU-Rendered Interface**: Smooth, responsive, modern design
- **Drag & Drop Support**: Easy directory selection
- **Real-Time Progress**: Visual progress bars and statistics
- **Dark Theme**: Professional appearance with customizable styling
- **Tabbed Interface**: Organized workflow with Process/Results/Settings/Logs

### 📊 Comprehensive Results
- **Detailed Analytics**: File-by-file compression statistics
- **Export Options**: JSON and CSV export for further analysis
- **Visual Results Table**: Easy-to-read results with color coding
- **File Management**: Automatic backup of originals

## 🛠️ Installation

### Prerequisites

1. **Python 3.9+**
2. **Ollama** (for AI-powered naming):
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh

   # Pull Qwen2.5-VL model
   ollama pull qwen2.5vl:7b
   
   # Start Ollama service
   ollama serve
   ```

### Install Application

```bash
# Clone repository
git clone <repository-url>
cd python-seo-image-converter

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## 🎯 Usage

### GUI Application (Default)
```bash
python main.py
```

### CLI Application
```bash
python main.py --cli /path/to/images

# With options
python main.py --cli /path/to/images --format webp --quality 85 --parallel-jobs 8
```

### Configuration

The application uses `config.yaml` for settings:

```yaml
# AI Configuration
ollama:
  endpoint: "http://localhost:11434/api/generate"
  model: "qwen2.5vl:7b"
  timeout: 45

# Image Processing
image:
  formats:
    output: "webp"  # webp, png, jpeg
  quality:
    webp: 85
    jpeg: 90
  optimization:
    lossless: true
    strip_metadata: true

# SEO Settings
seo:
  keyword_count: 8
  max_filename_length: 100

# Performance
processing:
  parallel_jobs: 0  # 0 = auto (80% of CPU cores)
  backup_originals: true
```

## 📋 Workflow

1. **Select Directory**: Choose input folder with images
2. **Configure Options**: Set output format, quality, and AI settings  
3. **Start Processing**: 
   - AI analyzes each image for SEO keywords
   - Images optimized with latest compression algorithms
   - Files renamed with SEO-friendly names
   - Originals backed up automatically
4. **View Results**: Detailed statistics and per-file results
5. **Export Data**: Save results as JSON or CSV

## 🔧 Architecture

### Core Components

- **`processor.py`**: Main processing engine with parallel execution
- **`ai_analyzer.py`**: Ollama/Qwen2.5-VL integration for image analysis
- **`optimizer.py`**: Advanced image optimization (WebP, PNG, JPEG)
- **`gui_dearpygui.py`**: Modern GPU-accelerated interface
- **`cli.py`**: Command-line interface with rich output

### Technology Stack

- **GUI Framework**: [Dear PyGui](https://github.com/hoffstadt/dearpygui) - Latest 2025 GPU-accelerated framework
- **AI Integration**: [Ollama](https://ollama.ai/) with Qwen2.5-VL vision model
- **Image Processing**: Pillow + specialized optimization libraries
- **Compression**: 
  - WebP: Native Pillow optimization
  - PNG: Zopfli compression (5% better than standard)
  - JPEG: MozJPEG lossless optimization (20-30% better)

## 🎨 GUI Features

### Main Interface
- **Process Tab**: Directory selection, options, progress tracking
- **Results Tab**: Comprehensive statistics and detailed results table
- **Settings Tab**: AI configuration, image processing options
- **Logs Tab**: Real-time application logs

### Visual Design
- **Modern Dark Theme**: Professional appearance with blue accents
- **GPU Acceleration**: Smooth 60fps interface rendering
- **Responsive Layout**: Adapts to different window sizes
- **Color-Coded Results**: Green for success, red for errors, yellow for warnings

## 📊 Performance

### Compression Results
- **WebP**: Typically 25-35% smaller than JPEG
- **PNG with Zopfli**: 5% better than standard PNG compression
- **JPEG with MozJPEG**: 20-30% better compression than standard JPEG

### Processing Speed
- **Parallel Processing**: 4-16 concurrent image operations
- **AI Analysis**: 4-8 seconds per image (Qwen2.5-VL 7B model)
- **Optimization**: 1-3 seconds per image depending on size
- **Batch Processing**: 100+ images processed efficiently

## 🔍 Example Results

### Before
```
IMG_20231025_143052.jpg (2.4 MB)
DSC_0891.png (5.1 MB)  
photo-1234.jpeg (1.8 MB)
```

### After
```
happy-family-walking-beach-sunset-vacation-children-parents.webp (0.6 MB) # 75% smaller
professional-meeting-office-team-discussion-laptop-conference.webp (1.2 MB) # 76% smaller  
delicious-chocolate-cake-dessert-birthday-celebration-sweet.webp (0.4 MB) # 78% smaller
```

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Not Found**
   - Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
   - Start service: `ollama serve`
   - Pull model: `ollama pull qwen2.5vl:7b`

2. **Permission Errors**
   - Ensure write access to output directory
   - Run with appropriate permissions

3. **Memory Issues**
   - Reduce parallel jobs in settings
   - Close other applications
   - Use smaller batch sizes

4. **GUI Issues**
   - Update graphics drivers
   - Install Dear PyGui: `pip install dearpygui`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Dear PyGui**: Modern GPU-accelerated Python GUI framework
- **Ollama Team**: Local LLM inference platform
- **Qwen2.5-VL**: Advanced Vision-Language Model by Alibaba Cloud
- **Python Community**: Amazing ecosystem of libraries

## 🎯 About Us

**JTG Systems** is dedicated to creating innovative tools that bridge the gap between artificial intelligence and practical web development needs. Our mission is to make advanced AI technologies accessible to developers, marketers, and content creators worldwide.

### Our Vision
We believe that AI-powered tools should be:
- **User-friendly**: Intuitive interfaces that anyone can use
- **Powerful**: Enterprise-grade capabilities without the complexity
- **Open**: Transparent, open-source development
- **Efficient**: Optimized for real-world performance needs

### The Team
- **Lead Developer**: Specialized in AI/ML integration and web optimization
- **UI/UX Design**: Focus on user-centered design and accessibility
- **Performance Engineering**: Optimization and scalability experts
- **Community**: Driven by feedback from our amazing user community

### Contact & Support
- **GitHub Issues**: [Report bugs or request features](https://github.com/jtgsystems/seo-image-converter/issues)
- **Discussions**: [Join the community](https://github.com/jtgsystems/seo-image-converter/discussions)
- **Email**: support@jtgsystems.com
- **Website**: [www.jtgsystems.com](https://www.jtgsystems.com)

---

## 🏷️ Keywords & Technologies

### SEO & Web Performance Keywords
`image optimization` `SEO tools` `web performance` `page speed optimization` `image compression` `website optimization` `search engine optimization` `web development tools` `image SEO` `page load speed` `core web vitals` `image conversion` `bulk image processing` `website performance` `SEO automation` `image metadata` `web optimization software` `site speed improvement` `image file size reduction` `SEO-friendly filenames`

### Technical Keywords  
`python gui application` `dear pygui` `artificial intelligence` `machine learning` `computer vision` `ollama integration` `qwen2.5vl model` `local AI` `image processing` `batch processing` `parallel processing` `webp compression` `png optimization` `jpeg compression` `zopfli` `mozjpeg` `pillow python` `python imaging` `desktop application` `cross-platform` `open source`

### AI & Machine Learning Keywords
`AI image analysis` `vision language model` `local AI inference` `image content recognition` `automated keyword generation` `AI-powered naming` `machine learning application` `computer vision API` `image classification` `content-aware optimization` `intelligent image processing` `AI workflow automation` `natural language processing` `multimodal AI` `vision transformer` `deep learning application`

### Development & Framework Keywords
`python 3.9+` `threading` `asyncio` `yaml configuration` `gui framework` `desktop gui` `modern python` `software architecture` `design patterns` `test-driven development` `continuous integration` `version control` `agile development` `user experience` `responsive design` `cross-platform compatibility` `performance optimization` `memory management` `error handling` `logging` `documentation`

---

<div align="center">

**⭐ Star this repository if it helped optimize your images! ⭐**

[🐛 Report Bug](https://github.com/jtgsystems/seo-image-converter/issues) • [✨ Request Feature](https://github.com/jtgsystems/seo-image-converter/issues) • [💬 Discussions](https://github.com/jtgsystems/seo-image-converter/discussions)

**Built with ❤️ by [JTG Systems](https://github.com/jtgsystems) • Made for the developer community**

</div>