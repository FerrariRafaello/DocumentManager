from dataclasses import dataclass
from typing import Dict, Optional
from flask import Flask, request, jsonify, Response, send_file
import logging
import datetime
import io

# Setup logging for traceability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Document:
    number: str
    creation_date: datetime.date
    summary: str

    def serialize(self) -> Dict[str, str]:
        return {
            "number": self.number,
            "creation_date": self.creation_date.isoformat(),
            "summary": self.summary,
        }

    def to_text(self) -> str:
        """Generate a text representation of the document for download."""
        return (
            f"Document Number: {self.number}\n"
            f"Creation Date: {self.creation_date.isoformat()}\n"
            f"Summary:\n{self.summary}"
        )

class DocumentService:
    _documents: Dict[str, Document] = {}

    @classmethod
    def create_document(cls, number: str, creation_date: str, summary: str) -> Document:
        date_obj = datetime.datetime.strptime(creation_date, "%Y-%m-%d").date()
        doc = Document(number=number, creation_date=date_obj, summary=summary)
        cls._documents[number] = doc
        logger.info(f"Document created: {doc}")
        return doc

    @classmethod
    def get_document(cls, number: str) -> Optional[Document]:
        return cls._documents.get(number)

    @classmethod
    def update_summary(cls, number: str, summary: str) -> Optional[Document]:
        doc = cls._documents.get(number)
        if doc:
            doc.summary = summary
            logger.info(f"Document updated: {doc}")
            return doc
        return None

    @classmethod
    def delete_document(cls, number: str) -> bool:
        if number in cls._documents:
            del cls._documents[number]
            logger.info(f"Document deleted: {number}")
            return True
        return False

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Document Manager</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 600px; margin: 30px auto; padding: 0 15px; }
  input, textarea, button { width: 100%; padding: 8px; margin: 6px 0 12px; box-sizing: border-box; }
  button { cursor: pointer; }
  #result { background: #f5f5f5; padding: 12px; white-space: pre-wrap; border-radius: 5px; }
</style>
</head>
<body>

<h1>Document Manager</h1>

<section>
  <h2>Create Document</h2>
  <input type="text" id="createNumber" placeholder="Document Number" />
  <input type="date" id="createDate" />
  <textarea id="createSummary" placeholder="Summary"></textarea>
  <button onclick="createDocument()">Create Document</button>
</section>

<section>
  <h2>Get Document</h2>
  <input type="text" id="getNumber" placeholder="Document Number" />
  <button onclick="getDocument()">Get Document (Download)</button>
</section>

<section>
  <h2>Update Document Summary</h2>
  <input type="text" id="updateNumber" placeholder="Document Number" />
  <textarea id="updateSummary" placeholder="New Summary"></textarea>
  <button onclick="updateDocument()">Update Summary</button>
</section>

<section>
  <h2>Delete Document</h2>
  <input type="text" id="deleteNumber" placeholder="Document Number" />
  <button onclick="deleteDocument()">Delete Document</button>
</section>

<h2>Result</h2>
<pre id="result">No action performed yet.</pre>

<script>
const apiBase = '/documents';

async function createDocument() {
  const number = document.getElementById('createNumber').value;
  const creation_date = document.getElementById('createDate').value;
  const summary = document.getElementById('createSummary').value;
  if (!number || !creation_date || !summary) {
    alert('Please fill all fields to create a document.');
    return;
  }
  const response = await fetch(apiBase, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({number, creation_date, summary})
  });
  const data = await response.json();
  document.getElementById('result').textContent = JSON.stringify(data, null, 2);
}

async function getDocument() {
  const number = document.getElementById('getNumber').value;
  if (!number) {
    alert('Please enter a document number.');
    return;
  }
  // Request the file to be downloaded
  const response = await fetch(`${apiBase}/${number}/download`);
  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${number}_document.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    document.getElementById('result').textContent = `Document ${number} downloaded!`;
  } else {
    const data = await response.json();
    document.getElementById('result').textContent = `Error: ${response.status} - ${data.error || 'Document not found'}`;
  }
}

async function updateDocument() {
  const number = document.getElementById('updateNumber').value;
  const summary = document.getElementById('updateSummary').value;
  if (!number || !summary) {
    alert('Please enter both document number and new summary.');
    return;
  }
  const response = await fetch(`${apiBase}/${number}`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({summary})
  });
  const data = await response.json();
  if (response.ok) {
    document.getElementById('result').textContent = JSON.stringify(data, null, 2);
  } else {
    document.getElementById('result').textContent = `Error: ${response.status} - ${data.error || 'Update failed'}`;
  }
}

async function deleteDocument() {
  const number = document.getElementById('deleteNumber').value;
  if (!number) {
    alert('Please enter a document number.');
    return;
  }
  const response = await fetch(`${apiBase}/${number}`, { method: 'DELETE' });
  const data = await response.json();
  if (response.ok) {
    document.getElementById('result').textContent = data.message;
  } else {
    document.getElementById('result').textContent = `Error: ${response.status} - Document not found`;
  }
}
</script>

</body>
</html>
"""

@app.route("/")
def serve_index():
    return Response(HTML_PAGE, mimetype="text/html")

@app.route("/documents", methods=["POST"])
def create_document():
    try:
        data = request.get_json(force=True)
        number = data["number"]
        creation_date = data["creation_date"]
        summary = data["summary"]
        doc = DocumentService.create_document(number, creation_date, summary)
        return jsonify(doc.serialize()), 201
    except Exception as e:
        logger.error(f"Error creating document: {e}")
        return jsonify({"error": "Failed to create document"}), 400

@app.route("/documents/<number>", methods=["GET"])
def get_document(number):
    doc = DocumentService.get_document(number)
    if doc:
        return jsonify(doc.serialize()), 200
    else:
        return jsonify({"error": "Document not found"}), 404

@app.route("/documents/<number>/download", methods=["GET"])
def download_document(number):
    doc = DocumentService.get_document(number)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    content = doc.to_text()
    # Use in-memory bytes buffer for file sending
    buffer = io.BytesIO()
    buffer.write(content.encode("utf-8"))
    buffer.seek(0)

    filename = f"{number}_document.txt"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="text/plain",
    )

@app.route("/documents/<number>", methods=["PUT"])
def update_document(number):
    try:
        data = request.get_json(force=True)
        summary = data.get("summary")
        if not summary:
            return jsonify({"error": "Summary is required"}), 400
        doc = DocumentService.update_summary(number, summary)
        if doc:
            return jsonify(doc.serialize()), 200
        else:
            return jsonify({"error": "Document not found"}), 404
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        return jsonify({"error": "Failed to update document"}), 400

@app.route("/documents/<number>", methods=["DELETE"])
def delete_document(number):
    success = DocumentService.delete_document(number)
    if success:
        return jsonify({"message": f"Document {number} deleted"}), 200
    else:
        return jsonify({"error": "Document not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
