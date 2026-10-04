"""IF-01 Payment Gateway รายเดิม (REQ-CON-003) อยู่หลัง interface นี้
ระบบจริงเขียน class ที่เรียก HTTP ของ gateway; ตอน test ใช้ FakeGateway"""
from dataclasses import dataclass, field


class GatewayTimeout(Exception):
    """gateway ไม่ตอบภายใน GATEWAY_TIMEOUT_SECONDS (UC-07 E1, REQ-IF-005)"""


@dataclass
class GatewayResult:
    status: str   # approved / declined / unknown
    ref: str


class Gateway:
    def authorize(self, ref: str, amount: int, timeout_seconds: int) -> GatewayResult:  # กันวงเงิน รอไม่เกิน timeout
        raise NotImplementedError

    def capture(self, ref: str) -> GatewayResult:  # ตัดเงินจริง
        raise NotImplementedError

    def void(self, ref: str) -> GatewayResult:  # ยกเลิกการกันวงเงิน (BR-01 R5)
        raise NotImplementedError

    def status_inquiry(self, ref: str) -> GatewayResult:  # REQ-IF-005
        raise NotImplementedError


@dataclass
class FakeGateway(Gateway):
    """สั่งพฤติกรรมได้: mode = approved | declined | timeout
    inquiry_answer = คำตอบของ status-inquiry เมื่อ timeout (approved / declined / unknown)"""
    mode: str = "approved"
    inquiry_answer: str = "unknown"
    calls: list[str] = field(default_factory=list)
    last_timeout_seconds: int | None = None

    def authorize(self, ref, amount, timeout_seconds):
        self.calls.append(f"authorize:{ref}")
        self.last_timeout_seconds = timeout_seconds
        if self.mode == "timeout":
            raise GatewayTimeout(ref)
        return GatewayResult(self.mode, ref)

    def capture(self, ref):
        self.calls.append(f"capture:{ref}")
        return GatewayResult("approved", ref)

    def void(self, ref):
        self.calls.append(f"void:{ref}")
        return GatewayResult("voided", ref)

    def status_inquiry(self, ref):
        self.calls.append(f"inquiry:{ref}")
        return GatewayResult(self.inquiry_answer, ref)


# gateway ที่ระบบใช้จริง ตั้งค่าใน main.py; test สลับเป็น FakeGateway ผ่าน dependency
_current: Gateway = FakeGateway()


def get_gateway() -> Gateway:
    return _current


def set_gateway(g: Gateway) -> None:
    global _current
    _current = g
