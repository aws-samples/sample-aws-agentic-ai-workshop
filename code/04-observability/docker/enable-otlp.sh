#!/bin/bash

# ADOT + Jaeger 트레이싱 스택 시작 스크립트
# Strands Agent → ADOT (localhost:4318 HTTP) → Jaeger → UI (localhost:16686)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NETWORK_NAME="tracing-net"

echo "🔧 Docker 네트워크 생성..."
docker network create $NETWORK_NAME 2>/dev/null || true

echo "🚀 Jaeger 시작..."
docker run -d --name jaeger \
  --network $NETWORK_NAME \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  jaegertracing/jaeger:latest

echo "⏳ Jaeger 준비 대기 (5초)..."
sleep 5

echo "🚀 ADOT Collector 시작..."
docker run -d --name adot \
  --network $NETWORK_NAME \
  -v "$SCRIPT_DIR/otel-config.yaml:/etc/otel-config.yaml" \
  -p 4318:4318 \
  amazon/aws-otel-collector:latest \
  --config=/etc/otel-config.yaml

echo ""
echo "✅ 트레이싱 스택 시작 완료!"
echo ""
echo "📊 Jaeger UI: http://localhost:16686"
echo "📡 OTLP Endpoint: localhost:4318 (HTTP)"
echo ""
echo "종료하려면: ./stop-tracing.sh"
