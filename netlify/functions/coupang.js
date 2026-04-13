// 내부 보수 및 업데이트 중
// 2026-04-13 ~ (재개 미정)

const MAINTENANCE_RESPONSE = {
  maintenance: true,
  status: "under_maintenance",
  message:
    "현재 내부 보수 및 업데이트 중입니다. 곧 업데이트된 모습으로 다시 찾아뵙겠습니다.",
  message_en:
    "Currently undergoing internal maintenance and updates. Service will resume soon.",
  since: "2026-04-13",
  inquiry: "https://github.com/uju777/coupang-mcp/issues",
};

exports.handler = async () => ({
  statusCode: 503,
  headers: {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "Access-Control-Allow-Origin": "*",
    "Retry-After": "86400",
  },
  body: JSON.stringify(MAINTENANCE_RESPONSE, null, 2),
});
