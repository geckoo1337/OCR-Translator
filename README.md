# OCR-Translator
Learning Python, a simple application with easyOCR, PyTorch, Qt5py and Deep-Translator.

It works, but it is not really useful because of a lack of precision reading text (but my Webcam is not really good - maybe the result could be better with a solid HD device). For this example - Russian text to English, I implemented a CUDA layer in order to get a powerful system using my GPU (Nvidia 3060-Ti = 20 fr/sec for me). Changing parameter (line 16), you can use this code computing video stream with the CPU - so less than 2 frames per second. The last line should be something about the *Antique Tira*, but obviously there is a misunderstanding translation which shows the harsh limitation of this application. For educational purposes only.

![OCRT](https://github.com/user-attachments/assets/38d34f2d-0397-41fe-b8f3-6ceabd901b73)
