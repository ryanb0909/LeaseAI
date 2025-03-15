import assemblyai as aai
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from openai import OpenAI

class AI_Assistant:
    client = ElevenLabs(
        api_key="API-KEY", 
    )
    def __init__(self):
        aai.settings.api_key = "API-KEY"
        self.openai_client = OpenAI(api_key = "API-KEY")

        self.transcriber = None

        
        self.full_transcript = [
            {"role":"system", "content":"You are a highly skilled AI, answer any questions with a maximum of 1000 words"},
        ]
    
    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None
    
    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        print("Session ID:", session_opened.session_id)
        return

    def on_error(self, error: aai.RealtimeError):
        print("An error occured:", error)
        return

    def on_close(self):
        print("Closing Session")
        return

    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return

        if isinstance(transcript, aai.RealtimeFinalTranscript):
            self.generate_ai_response(transcript)
        else:
            print(transcript.text, end="\r")

    def start_transcription(self):
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate = 16000,
            on_data = self.on_data,
            on_error = self.on_error,
            on_open = self.on_open,
            on_close = self.on_close,
            end_utterance_silence_threshold = 1000
        )

        self.transcriber.connect()
        microphone_stream = aai.extras.MicrophoneStream(sample_rate =16000)
        self.transcriber.stream(microphone_stream)

    def generate_ai_response(self, transcript):

        self.stop_transcription()

        self.full_transcript.append({"role":"user", "content": transcript.text})
        print(f"\nPatient: {transcript.text}", end="\r\n")

        response = self.openai_client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = self.full_transcript
        )

        ai_response = response.choices[0].message.content

        self.generate_audio(ai_response)

        self.start_transcription()
        print(f"\nReal-time transcription: ", end="\r\n")

    def generate_audio(self, text):

        self.full_transcript.append({"role":"assistant", "content": text})
        print(f"\nAI Receptionist: {text}")

        audio_stream = self.client.generate(
            text = text,
            voice = "Brian",
            stream = True
        )

        stream(audio_stream)

greeting = "Hi Ryan, please ask me any question you like"
ai_assistant = AI_Assistant()
ai_assistant.generate_audio(greeting)
ai_assistant.start_transcription()
