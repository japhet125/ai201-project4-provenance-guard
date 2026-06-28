from flask import Flask, request, jsonify
from uuid import uuid4

from detector import analyze_with_groq
from audit import write_log, load_log
from heuristics import calculate_stylometric_score
from confidence import combine_scores, classify_from_score
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from labels import generate_label
from appeals import submit_appeal


app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Provenance Guard API is running."
    })


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
def submit():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    text = data.get("text")
    creator_id = data.get("creator_id")

    if not text or not creator_id:
        return jsonify({
            "error": "Both 'text' and 'creator_id' are required."
        }), 400

    content_id = str(uuid4())

    llm_result = analyze_with_groq(text)
    stylometric_result = calculate_stylometric_score(text)

    combined_score = combine_scores(
        llm_score=llm_result["score"],
        stylometric_score=stylometric_result["score"]
    )

    attribution = classify_from_score(combined_score)

    response = {
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": attribution,
        "confidence": combined_score,
        "label": generate_label(attribution),
        "signals": {
            "llm_score": llm_result["score"],
            "llm_reason": llm_result["reason"],
            "stylometric_score": stylometric_result["score"],
            "stylometric_metrics": stylometric_result["metrics"]
        },
        "status": "classified"
    }

   

    log_entry = {
        "event_type": "submission",
        "content_id": content_id,
        "creator_id": creator_id,
        "text_preview": text[:120],
        "attribution": response["attribution"],
        "confidence": response["confidence"],
        "llm_score": llm_result["score"],
        "llm_reason": llm_result["reason"],
        "stylometric_score": stylometric_result["score"],
        "stylometric_metrics": stylometric_result["metrics"],
        "label": response["label"],
        "status": "classified"
    }

    write_log(log_entry)

    return jsonify(response)


@app.route("/log", methods=["GET"])
def get_log():
    return jsonify({
        "entries": load_log()
    })
@app.route("/appeal", methods=["POST"])
def appeal():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    content_id = data.get("content_id")
    creator_reasoning = data.get("creator_reasoning")

    if not content_id or not creator_reasoning:
        return jsonify({
            "error": "Both 'content_id' and 'creator_reasoning' are required."
        }), 400

    result = submit_appeal(content_id, creator_reasoning)

    if not result["found"]:
        return jsonify(result), 404

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5050)