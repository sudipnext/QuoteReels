# QuoteReels

![QuoteReels](https://img.shields.io/badge/QuoteReels-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.6%2B-blue)

QuoteReels is a powerful Flask application that automates the creation of short-form video content. It fetches random or custom quotes, analyzes them using the Gemini AI API, downloads relevant background videos from Coverr, Pexels, or Pixabay, and generates a professional video output with AI voiceover.

## ✨ Features

- 🔄 **Automated Quote Fetching**: Get daily random quotes or use your own custom quotes
- 🧠 **AI-Powered Analysis**: Uses Gemini AI to categorize and analyze quotes for best video match
- 🎥 **Smart Video Selection**: Downloads relevant background videos from Coverr, Pexels, or Pixabay
- 🗣️ **AI Voiceover**: Choose from dozens of realistic voices for text-to-speech narration
- 🎬 **Professional Video Generation**: Creates social media-ready vertical videos (9:16)
- ⚡ **Fast & Memory-Efficient**: Optimized video processing with MoviePy
- 🚀 **API & Web UI**: User-friendly web interface and REST API endpoints
- 📥 **Download & Preview**: Instantly preview and download your generated videos

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sudipnext/QuoteReels.git
   ```

2. **Navigate to the project directory:**
   ```bash
   cd QuoteReels
   ```

3. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

4. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   Create a `.env` file in the root directory with the following variables:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   COVERR_API_KEY=your_coverr_api_key
   PEXELS_API_KEY=your_pexels_api_key
   PIXABAY_API_KEY=your_pixabay_api_key
   ```

## 📋 Usage

### Running the Application

To start the application, execute:

```bash
python app.py
```

This will:
1. Serve a web UI at `http://localhost:5000`
2. Allow you to generate videos from random or custom quotes
3. Let you choose the video provider (Coverr, Pexels, Pixabay) and AI voice
4. Preview and download your generated videos

### API Endpoints

- `GET /get-random-quote` — Fetch a random quote
- `POST /generate-video` — Generate a video from a quote (random or custom)
- `POST /generate-video-custom` — Generate a video from a custom quote
- `GET /list/voices` — List available AI voices
- `GET /api/videos` — List generated videos
- `GET /api/videos/<filename>` — Stream a generated video
- `GET /api/download/<filename>` — Download a generated video

### Advanced Usage

- **Custom Quotes**: Enter your own quote and author in the web UI
- **Voice Selection**: Choose from a wide range of AI voices (male/female, multiple languages)
- **Video Provider**: Select between Coverr, Pexels, or Pixabay for background video matching

## 🧪 Testing

Run the test suite to ensure everything is working correctly:

```bash
pytest
```

Or run individual test modules:

```bash
pytest tests/test_analyzer.py
```

## 🤝 Contributing

We welcome contributions to QuoteReels! Here's how you can help:

1. **Fork the repository** on GitHub
2. **Create a new branch** for your feature or bugfix
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes** and commit them
   ```bash
   git commit -m 'Add an amazing feature'
   ```
4. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Contribution Guidelines

- Follow the existing code style and conventions
- Add/update tests for any new functionality
- Make sure your code passes all tests
- Keep pull requests focused on a single topic
- Document any new functions, classes or modules
- Update the README if necessary

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Gemini AI](https://ai.google.dev/gemini-api) - AI analysis
- [Coverr](https://coverr.co/) - Video resources
- [Pexels](https://pexels.com/) - Video resources
- [Pixabay](https://pixabay.com/) - Video resources
- [MoviePy](https://zulko.github.io/moviepy/) - Video editing library
- [Edge TTS](https://github.com/ranyelhousieny/edge-tts) - Text-to-speech voices