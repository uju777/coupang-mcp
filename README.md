---
title: Coupang MCP
emoji: 🛒
colorFrom: red
colorTo: yellow
sdk: docker
pinned: false
---

# Coupang MCP Server

Claude Desktop에서 쿠팡 상품을 검색하고 **실시간 최저가**를 확인할 수 있는 MCP 서버입니다.

## 주요 특징

| 기능 | 설명 |
|------|------|
| **실시간 가격** | 다나와에서 실제 판매 가격 조회 (쿠팡 API 가격보다 정확) |
| **로켓배송 분리** | 로켓배송 / 일반배송 상품 구분 표시 |
| **가격 형식** | `1,890,000원 (189만원)` - 정확한 가격 + 만원 환산 |
| **폴백 지원** | 다나와 조회 실패 시 쿠팡 API 가격 자동 사용 |

---

## 빠른 시작 (3분)

### 1. Claude Desktop 설정 파일 열기

**Mac:**
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 2. mcpServers에 추가

```json
{
  "mcpServers": {
    "coupang": {
      "command": "npx",
      "args": ["mcp-remote", "https://yuju777-coupang-mcp.hf.space/mcp"]
    }
  }
}
```

### 3. Claude Desktop 재시작

설정 저장 후 Claude Desktop을 완전히 종료했다가 다시 실행하세요.

---

## 사용 가능한 도구

| 도구 | 설명 | 예시 |
|------|------|------|
| `search_coupang_products` | 상품 검색 | "맥북 검색해줘" |
| `search_coupang_rocket` | 로켓배송만 검색 | "로켓배송 에어팟 찾아줘" |
| `search_coupang_budget` | 가격대별 검색 | "10만원 이하 키보드" |
| `compare_coupang_products` | 상품 비교표 | "아이패드 vs 갤럭시탭 비교" |
| `get_coupang_recommendations` | 인기 검색어 추천 | "요즘 뭐가 인기야?" |
| `get_coupang_seasonal` | 시즌/상황별 추천 | "설날 선물 추천" |
| `get_coupang_best_products` | 베스트 상품 | "전자제품 베스트" |
| `get_coupang_goldbox` | 골드박스 특가 | "오늘 특가 뭐있어?" |

---

## 사용 예시

Claude Desktop에서 자연어로 질문하면 됩니다:

```
"타이벡 감귤 검색해줘"
"20만원대 노트북 찾아줘"
"에어팟 프로 로켓배송으로"
"아빠 선물 뭐가 좋을까?"
"맥북에어 vs 맥북프로 비교해줘"
```

### 출력 예시

```
## rocket (3)

1. **Apple 2024 맥북 에어 13 M3**
   1,390,000원 (139만원)
   https://link.coupang.com/...

2. **Apple 에어팟 프로 2세대**
   269,000원 (27만원대)
   https://link.coupang.com/...

## normal (2)

1. **삼성전자 갤럭시 버즈3**
   159,000원 (16만원대)
   https://link.coupang.com/...
```

---

## 기술 구현

### 가격 조회 흐름

```
Claude Desktop
    ↓
HF Space (MCP 서버)
    ↓
Netlify 프록시 (도쿄) → 다나와 가격 조회
    ↓
가격 반환 (다나와 우선, 실패 시 쿠팡 API 폴백)
```

### 왜 프록시를 사용하나요?

HF Space는 해외 서버(미국/유럽)에서 실행됩니다. 다나와는 해외 IP를 차단하기 때문에, 아시아 리전(도쿄)의 Netlify 프록시를 경유합니다.

---

## 자주 묻는 질문

**Q: 가격이 "약 X만원대"로 부정확하게 나와요**
A: 다나와 조회가 실패하면 쿠팡 API 가격(부정확)이 표시됩니다. 대부분의 인기 상품은 다나와에서 정확한 가격을 가져옵니다.

**Q: 일부 상품에 가격이 안 나와요**
A: 다나와에 등록되지 않은 상품이거나, 쿠팡 전용 상품일 수 있습니다.

**Q: 로켓배송이 뭔가요?**
A: 쿠팡이 직접 배송하는 상품으로, 빠른 배송(당일/익일)이 가능합니다.

---

## 링크

- **MCP 엔드포인트:** `https://yuju777-coupang-mcp.hf.space/mcp`
- **HF Space:** https://huggingface.co/spaces/yuju777/coupang-mcp
- **GitHub:** https://github.com/uju777/coupang-mcp

---

## 라이선스

MIT License
