# Arabic Law LLM Inference Application

This project is a full-stack web application that serves a fine-tuned Large Language Model (LLM) on a dataset of Arabic legal information. The backend is built with FastAPI to provide a robust API for model inference, while the frontend is a simple web interface using HTML, CSS, and JavaScript.

## ⚙️ Setup and Installation

### Prerequisites

* Python 3.12 or higher
* `uv` or `pip` for dependency management
* Git

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install the required dependencies. It's recommended to use a virtual environment.
    ```bash
    # Using uv (if you have it)
    uv pip install -r requirements.txt

    # Or using pip
    pip install -r requirements.txt
    ```

### Running Locally

To run the application locally, you can use Uvicorn. Ensure you are in the `backend` directory.

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload