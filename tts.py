from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torch
import random
import string
import soundfile as sf

class TTS:
    """
    Class to handle converting text strings to audio files
    """

    def __init__(self):
        """
        Initialization method
        """


        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # load the processor
        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        # load the model
        self.model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(self.device)
        # load the vocoder, that is the voice encoder
        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan").to(self.device)
        # we load this dataset to get the speaker embeddings
        self.embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")

        # speaker ids from the embeddings dataset
        self.speakers = {
            'awb': 0,     # Scottish male
            'bdl': 1138,  # US male
            'clb': 2271,  # US female
            'jmk': 3403,  # Canadian male
            'ksp': 4535,  # Indian male
            'rms': 5667,  # US male
            'slt': 6799   # US female
        }

    def save_text_to_speech(self, text, speaker=None):

        # preprocess text
        inputs = self.processor(text=text, return_tensors="pt").to(self.device)
        if speaker is not None:
            # load xvector containing speaker's voice characteristics from a dataset
            speaker_embeddings = torch.tensor(self.embeddings_dataset[speaker]["xvector"]).unsqueeze(0).to(self.device)
        else:
            # random vector, meaning a random voice
            speaker_embeddings = torch.randn((1, 512)).to(self.device)
        # generate speech with the models
        speech = self.model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=self.vocoder)
        if speaker is not None:
            # if we have a speaker, we use the speaker's ID in the filename
            output_filename = f"{speaker}-{'-'.join(text.split()[:6])}.mp3"
        else:
            # if we don't have a speaker, we use a random string in the filename
            random_str = ''.join(random.sample(string.ascii_letters+string.digits, k=5))
            output_filename = f"{random_str}-{'-'.join(text.split()[:6])}.mp3"
        # save the generated speech to a file with 16KHz sampling rate
        sf.write(output_filename, speech.cpu().numpy(), samplerate=16000)
        # return the filename for reference
        return output_filename
    
    def loadFile(self, filePath):
        print("todo")


if __name__ == "__main__":

    print("Running TTS")
    tts = TTS()
    #tts.save_text_to_speech("Python is my favorite programming language", speaker=tts.speakers["slt"])
