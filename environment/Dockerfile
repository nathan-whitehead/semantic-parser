FROM python:3.13-alpine

RUN apk add --no-cache gcc musl-dev libffi-dev

RUN adduser -D -h /home/runner runner
USER runner

WORKDIR /home/runner