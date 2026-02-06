#!/bin/bash

echo "🛑 Parando AgroADB Demo..."

# Parar backend
if [ -f "backend/backend.pid" ]; then
    kill $(cat backend/backend.pid) 2>/dev/null
    rm backend/backend.pid
    echo "✅ Backend parado"
fi

# Parar frontend
if [ -f "frontend/frontend.pid" ]; then
    kill $(cat frontend/frontend.pid) 2>/dev/null
    rm frontend/frontend.pid
    echo "✅ Frontend parado"
fi

echo "✅ AgroADB Demo encerrada!"
