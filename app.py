import fitz
from flask import Flask, request, jsonify, render_template
from llm_gateway import get_llm_client, DEFAULT_MODEL

app = Flask(__name__)

# --- Extract PDF text on startup ---
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
        return ""

extracted_text = extract_text_from_pdf("Landon-Hotel.pdf")
with open("pdf_text.txt", "w", encoding="utf-8") as f:
    f.write(extracted_text)

# --- Load context ---
try:
    context = open("pdf_text.txt", "r").read()
    file_missing = False
except FileNotFoundError:
    context = ""
    file_missing = True

# --- Prompt template ---
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

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if file_missing:
        return jsonify({"answer": "I'm sorry, I currently have no information available. Please try again later."})

    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "Please ask a question."})

    formatted_prompt = hotel_assistant_template.format(context=context, question=question)
    try:
        client = get_llm_client()  # refreshes token if expired
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error: {e}"

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
