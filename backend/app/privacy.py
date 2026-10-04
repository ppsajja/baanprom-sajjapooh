"""REQ-PRV-002 เบอร์โทรลูกค้าห้ามปรากฏใน log ของระบบ
ทุกโมดูลต้องขอ logger จากที่นี่ ตัวกรองจะแทนเบอร์โทรที่หลุดมาด้วย [phone]"""
import logging
import re

PHONE_PATTERN = re.compile(r"0\d{1,2}[- ]?\d{3}[- ]?\d{4}")


class PhoneFilter(logging.Filter):
    # รองรับ REQ-PRV-002: กรองข้อความ log ก่อนเขียน
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = PHONE_PATTERN.sub("[phone]", str(record.msg))
        if isinstance(record.args, dict):
            # logging เก็บ arg เดี่ยวที่เป็น dict ไว้ทั้งก้อน ให้แปลงเป็นข้อความแล้วกรอง
            record.args = (PHONE_PATTERN.sub("[phone]", str(record.args)),)
        elif record.args:
            record.args = tuple(PHONE_PATTERN.sub("[phone]", str(a)) for a in record.args)
        return True


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not any(isinstance(f, PhoneFilter) for f in logger.filters):
        logger.addFilter(PhoneFilter())
    return logger
