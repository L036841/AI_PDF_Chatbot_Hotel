import fitz
from llm_gateway import get_llm_client, DEFAULT_MODEL

# --- Step 1: Extract text from PDF ---
def extract_text_from_pdf(pdf_file_path):
    try:
        doc = fitz.open(pdf_file_path)
        pdf_text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pdf_text += page.get_text("text")
        doc.close()
        return pdf_text
    except Exception as e:
        return f"Error extracting text: {e}"

pdf_path = "Landon-Hotel.pdf"
extracted_text = extract_text_from_pdf(pdf_path)

with open("pdf_text.txt", "w", encoding="utf-8") as f:
    f.write(extracted_text)

print("PDF text extracted successfully.")

# --- Step 2: Load context ---
try:
    context = open("pdf_text.txt", "r").read()
    file_missing = False
except FileNotFoundError:
    context = ""
    file_missing = True

# --- Step 3: Define prompt ---
hotel_assistant_template = """
You are a hotel assistant for Landon Hotel named "Night Manager".

STRICT RULES:
- Answer ONLY using the hotel information provided below between the <context> tags.
- Do NOT use your own knowledge or training data to fill in missing details.
- Do NOT guess or make up any information (prices, policies, amenities, etc.).
- If the answer is not found in the context, respond with: "I don't have that information. Please contact us directly."
- If the question is not related to Landon Hotel, respond with: "I can't assist you with that, sorry!"

<context>
{context}
</context>

Question: {question}
Answer:
"""

# --- Step 4: Run chatbot ---
client = get_llm_client()

def query_llm(question):
    if file_missing:
        print("I'm sorry, I currently have no information available to answer your question. Please try again later.")
        return
    formatted_prompt = hotel_assistant_template.format(context=context, question=question)
    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0,
        )
        print(response.choices[0].message.content)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"Error: {e}")

try:
    while True:
        query_llm(input())
except KeyboardInterrupt:
    print("\nGoodbye!")
