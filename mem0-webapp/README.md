# Mem0 Web App

This simple React + TypeScript app lets you view memories stored in a Mem0 instance and ask questions about them. It is configured with [Vite](https://vitejs.dev/) so it can be deployed easily on Netlify.

## Getting Started

```
# install dependencies
npm install

# start a dev server
npm run dev
```

## Deployment on Netlify

1. Push this repository to your own Git provider.
2. In Netlify create a new site from Git and select this folder as the base directory (`mem0-webapp`).
3. Set the build command to `npm run build` and the publish directory to `mem0-webapp/dist`.

Netlify will install dependencies, build the app and serve the static files.

## Usage

1. Enter the Mem0 instance URL and your API key.
2. Specify the user ID whose memories you want to view.
3. Click **Fetch Memories** to see all memories.
4. Ask a question in the input field and press **Ask** to query the instance.

The responses from the server are shown as JSON for simplicity.
