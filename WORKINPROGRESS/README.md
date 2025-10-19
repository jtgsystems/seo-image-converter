# Work In Progress - Alternative Implementations

This folder contains experimental/alternative implementations of the SEO Image Converter.

## Tauri Desktop App

**Location**: `tauri-desktop-app/`

A desktop application version built with modern web technologies:

### Technology Stack
- **Frontend**: SvelteKit + Vite + Tailwind CSS
- **Backend**: Rust (Tauri framework)
- **Architecture**: Web UI rendered in a native desktop window

### Features
- Cross-platform desktop executable
- Drag-and-drop interface for image selection
- Modern, responsive UI with Tailwind styling
- Wraps the bash script `seo_image_processor.sh`
- System tray integration
- Real-time log streaming

### Status
🚧 **Experimental** - This is a prototype/proof-of-concept version.

The main active version is the Python implementation in the root directory, which uses Dear PyGui and has full Qwen2.5-VL integration.

### Building

```bash
cd tauri-desktop-app

# Install dependencies
npm install

# Development mode
npm run tauri dev

# Build executable
npm run tauri build
```

### Architecture

See `architecture.md` for detailed system design including:
- Component breakdown
- Interface design
- UI wireframes
- Technology rationale

## Bash Script Version

**File**: `seo_image_processor.sh`

The original bash script that the Tauri app wraps. This script handles:
- Image processing with cwebp/mozjpeg/zopfli
- Ollama AI integration for SEO naming
- Batch processing

---

## Main Implementation

The **primary/production version** is in the root directory:
- Python-based with Dear PyGui
- Full Qwen2.5-VL integration
- Both CLI and GUI modes
- Actively maintained and updated

Refer to the main `README.md` in the repository root for documentation on the production version.
