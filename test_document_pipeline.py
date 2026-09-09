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
            (
                "Supported Documents",
                "*.pdf *.docx *.txt *.pptx"
            ),
            ("PDF files", "*.pdf"),
            ("Word Documents", "*.docx"),
            ("Text files", "*.txt"),
            ("PowerPoint files", "*.pptx"),
        ]
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


print(f"\n✓ File selected:")
print(file_path)


# ---------------------------------------------------------
# STEP 1: READ DOCUMENT
# ---------------------------------------------------------

reader = DocumentReader()

try:

    extracted_text = reader.read(file_path)

except Exception as e:

    print("\n❌ Document reading failed:")
    print(e)
    exit()


if not extracted_text.strip():

    print("\n❌ No readable text found in the document.")
    exit()


print("\n✓ Text extracted successfully.")

print("\nExtracted characters:", len(extracted_text))


# ---------------------------------------------------------
# STEP 2: UNDERSTAND CONTENT
# ---------------------------------------------------------

print("\n🧠 Sending content to Content Intelligence...")


engine = ContentIntelligence()

try:

    content_model = engine.analyze(
        extracted_text,
        source_files=[file_path]
    )

except Exception as e:

    print("\n❌ Content Intelligence failed:")
    print(e)
    exit()


# ---------------------------------------------------------
# STEP 3: DISPLAY RESULT
# ---------------------------------------------------------

engine.print_model(content_model)


# ---------------------------------------------------------
# STEP 4: SAVE RESULT
# ---------------------------------------------------------

engine.save(
    content_model,
    "document_content_model.json"
)


print("\n")
print("=" * 60)
print("       ✅ DOCUMENT PIPELINE COMPLETE")
print("=" * 60)

print("\nYour document has been:")
print("✓ Read")
print("✓ Analyzed")
print("✓ Converted into structured content")

print(
    "\nSaved to:"
    "\noutput/content/document_content_model.json"
)
