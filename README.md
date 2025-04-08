# Reels Automator

![Reels Automator](https://img.shields.io/badge/Reels-Automator-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.6%2B-blue)

Reels Automator is a powerful Flask application that automates the creation of short-form video content. It fetches random quotes from a quotes API, analyzes them using the Gemini AI API, downloads relevant background videos from Coverr based on the analyzed category, and generates a professional video output combining these elements.

## ✨ Features

- 🔄 **Automated Quote Fetching**: Daily random quotes from a dedicated quotes API
- 🧠 **AI-Powered Analysis**: Uses Gemini AI to categorize and analyze quotes
- 🎥 **Smart Video Selection**: Downloads relevant background videos from Coverr
- 🎬 **Professional Video Generation**: Creates social media-ready vertical videos
- 🚀 **AWS-Ready**: Designed for deployment on AWS Lambda


## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sudipnext/QuoteReels.git
   ```

2. **Navigate to the project directory:**
   ```bash
   cd reels-automator
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
   QUOTES_API_KEY=your_quotes_api_key
   OUTPUT_DIR=path/to/output/directory
   ```

## 📋 Usage

### Running the Application

To start the application, execute:

```bash
python app.py
```

This will:
1. Fetch a random quote from the quotes API
2. Analyze the quote using Gemini AI
3. Download an appropriate background video from Coverr
4. Generate a video with the quote overlaid on the background
5. Save the output to the configured directory

### Advanced Usage

For batch processing or custom configurations, you can modify the settings in `config.py`.

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

We welcome contributions to Reels Automator! Here's how you can help:

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
- [MoviePy](https://zulko.github.io/moviepy/) - Video editing library