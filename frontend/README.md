# Frontend (Next.js + shadcn-style scaffold)

## Setup
```bash
cd frontend
npm install
npm run dev
```

## Environment
Create `.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

## Routes
- `/login`
- `/dashboard`
- `/resumes`
- `/resumes/[id]`
- `/tailor-runs`
- `/tailor-runs/[runId]`
- `/applications`

## Notes
- Uses local `X-Dev-User-Email` header from login page for development.
- API client types are in `src/lib/types.ts`.
