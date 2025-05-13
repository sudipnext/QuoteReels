import asyncio
import edge_tts

class TTSClient:
    def __init__(self):
        pass

    def list_voices(self, lang: str = None):
        """
        List available voices. Optionally filter by language code (e.g., 'en', 'en-US').
        """
        async def get_voices():
            # Use the async list_voices function from edge_tts.voices
            voices = await edge_tts.voices.list_voices()
            if lang:
                voices = [v for v in voices if v["Locale"].startswith(lang)]
            return voices

        return asyncio.run(get_voices())

    def generate_voice(self, text: str, voice: str, output_file: str):
        """
        Generate speech from text using the specified voice and save to output_file.
        """
        async def synthesize():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)

        asyncio.run(synthesize())