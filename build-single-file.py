"""전달용 단일 HTML 파일을 만든다.

index.html 의 `img/*.png` 참조를 base64 data URI 로 바꿔 한 파일에 넣는다.
파일 하나라서 카톡·메일로 그대로 보낼 수 있고, 인터넷 없이 열어도 이미지가 나온다
(웹폰트만 시스템 폰트로 대체된다).

    쓰는 법:  python build-single-file.py

산출물 `고보성_포트폴리오_단일파일.html` 은 .gitignore 로 저장소에서 제외한다 —
같은 이미지가 두 벌이 되기 때문이다. 저장소의 배포 대상은 index.html 하나다.

🔴 index.html 이나 img/ 를 고치면 이 스크립트를 다시 돌려야 한다.
   안 그러면 전달한 파일만 옛날 내용으로 남는다.

이미지 참조가 하나라도 남으면 파일을 쓰지 않고 실패한다 —
조용히 깨진 파일을 만들어 보내는 것이 가장 나쁘다.
"""

import base64
import pathlib
import re
import sys

SITE = pathlib.Path(__file__).resolve().parent
SRC = SITE / "index.html"
DST = SITE / "고보성_포트폴리오_단일파일.html"

IMG_REF = re.compile(r'src="(img/[^"]+)"')

MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}


def main() -> int:
    if not SRC.exists():
        print(f"FAIL — {SRC.name} 이 없다")
        return 1

    html = SRC.read_text(encoding="utf-8")
    inlined: list[str] = []
    missing: list[str] = []

    def to_data_uri(m: re.Match) -> str:
        rel = m.group(1)
        path = SITE / rel
        mime = MIME.get(path.suffix.lower())
        if not path.exists() or mime is None:
            missing.append(rel)
            return m.group(0)
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        inlined.append(rel)
        return f'src="data:{mime};base64,{b64}"'

    out = IMG_REF.sub(to_data_uri, html)

    left = IMG_REF.findall(out)
    if missing or left:
        print("FAIL — 치환하지 못한 이미지가 있다:")
        for rel in sorted(set(missing + left)):
            print("   ", rel)
        return 1

    DST.write_text(out, encoding="utf-8")
    print(f"OK  이미지 {len(inlined)}장 내장  →  {DST.name}  ({DST.stat().st_size / 1024 / 1024:.2f}MB)")

    unused = sorted(p.name for p in (SITE / "img").iterdir()
                    if p.suffix.lower() in MIME and f"img/{p.name}" not in inlined)
    if unused:
        print(f"⚠️  index.html 이 안 쓰는 이미지 {len(unused)}장: {', '.join(unused)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
