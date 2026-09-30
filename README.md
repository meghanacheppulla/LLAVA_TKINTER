# LLaVA Image Assistant (Tkinter + LLaVA)

Upload any photo, type any question, and LLaVA answers live. Runs locally through Ollama.

## What to install
1. Python 3.10+  (Tkinter comes with Python on Windows/Mac; Linux: `sudo apt install python3-tk`)
2. Ollama         https://ollama.com/download
3. LLaVA model    `ollama pull llava`      (one time, about 4.7 GB)
4. Python packages:
       pip install -r requirements.txt
   (ollama = talks to LLaVA, Pillow = shows JPG/PNG previews inside Tkinter)

## Run
1. Start Ollama (open the Ollama app, or run `ollama serve`).
2. In this folder:  `python app.py`

## Use
1. Click **Upload Image**.
2. Type your question in the **Your question** box at the bottom, press **Enter** or **Ask**.
3. The answer streams live in the right panel. Ask follow-up questions about the same image.
4. **Clear Chat** resets the conversation. Uploading a new image also starts a fresh chat.

## Troubleshooting
- "Could not reach LLaVA": Ollama isn't running, or run `ollama pull llava`.
- First answer is slow: the model is loading into memory. Later answers are faster.
