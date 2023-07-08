import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:                # เรียกใช้  Microphone พื้นฐานของระบบ
  audio = r.listen(source)                   # รับเสียงเข้ามาแล้วประมวลผลส่งไปยัง Google Speech Recognition API
try:
  print("You said " + r.recognize_google(audio,language = "th-TH"))   # แสดงข้อความจากเสียงด้วย Google Speech Recognition
except LookupError:                            # ประมวลผลแล้วไม่รู้จักหรือเข้าใจเสียง
  print("Could not understand audio")
