FROM python:3.9.1-alpine

RUN pip install rq-dashboard==0.6.1
RUN pip install click==7.1.2  # Fix rq-dashboard: https://github.com/Parallels/rq-dashboard/issues/387

ENV DASHBOARD_PORT=${DASHBOARD_PORT:-9001}
ENV REDIS_URL=${REDIS_URL:-redis://redis:6379}

CMD rq-dashboard --redis-url $REDIS_URL --port $DASHBOARD_PORT --poll-interval 1000
