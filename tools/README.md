# Additional Tools

This directory contains additional utilities for photo management and processing.

## Photo Sorter

`photo_sorter.py` - AI-powered photo organizer using Qwen2.5-VL vision model.

### Features

- **AI-Powered Categorization**: Uses Qwen2.5-VL to intelligently categorize photos
- **13 Smart Categories**: People, Nature, Objects, Documents, Architecture, Vehicles, Food, Technology, Art, Events, Sports, Animals, and Unclear
- **Parallel Processing**: Multi-threaded processing for faster batch operations
- **Flexible Modes**: Copy or move files
- **Progress Tracking**: Real-time progress updates
- **Duplicate Handling**: Automatically handles duplicate filenames

### Requirements

- Ollama running with Qwen2.5-VL model installed:
  ```bash
  ollama serve
  ollama pull qwen2.5vl:7b
  ```

### Usage

```bash
# Basic usage (copy mode)
python tools/photo_sorter.py /path/to/photos /path/to/sorted

# Move files instead of copying
python tools/photo_sorter.py /path/to/photos /path/to/sorted --move

# Process only first 50 photos (for testing)
python tools/photo_sorter.py /path/to/photos /path/to/sorted --limit 50

# Sequential processing (no parallel)
python tools/photo_sorter.py /path/to/photos /path/to/sorted --no-parallel
```

### Categories

| Category | Description |
|----------|-------------|
| **people** | Photos with people, faces, portraits, groups |
| **nature** | Landscapes, scenery, plants, natural environments |
| **objects** | Items, products, tools, everyday objects |
| **documents** | Text, papers, documents, screenshots, receipts |
| **architecture** | Buildings, houses, structures, interiors |
| **vehicles** | Cars, trucks, motorcycles, boats, planes |
| **food** | Meals, cooking, restaurants, food items, drinks |
| **technology** | Computers, phones, electronics, gadgets, screens |
| **art** | Artwork, drawings, paintings, sculptures, creative content |
| **events** | Parties, celebrations, weddings, concerts, gatherings |
| **sports** | Athletic activities, games, competitions, outdoor activities |
| **animals** | Pets, wildlife, birds, insects, animals |
| **unclear** | Unclear, corrupted, or unidentifiable images |

### Output Structure

The tool creates subdirectories for each category:

```
/path/to/sorted/
├── people/
├── nature/
├── objects/
├── documents/
├── architecture/
├── vehicles/
├── food/
├── technology/
├── art/
├── events/
├── sports/
├── animals/
└── unclear/
```

### Performance

- Processing speed: 4-8 seconds per image (Qwen2.5-VL 7B model)
- Parallel processing: Uses up to 4 concurrent workers by default
- Supports common image formats: JPG, JPEG, PNG, GIF, BMP, WEBP, TIFF, HEIC

### Integration

The photo sorter integrates seamlessly with the main SEO Image Converter:

- Uses the same `AIImageAnalyzer` class
- Shares configuration from `config.yaml`
- Uses the same logging system
- Compatible with the same Ollama setup

### Example Output

```
INFO: Initialized photo sorter: /home/user/photos → /home/user/sorted
INFO: Mode: COPY files
INFO: Found 150 images, processing 150...
INFO: Copied vacation_beach.jpg → nature/
INFO: Copied family_portrait.jpg → people/
INFO: Copied receipt_scan.jpg → documents/
INFO: Progress: 50/150 (33%)
...
============================================================
PHOTO SORTING COMPLETE
============================================================
Total processed: 150 images
Successfully sorted: 148
Failed: 2

Category breakdown:
  People           42 images - Photos with people, faces, portraits, groups
  Nature           35 images - Landscapes, scenery, plants, natural environments
  Food             18 images - Meals, cooking, restaurants, food items, drinks
  Architecture     15 images - Buildings, houses, structures, interiors
  Documents        12 images - Text, papers, documents, screenshots, receipts
  Objects           8 images - Items, products, tools, everyday objects
  Animals           7 images - Pets, wildlife, birds, insects, animals
  Technology        6 images - Computers, phones, electronics, gadgets, screens
  Events            3 images - Parties, celebrations, weddings, concerts, gatherings
  Vehicles          2 images - Cars, trucks, motorcycles, boats, planes
```

### Tips

1. **Test First**: Use `--limit 10` to test on a small batch before processing large collections
2. **Backup**: In copy mode (default), originals are preserved automatically
3. **Review**: Check the "unclear" folder for any images the AI couldn't categorize
4. **Speed**: Use `--no-parallel` if you experience issues with concurrent processing
5. **Accuracy**: The Qwen2.5-VL model provides excellent categorization accuracy (96.4% DocVQA score)

### Troubleshooting

**Error: "Ollama service not available!"**
- Start Ollama: `ollama serve`
- Verify model is installed: `ollama list`
- If model missing: `ollama pull qwen2.5vl:7b`

**Slow Processing**
- Enable parallel processing (default)
- Consider using a more powerful GPU
- Try the 7B model instead of larger variants

**Incorrect Categories**
- The AI chooses the most specific category for the primary subject
- Review the "unclear" folder for any misclassified images
- Categories are based on dominant content in the image
