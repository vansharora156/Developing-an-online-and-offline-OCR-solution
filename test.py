import easyocr
import sys
import os

def run_ocr(image_path, lang='en'):
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return

    print(f"--- Initializing OCR ({lang}) ---")
    reader = easyocr.Reader([lang])
    
    print(f"--- Processing {image_path} ---")
    result = reader.readtext(image_path)
    
    print("\n------ OCR OUTPUT ------")
    full_text = []
    for item in result:
        text = item[1]
        print(text)
        full_text.append(text)
    
    # Save result to text file
    output_info = f"output/{os.path.basename(image_path)}_result.txt"
    os.makedirs("output", exist_ok=True)
    with open(output_info, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    
    print(f"\n✅ Result saved to {output_info}")

if __name__ == "__main__":
    img = "test.png" # Default
    if len(sys.argv) > 1:
        img = sys.argv[1]
    
    run_ocr(img)
