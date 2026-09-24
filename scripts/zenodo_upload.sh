#!/usr/bin/env bash
# scripts/zenodo_upload.sh — Upload and mint DOI on Zenodo for PIREUS
#
# Usage:
#   export ZENODO_TOKEN="your-token"
#   bash scripts/zenodo_upload.sh
#
# Supports sandbox mode:
#   export ZENODO_SANDBOX=1
#   export ZENODO_TOKEN="sandbox-token"
#   bash scripts/zenodo_upload.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARCHIVE="/tmp/pireus-v1.0.0.tar.gz"

echo "=== 1. Empacotando o repositório PIREUS para o Zenodo ==="
cd "$ROOT_DIR"
git archive --format=tar.gz --prefix=pireus-v1.0.0/ HEAD > "$ARCHIVE"
ARCHIVE_SHA=$(sha256sum "$ARCHIVE" | awk '{print $1}')
ARCHIVE_SIZE=$(du -h "$ARCHIVE" | cut -f1)
echo "  Arquivo gerado: $ARCHIVE"
echo "  Tamanho: $ARCHIVE_SIZE"
echo "  SHA-256: $ARCHIVE_SHA"

if [ -z "${ZENODO_TOKEN:-}" ]; then
    echo ""
    echo "================================================================="
    echo "  Pacote pronto para upload no Zenodo!"
    echo "  Para disparar o upload via API e mintar o DOI automaticamente:"
    echo "    export ZENODO_TOKEN=\"seu_token_aqui\""
    echo "    bash $0"
    echo "  Obtenha o token em: https://zenodo.org/account/settings/applications/tokens/new/"
    echo "  Ou ative a integração automática no GitHub em: https://zenodo.org/account/settings/github/"
    echo "================================================================="
    exit 0
fi

if [ "${ZENODO_SANDBOX:-0}" = "1" ]; then
    API="https://sandbox.zenodo.org/api"
    echo "[sandbox mode] Usando sandbox do Zenodo (prefixo 10.5072)"
else
    API="https://zenodo.org/api"
fi

FILENAME=$(basename "$ARCHIVE")
METADATA_FILE="$ROOT_DIR/.zenodo.json"

echo "=== 2. Criando novo depósito no Zenodo ==="
DEPOSIT_RESPONSE=$(curl -s -H "Authorization: Bearer $ZENODO_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{}' \
    "$API/deposit/depositions")

DEPOSIT_ID=$(echo "$DEPOSIT_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null || true)
BUCKET_URL=$(echo "$DEPOSIT_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['links']['bucket'])" 2>/dev/null || true)

if [ -z "$DEPOSIT_ID" ] || [ "$DEPOSIT_ID" = "None" ]; then
    echo "Erro: Falha ao criar depósito."
    echo "$DEPOSIT_RESPONSE"
    exit 1
fi
echo "  Depósito ID: $DEPOSIT_ID"
echo "  Bucket URL: $BUCKET_URL"

echo "=== 3. Enviando arquivo $FILENAME ($ARCHIVE_SIZE) ==="
UPLOAD_RESPONSE=$(curl -s --upload-file "$ARCHIVE" \
    -H "Authorization: Bearer $ZENODO_TOKEN" \
    "$BUCKET_URL/$FILENAME")

echo "=== 4. Vinculando metadados científicos (.zenodo.json) ==="
META_PAYLOAD=$(python3 -c "import json; m=json.load(open('$METADATA_FILE')); print(json.dumps({'metadata': m}))")
META_RESPONSE=$(curl -s -X PUT \
    -H "Authorization: Bearer $ZENODO_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$META_PAYLOAD" \
    "$API/deposit/depositions/$DEPOSIT_ID")

META_TITLE=$(echo "$META_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['metadata']['title'])" 2>/dev/null || true)
echo "  Título Registrado: $META_TITLE"

echo ""
echo "Depósito pronto em rascunho:"
echo "  $API/deposit/depositions/$DEPOSIT_ID"
echo ""

read -r -p "Publicar agora no Zenodo e mintar DOI definitivo? [y/N] " CONFIRM
if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    echo "=== 5. Publicando e emitindo DOI ==="
    PUB_RESPONSE=$(curl -s -X POST \
        -H "Authorization: Bearer $ZENODO_TOKEN" \
        "$API/deposit/depositions/$DEPOSIT_ID/actions/publish")
    DOI=$(echo "$PUB_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['doi'])" 2>/dev/null || true)
    RECORD_URL=$(echo "$PUB_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['links']['record_html'])" 2>/dev/null || true)
    
    if [ -n "$DOI" ] && [ "$DOI" != "None" ]; then
        echo "=========================================="
        echo "  PUBLICADO COM SUCESSO!"
        echo "  DOI: $DOI"
        echo "  URL: $RECORD_URL"
        echo "=========================================="
    else
        echo "Erro ao publicar: $PUB_RESPONSE"
        exit 1
    fi
else
    echo "Rascunho mantido no Zenodo. Conclua a publicação quando desejar na interface web."
fi
