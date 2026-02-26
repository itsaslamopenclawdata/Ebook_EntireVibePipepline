# Multi-stage build for Vibe PDF Frontend
FROM node:20-alpine as base

WORKDIR /app

# Install dependencies only when needed
FROM base as deps

# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat

COPY frontend/package.json frontend/package-lock.json* ./

RUN npm ci --legacy-peer-deps

# Development stage
FROM base as development

COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ ./

ENV NODE_ENV=development

EXPOSE 3000

CMD ["npm", "run", "dev"]

# Build stage
FROM base as builder

COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ ./

ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# Production stage
FROM base as production

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
