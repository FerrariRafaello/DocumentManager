# Document Manager API

A simple RESTful API built with Python and Flask to manage documents with properties such as number, creation date, and summary.

**Features**
- Create, retrieve, update, and delete documents via REST endpoints
- Document data stored in-memory with data validation
- Download document details as a text file from the web interface
- Clean, minimalistic HTML frontend for interacting with the API
- Logging for traceability and debugging
  
---

| Endpoint        | Method | Description                       |
|-----------------|--------|---------------------------------|
| `/documents`    | POST   | Create a new document            |
| `/documents/<number>` | GET    | Retrieve a document by number   |
| `/documents/<number>` | PUT    | Update the summary of a document|
| `/documents/<number>` | DELETE | Delete a document               |


---

**How to run**
Install dependencies:

-> pip install Flask

Run the app:

-> python3 app.py

-> Open your browser at http://localhost:5000 to use the frontend.

**Frontend**
- Use the web interface to create, get, update, and delete documents.
- When retrieving a document, it automatically downloads as a .txt file with its details.

---

**Technologies used**
- Python 3.8+
- Flask for REST API
- HTML, JavaScript for frontend
- Dataclasses for clean data handling 
- Logging for better traceability

License
MIT License
