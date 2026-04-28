from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# -----------------------------------------
# Course → Subject Mapping (internal logic)
# -----------------------------------------

COURSE_SUBJECT_MAP = {
    "ENGL 1101": ["composition", "writing"],
    "ENGL 1102": ["literature", "writing"],
    "PSYC 1101": ["psychology"],
    "BIOL 1107": ["biology"]
}

# -----------------------------------------
# Curated OER fallback (guaranteed demo results)
# -----------------------------------------

CURATED_OER = {
    "ENGL 1101": [
        {
            "title": "Writing for Success",
            "link": "https://open.lib.umn.edu/writingforsuccess/"
        },
        {
            "title": "Open Rhetoric",
            "link": 
"https://human.libretexts.org/Bookshelves/Composition/Open_Rhetoric"
        }
    ],
    "PSYC 1101": [
        {
            "title": "Psychology 2e",
            "link": "https://openstax.org/details/books/psychology-2e"
        }
    ],
    "BIOL 1107": [
        {
            "title": "Biology 2e",
            "link": "https://openstax.org/details/books/biology-2e"
        }
    ]
}

# -----------------------------------------
# Fake "LLM reasoning" (intent mapping)
# -----------------------------------------

def interpret_course(user_input):
    course = user_input.strip().upper()
    return COURSE_SUBJECT_MAP.get(course, [course.lower()])[0]

# -----------------------------------------
# OER Commons search (best effort)
# -----------------------------------------

def search_oer_commons(keyword):
    url = f"https://www.oercommons.org/api/search?f.search={keyword}"

    try:
        response = requests.get(url, timeout=8)
        if response.status_code != 200:
            return []
    except requests.RequestException:
        return []

    data = response.json()
    results = []

    for item in data.get("results", []):
        if item.get("license"):
            results.append({
                "title": item.get("title"),
                "link": 
f"https://www.oercommons.org{item.get('detail_url')}"
            })

    return results[:3]

# -----------------------------------------
# Routes
# -----------------------------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    course = user_message.strip().upper()

    keyword = interpret_course(course)
    results = search_oer_commons(keyword)

    # Fallback to curated OER if API returns nothing
    if not results and course in CURATED_OER:
        results = CURATED_OER[course]

    if not results:
        reply = "I couldn't find suitable open resources for that course. 
Try another subject."
    else:
        reply = "Here are recommended open educational resources:\n\n"
        for r in results:
            reply += f"• {r['title']}\n  {r['link']}\n\n"

    return jsonify({"reply": reply})

# -----------------------------------------
# Run app
# -----------------------------------------

if __name__ == "__main__":
    app.run(debug=True)

