# Coupang MCP

Claude에서 쿠팡 상품 검색, 골드박스 특가, 베스트 상품을 조회할 수 있는 MCP 서버입니다.

## 특징

**API 키 없이 바로 사용 가능!** - 별도 설정 없이 아래 설정만 추가하면 됩니다.

## 기능

- **상품 검색**: 키워드로 쿠팡 상품 검색
- **베스트 상품**: 카테고리별 베스트셀러 조회
- **골드박스**: 오늘의 특가/할인 상품
- **딥링크 생성**: 쿠팡 URL을 단축 링크로 변환

## 설치 방법

### 1. 설정 파일에 추가

`~/.claude/settings.json` (Mac) 또는 `%APPDATA%\Claude\settings.json` (Windows):

```json
{
  "mcpServers": {
    "coupang": {
      "command": "sh",
      "args": [
        "-c",
        "cd /path/to/coupang-mcp/client && uv run --with 'mcp[cli]' --with httpx python server.py"
      ]
    }
  }
}
```

### 2. 사용

Claude에서 바로 질문하세요:
- "쿠팡에서 에어팟 검색해줘"
- "가전디지털 베스트 상품 보여줘"
- "오늘 골드박스 특가 뭐 있어?"

## 카테고리 ID

| ID | 카테고리 |
|----|----------|
| 1001 | 여성패션 |
| 1002 | 남성패션 |
| 1010 | 뷰티 |
| 1012 | 식품 |
| 1016 | 가전디지털 |
| 1017 | 스포츠/레저 |
| 1024 | 헬스/건강식품 |
| 1029 | 반려동물용품 |

## License

MIT
