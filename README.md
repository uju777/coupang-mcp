[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/uju777-coupang-mcp-badge.png)](https://mseep.ai/app/uju777-coupang-mcp)

---
title: Coupang MCP
emoji: 🛒
colorFrom: red
colorTo: yellow
sdk: docker
pinned: false
---

> ## ⚠️ 현재 내부 보수 및 업데이트 중입니다 (Under Maintenance)
>
> 서비스가 일시적으로 중단되었습니다.
> 개선 작업 후 더 나은 모습으로 다시 찾아뵙겠습니다.
>
> API 호출 시 HTTP 503 점검 응답이 반환됩니다.
>
> ---
>
> **Currently undergoing internal maintenance and updates.**
> Service is temporarily paused. We will be back soon with improvements.
> All API calls return HTTP 503 maintenance response.
>
> 문의 / Inquiry: [GitHub Issues](https://github.com/uju777/coupang-mcp/issues)

---

# Coupang MCP Server

Claude Desktop에서 쿠팡 상품을 검색하고 **실시간 최저가**를 확인할 수 있는 MCP 서버입니다.

## 주요 특징

| 기능              | 설명                                                    |
| ----------------- | ------------------------------------------------------- |
| **실시간 가격**   | 다나와에서 실제 판매 가격 조회 (쿠팡 API 가격보다 정확) |
| **로켓배송 분리** | 로켓배송 / 일반배송 상품 구분 표시                      |
| **가격 형식**     | `1,890,000원 (189만원)` - 정확한 가격 + 만원 환산       |
| **폴백 지원**     | 다나와 조회 실패 시 쿠팡 API 가격 자동 사용             |

---

## 빠른 시작 (3분)

### 1. Claude Desktop 설정 파일 열기

**Mac:**

```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**

```
%APPDATA%\Claude
```
