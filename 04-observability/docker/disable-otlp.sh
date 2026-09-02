#!/bin/bash

# ADOT + Jaeger 트레이싱 스택 종료 스크립트

echo "🛑 컨테이너 종료 중..."
docker stop adot jaeger 2>/dev/null || true

echo "🗑️  컨테이너 삭제 중..."
docker rm adot jaeger 2>/dev/null || true

echo "🔌 네트워크 삭제 중..."
docker network rm tracing-net 2>/dev/null || true

echo "✅ 트레이싱 스택 종료 완료!"
