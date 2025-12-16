FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Bake NEXT_PUBLIC_* at build time if provided.
ARG NEXT_PUBLIC_LANGGRAPH_API_URL=/api
ARG NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID=roscoe_paralegal
ENV NEXT_PUBLIC_LANGGRAPH_API_URL=$NEXT_PUBLIC_LANGGRAPH_API_URL
ENV NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID=$NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0
ENV PORT=3000
COPY --from=builder /app ./
EXPOSE 3000
CMD ["npm", "start"]

