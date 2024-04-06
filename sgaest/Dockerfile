# Install dependencies only when needed
FROM node:16-alpine AS builder

# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat

WORKDIR /app

COPY package.json .
COPY package-lock.json .
RUN npm ci --ignore-scripts # Dont run postinstall before we have copied the project

COPY . .
RUN npm run build


# Production image, copy all the files and run Svelte
FROM mhart/alpine-node:slim-16 AS runner
WORKDIR /app

# Production build
ENV NODE_ENV production

# Create user and group for the app
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nodejs

COPY --from=builder /app/build build/
COPY --from=builder /app/node_modules node_modules/
COPY package.json .

# Run the app
USER nodejs
EXPOSE 3000
ENV PORT 3000
CMD [ "node", "build" ]
