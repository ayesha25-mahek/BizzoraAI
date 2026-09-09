import tkinter as tk
from tkinter import filedialog

from services.document_reader import DocumentReader
from services.content_intelligence import ContentIntelligence


def select_file():

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select source document",
        filetypes=[
            ("Supported Documents", "*.pdf *.docx *.txt *.pptx"),
            ("PDF files", "*.pdf"),
            ("Word Documents", "*.docx"),
            ("Text files", "*.txt"),
            ("PowerPoint files", "*.pptx"),
        ],
    )

    root.destroy()

    return file_path


print("=" * 60)
print("              BIZZORAAI")
print("        DOCUMENT INTELLIGENCE")
print("=" * 60)

print("\n📂 Select your source document...")

file_path = select_file()

if not file_path:
    print("\n❌ No file selected.")
    exit()


print("\n✓ Selected:")
print(file_path)


# ---------------------------------------------------------
# STEP 1: READ DOCUMENT
# ---------------------------------------------------------

reader = DocumentReader()

try:

    content = reader.read(file_path)

except Exception as e:

    print("\n❌ Document reading failed:")
    print(e)
    exit()


if not content.strip():

    print("\n❌ No readable content found.")
    exit()


print("\n✓ Text extracted successfully.")
print(f"Extracted characters: {len(content)}")


# ---------------------------------------------------------
# STEP 2: CONTENT INTELLIGENCE
# ---------------------------------------------------------

print("\n🧠 Sending content to Content Intelligence...")


try:

    engine = ContentIntelligence()

    content_model = engine.analyze(
        content,
        source_files=[file_path]
    )

except Exception as e:

    print("\n❌ Content Intelligence failed:")
    print(e)
    exit()


# ---------------------------------------------------------
# STEP 3: DISPLAY RESULT
# ---------------------------------------------------------

print("\n")
print("=" * 60)
print("          CONTENT INTELLIGENCE RESULT")
print("=" * 60)

print(content_model)


# ---------------------------------------------------------
# STEP 4: SAVE RESULT
# ---------------------------------------------------------

try:

    engine.save(
        content_model,
        "document_content_model.json"
    )

    print("\n✓ Content model saved.")

except Exception as e:

    print("\n⚠ Could not save content model:")
    print(e)


print("\n")
print("=" * 60)
print("       ✅ DOCUMENT PIPELINE COMPLETE")
print("=" * 60)