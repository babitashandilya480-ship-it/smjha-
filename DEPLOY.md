# Samjha public deployment

The hosted chat is a Vercel Vite frontend plus a single persistent FastAPI service. Do not deploy the API as a Vercel Function: its SQLite data, background chat runs, and event stream require a long-lived process and persistent storage.

## Before deploying

- Create a private Git repository for this source. Review the files before pushing. Never commit `backend/.env`, `backend/.env.cloud`, `data/`, SQLite files, PDFs, or API keys.
- Set up a paid Render web-service plan with a persistent disk (see `render.yaml`). A free ephemeral disk loses accounts and chats on redeploy.
- Obtain a Cheaper Inference API key and set an explicit request allowance/budget. This is the existing cloud adapter; no model weights are trained by PDF uploads.
- Optional web research requires a Tavily key.

## Backend (Render)

Create a Blueprint from the private repository and `render.yaml`. The Docker service runs one Uvicorn worker because chat jobs and their cancellation state are process-local. Set these environment variables in Render's private dashboard:

| Variable | Value |
| --- | --- |
| `SAMJHA_PUBLIC_ORIGIN` | Exact HTTPS production Vercel URL, without trailing slash |
| `SAMJHA_ALLOWED_HOSTS` | Render service hostname, without `https://` |
| `CI_API_KEY` | Cloud inference API key |
| `CI_MODEL` | A model supported by that key |
| `CI_MAX_REQUESTS` | Explicit positive lifetime request allowance; review uses multiple calls |
| `TAVILY_API_KEY` | Optional research key |

`CI_ENABLED=true` and both database paths are set by the Blueprint. If the Render hostname or Vercel URL differs from the planned name, update the values and redeploy. Confirm `/api/health` responds and `/api/v1/auth/guest` can create a session over HTTPS before publishing the UI. Back up the persistent disk separately.

## Frontend (Vercel)

Import the same private repository into Vercel, set **Root Directory** to `frontend/samjha-frontend`, and add the project environment variable `SAMJHA_API_ORIGIN` as the exact HTTPS Render origin, without a path. `vercel.mjs` refuses to build without it, rewrites `/api/*` to Render, and sends all other routes to the SPA. The build sets hosted mode: guest accounts are isolated, cloud chat is selected by default, and local-only learning endpoints are not advertised.

After deployment, verify a new guest can start a chat, receive a streamed answer, upload a PDF, sign out, and that a second browser does not see the first guest's chats. Verify a registered account can sign in after a backend restart. Check that research works only when its key is configured. Do not publish the site merely because the static UI loads.

## Current limitations

- Home, Learn, Mistakes, and Progress use the older shared local database. The public API blocks those routes to prevent cross-user data exposure. The hosted site currently exposes the Samjha chat workspace only. Those sections require a tenant-aware data migration before they can be published.
- The five supplied local PDFs are deliberately excluded from the Docker image. Users can upload their own PDFs. Publishing the supplied corpus requires an explicit decision to make its text available to hosted users.
- Guest sessions are not recoverable after their cookie is lost. Encourage account creation for durable access; password recovery and email verification are not implemented.
- Render disk hosting and cloud inference may incur charges. Set provider spending limits and monitor use before sharing the URL widely.
