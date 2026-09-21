# Fortune Module 4 Frontend

Next.js frontend for the personal knowledge base and privacy surfaces of Module 4. The visual
system follows `Slyvia0425/fortune`; the data calls target this repository's FastAPI service. The
main workspace includes a retrieval agent that answers from the current user's collections, notes,
and tags while preserving the matching `source_id` references.

## Local development

Start the Module 4 API on port `8000`, then run:

```bash
cp .env.example .env.local
npm install
npm run dev
```

Open <http://localhost:3000>.

## Remote browser access

Set `NEXT_PUBLIC_MODULE4_API_BASE_URL` to an address reachable from the browser before building or
starting the frontend. The FastAPI service must also allow the frontend origin through
`CORS_ORIGINS`.

Local network example:

```bash
NEXT_PUBLIC_MODULE4_API_BASE_URL=http://192.168.1.20:8000 npm run dev -- --hostname 0.0.0.0
```

For a non-local network, terminate TLS in a reverse proxy and use an HTTPS API origin. Set
`REQUIRE_USER_HEADER=true` on the API and replace the development identity with the authenticated
pseudonymous user id.

## Production

```bash
npm run build
npm start -- --hostname 0.0.0.0 --port 3000
```

The browser calls the API directly. Therefore, `NEXT_PUBLIC_MODULE4_API_BASE_URL` is a build-time
value in production and must be set before `npm run build` when the frontend and API are on
different hosts.
