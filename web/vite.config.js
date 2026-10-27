import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// /interview serves the HTML deliverables in public/interview (folder index + trailing-slash redirect).
const interviewPages = {
  name: 'interview-pages',
  configureServer(server) {
    server.middlewares.use((req, res, next) => {
      const path = req.url.split('?')[0]
      if (path === '/interview') { res.writeHead(301, { Location: '/interview/' }); return res.end() }
      if (path === '/interview/') req.url = '/interview/index.html'
      next()
    })
  },
}

export default defineConfig({
  plugins: [interviewPages, react()],
  server: { port: 5173, proxy: { '/api': 'http://localhost:8000' } },
})
