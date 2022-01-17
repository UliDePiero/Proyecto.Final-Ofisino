FROM node:14-slim


WORKDIR /user/src/app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Fine tuning for production
# --------------------------

# Don't run as root, so give permissions to node user
COPY --chown=node:node . .
USER node

# Expose server port
EXPOSE 3000:3000
# To expose server outside docker network
ENV HOST=0.0.0.0 
# To avoid security problems for debug mode on libraries
ENV NODE_ENV production

CMD ["npm", "start"]
