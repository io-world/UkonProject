import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// /interview, /ai and /reset serve the HTML pages in public/ (folder index + trailing-slash redirect), not the React app.
const interviewPages = {
  name: 'interview-pages',
  configureServer(server) {
    server.middlewares.use((req, res, next) => {
      const path = req.url.split('?')[0]
      for (const dir of ['/interview', '/ai', '/reset']) {
        if (path === dir) { res.writeHead(301, { Location: `${dir}/` }); return res.end() }
        if (path === `${dir}/`) req.url = `${dir}/index.html`
      }
      next()
    })
  },
}

export default defineConfig({
  plugins: [interviewPages, react()],
  server: { port: 5173, proxy: { '/api': 'http://localhost:8000' } },
})
