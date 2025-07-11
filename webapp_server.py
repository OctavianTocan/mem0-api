# webapp_server.py

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# This module is responsible for serving the static front-end application (e.g., a React or Vue app).
# It's designed to be mounted into the main FastAPI application (`mem0_api.py`)
# to allow both the API and the web app to be served from the same port.

app = FastAPI()

# -- Define the location of the built web application files --
static_dir = "mem0-webapp/dist"
index_file = os.path.join(static_dir, "index.html")

if os.path.exists(static_dir):
    # Mount the 'assets' directory. Modern web bundlers (like Vite) place compiled
    # JavaScript, CSS, and other static assets in a specific folder (usually 'assets').
    # This line ensures that requests for these files (e.g., /assets/index-*.js)
    # are served directly from the filesystem.
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(static_dir, "assets")),
        name="assets",
    )

    # This catch-all route is the core of serving a Single Page Application (SPA).
    # It directs any request that hasn't been matched yet (i.e., it's not an API route
    # or a static asset) to the main `index.html` file. The client-side router
    # then interprets the URL and renders the appropriate view.
    @app.get("/{catch_all:path}")
    def serve_spa(catch_all: str):
        if os.path.exists(index_file):
            return FileResponse(index_file)
        else:
            raise HTTPException(status_code=404, detail="index.html not found")

else:

    @app.get("/")
    def root():
        raise HTTPException(
            status_code=404,
            detail="Web app not built. Run 'npm run build' in mem0-webapp directory",
        )
