LLaVA Tkinter – AI Image Assistant
A desktop application that lets users upload an image and ask natural-language questions about it. It uses the LLaVA vision-language model, served locally through Ollama, with a Tkinter graphical interface. All processing runs on the user's machine, so no images are sent to the cloud.
Features
Upload images (PNG, JPG, JPEG, WEBP, BMP, GIF) and ask any question about them
Live, streaming answers displayed word by word
Region zoom: drag a box over a small or distant detail; the app crops, enlarges and sharpens it before analysis
Model selector for installed LLaVA variants (`llava`, `llava:13b`, `llava:34b`)
Optional follow-up mode that remembers earlier questions
Prompt design that discourages guessing: the model states when a detail is unclear
Fully offline after setup
Tech Stack
Component	Purpose
Python 3.10+	Core language
Tkinter	Desktop GUI
Ollama	Local model runtime
LLaVA	Vision-language model
Pillow	Image preview, cropping and preprocessing
Installation
Install Python 3.10+ and Ollama.
Download a model:
```bash
   ollama pull llava          # ~4.7 GB, fastest
   ollama pull llava:13b      # ~8 GB, more accurate (16 GB+ RAM recommended)
   ```
Clone the repository and install dependencies:
```bash
   git clone https://github.com/meghanacheppulla/LLAVA_TKINTER.git
   cd LLAVA_TKINTER
   pip install -r requirements.txt
   ```
Usage
```bash
python app.py
```
Click Upload Image.
(Optional) Drag on the image to zoom into a specific area.
Type a question in the Your question box and press Enter.
Example questions: "What is the colour of the image?", "Is this person wearing an ID card?", "Describe the scene."
Limitations
LLaVA is a compact local model. It can make mistakes on very small details, crowded scenes or exact text. Use the zoom feature and a larger model for better accuracy, and verify important results manually.
Project Structure
```
LLAVA_TKINTER/
├── app.py
├── requirements.txt
└── README.md
```
