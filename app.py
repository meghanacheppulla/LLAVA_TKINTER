"""
LLaVA Image Assistant  (Tkinter + LLaVA via Ollama)
---------------------------------------------------
1. Upload any photo.
2. Type ANY question in the box at the bottom and press Enter / Ask.
3. LLaVA answers live, word by word. Follow-up questions work too.
"""
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageTk      # only used to show JPG/PNG previews
import ollama

MODEL = "llava"
PREVIEW = (380, 300)

SYSTEM_PROMPT = ("You are a helpful vision assistant. Look carefully at the image and "
                 "answer the user's question clearly and directly in simple English. "
                 "Keep answers short unless the user asks for detail.")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LLaVA Image Assistant")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1000, sw - 60), min(640, sh - 120)
        self.geometry(f"{w}x{h}+30+30")
        self.minsize(760, 480)
        self.configure(bg="#0f172a")

        self.image_path = None
        self.photo = None
        self.history = []          # chat messages (keeps follow-up context)
        self.busy = False

        self._build()

    # ---------------- UI ----------------
    def _build(self):
        ttk.Style(self).theme_use("clam")

        tk.Label(self, text="🖼️  LLaVA Image Assistant", bg="#0f172a", fg="#e2e8f0",
                 font=("Segoe UI", 18, "bold")).pack(pady=(10, 0))
        tk.Label(self, text="Upload a photo, then ask anything about it",
                 bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 10)).pack()

        # status bar and input row are packed FIRST at the bottom so they never get cut off
        self.status = tk.Label(self, text="Ready", bg="#0f172a", fg="#64748b",
                               anchor="w", font=("Segoe UI", 9))
        self.status.pack(side="bottom", fill="x", padx=16, pady=(0, 6))

        inp = tk.Frame(self, bg="#0f172a")
        inp.pack(side="bottom", fill="x", padx=16, pady=(0, 6))
        tk.Label(inp, text="Your question:", bg="#0f172a", fg="#e2e8f0",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        row = tk.Frame(inp, bg="#0f172a")
        row.pack(fill="x", pady=(2, 0))
        self.entry = tk.Entry(row, font=("Segoe UI", 12), bg="#f8fafc", fg="#0f172a",
                              relief="flat", insertbackground="#0f172a")
        self.entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.entry.bind("<Return>", lambda e: self.ask())
        self.ask_btn = tk.Button(row, text="Ask ➤", command=self.ask, bg="#6366f1", fg="white",
                                 activebackground="#4f46e5", activeforeground="white",
                                 font=("Segoe UI", 11, "bold"), relief="flat", padx=18)
        self.ask_btn.pack(side="left", padx=(8, 0), fill="y")

        body = tk.Frame(self, bg="#0f172a")
        body.pack(fill="both", expand=True, padx=16, pady=10)

        # left panel: image + buttons
        left = tk.Frame(body, bg="#1e293b", width=PREVIEW[0] + 20)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)
        self.preview = tk.Label(left, text="No image yet\n\nClick “Upload Image”",
                                bg="#1e293b", fg="#64748b", font=("Segoe UI", 11))
        self.preview.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Button(left, text="📂  Upload Image", command=self.upload, bg="#e2e8f0",
                  font=("Segoe UI", 10, "bold"), relief="flat", pady=8)\
            .pack(fill="x", padx=10, pady=(0, 6))
        tk.Button(left, text="🧹  Clear Chat", command=self.clear_chat, bg="#e2e8f0",
                  font=("Segoe UI", 10, "bold"), relief="flat", pady=8)\
            .pack(fill="x", padx=10, pady=(0, 10))

        # right panel: answers
        right = tk.Frame(body, bg="#1e293b")
        right.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(right)
        sb.pack(side="right", fill="y")
        self.out = tk.Text(right, wrap="word", bg="#0b1220", fg="#e2e8f0",
                           font=("Segoe UI", 12), relief="flat", padx=12, pady=12,
                           yscrollcommand=sb.set, state="disabled")
        self.out.pack(fill="both", expand=True)
        sb.config(command=self.out.yview)
        self.out.tag_config("you", foreground="#a5b4fc", font=("Segoe UI", 12, "bold"))
        self.out.tag_config("ai", foreground="#86efac")
        self.out.tag_config("err", foreground="#fca5a5")

        self._write("Welcome! Upload an image, then type your question below "
                    "(e.g. “What is the colour of the image?”, “What is in this photo?”).\n\n", "ai")

    # ---------------- helpers ----------------
    def _write(self, text, tag=None):
        self.out.config(state="normal")
        self.out.insert("end", text, tag)
        self.out.see("end")
        self.out.config(state="disabled")

    def clear_chat(self):
        self.history.clear()
        self.out.config(state="normal")
        self.out.delete("1.0", "end")
        self.out.config(state="disabled")

    def upload(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.gif")])
        if not path:
            return
        self.image_path = path
        img = Image.open(path).convert("RGB")
        img.thumbnail(PREVIEW)
        self.photo = ImageTk.PhotoImage(img)
        self.preview.config(image=self.photo, text="")
        self.clear_chat()                       # new image = new conversation
        self._write("Image loaded ✅  Now type your question below.\n\n", "ai")
        self.entry.focus_set()

    # ---------------- ask LLaVA ----------------
    def ask(self):
        if self.busy:
            return
        q = self.entry.get().strip()
        if not self.image_path:
            return messagebox.showinfo("No image", "Please upload an image first.")
        if not q:
            return
        self.entry.delete(0, "end")
        self._write(f"You: {q}\n", "you")
        self._write("AI: ", "ai")

        # the image is attached to the first question; follow-ups reuse the context
        msg = {"role": "user", "content": q}
        if not any("images" in m for m in self.history):
            msg["images"] = [self.image_path]
        self.history.append(msg)

        self.busy = True
        self.ask_btn.config(state="disabled")
        self.status.config(text="LLaVA is thinking…")
        threading.Thread(target=self._stream, daemon=True).start()

    def _stream(self):
        reply = ""
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history
            for chunk in ollama.chat(model=MODEL, messages=messages, stream=True):
                piece = chunk["message"]["content"]
                reply += piece
                self.after(0, self._write, piece, "ai")
            self.history.append({"role": "assistant", "content": reply})
            self.after(0, self._write, "\n\n")
        except Exception as e:
            self.history.pop()                  # drop the failed question
            self.after(0, self._write,
                       f"\nCould not reach LLaVA: {e}\n"
                       f"Make sure Ollama is running and you ran:  ollama pull {MODEL}\n\n", "err")
        finally:
            self.after(0, self._done)

    def _done(self):
        self.busy = False
        self.ask_btn.config(state="normal")
        self.status.config(text="Ready")
        self.entry.focus_set()


if __name__ == "__main__":
    App().mainloop()
