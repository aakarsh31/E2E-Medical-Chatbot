from flask import Blueprint
from flask import render_template,request,jsonify, Response
import logger as _logger_config  #Triggers only basicConfig
from src.chain import conversational_rag_chain
import logging
from src.extensions import limiter


chat_bp = Blueprint('chat',__name__)
logger = logging.getLogger(__name__)



@chat_bp.route('/')
def index():
    return render_template('chat.html')

@chat_bp.route("/get", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def chat():
    try:
        msg = request.form['msg']
        if not msg:
            return jsonify({"error":"Empty user message"}), 400
        session_id = request.form["session_id"]
        logger.info(f"Received user message: {msg}")
    except Exception as e:
        logger.warning(f'Invalid request: {e}')
        return jsonify({"error": "Invalid/Empty user message"}), 400

    try:
        response = conversational_rag_chain.stream(
            {"input": msg},
            config={"configurable": {"session_id": session_id}}
        )
    except Exception as e:
        logger.error(f"Pipeline failure: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    def generate():
        for chunk in response:
            if chunk.content:
                yield f"data: {chunk.content}\n\n"
        yield "data: [DONE]\n\n"

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )
