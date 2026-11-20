# load_scores.py
# ---------------------------------------------------------------------------
# 10주차 실습에서 만든 v5(재검토판)를 정리한 것입니다.
# 11주차에는 이 함수를 "시험하는" 코드를 여러분이 직접 만듭니다.
#
# 명세 (10주차 명세서 6칸 요약)
#   load_scores(path) -> (kept, skipped)
#     kept    : [(이름, 점수), ...]      점수는 0~100 사이의 정수
#     skipped : [(줄번호, 원본줄, 이유), ...]   건너뛴 줄의 기록
#
#   ① 파일이 없으면        → FileNotFoundError 를 그대로 올립니다 (숨기지 않습니다)
#   ② 헤더만 있으면        → ([], []) 를 돌려줍니다
#   ③ 열 개수가 2가 아니면 → 건너뛰고 기록합니다
#   ④ 점수가 비었거나 정수가 아니면 → 건너뛰고 기록합니다
#   ⑤ 점수가 0~100 밖이면  → 건너뛰고 기록합니다
#   ⑥ 이름이 비었으면      → 건너뛰고 기록합니다
#
#   ★ 같은 이름이 두 번 나오는 경우 (v5 재검토에서 바꾼 부분)
#     이 함수는 지우지 않고 둘 다 남깁니다.
#     이름이 같다고 같은 사람이라는 보장이 없기 때문입니다(동명이인).
#     누구를 남길지는 이 함수가 아니라 쓰는 쪽에서 정할 일입니다.
#
#   빈 줄은 기록 없이 그냥 건너뜁니다.
# ---------------------------------------------------------------------------

import csv

import pytest

MIN_SCORE = 0
MAX_SCORE = 100


def load_scores(path):
    """성적 CSV를 읽어 (유효한 목록, 건너뛴 줄 기록) 을 돌려준다."""
    kept = []
    skipped = []

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for line_no, row in enumerate(reader, start=1):
            if line_no == 1:              # 헤더
                continue
            if not row:                   # 빈 줄 — 기록하지 않는다
                continue

            원본 = ",".join(row)

            if len(row) != 2:
                skipped.append((line_no, 원본, "열 개수가 2가 아님"))
                continue

            name = row[0].strip()
            raw = row[1].strip()

            if name == "":
                skipped.append((line_no, 원본, "이름이 비어 있음"))
                continue
            if raw == "":
                skipped.append((line_no, 원본, "점수가 비어 있음"))
                continue

            try:
                score = int(raw)
            except ValueError:
                skipped.append((line_no, 원본, "점수가 정수가 아님"))
                continue

            if score < MIN_SCORE or score > MAX_SCORE:
                skipped.append((line_no, 원본, "점수가 0~100 밖"))
                continue

            kept.append((name, score))

    return kept, skipped


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "scores.csv"
    kept, skipped = load_scores(path)
    print(f"읽은 줄 : {len(kept)}개")
    for name, score in kept:
        print(f"  {name} {score}")
    print(f"건너뛴 줄 : {len(skipped)}개")
    for line_no, 원본, 이유 in skipped:
        print(f"  {line_no}행  {원본}   ← {이유}")


def write_scores_file(tmp_path, content):
    path = tmp_path / "scores.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_scores_keeps_valid_rows_and_duplicate_names(tmp_path):
    path = write_scores_file(
        tmp_path,
        "이름,점수\n홍길동,85\n김철수,92\n홍길동,90\n",
    )

    kept, skipped = load_scores(path)

    assert kept == [("홍길동", 85), ("김철수", 92), ("홍길동", 90)]
    assert skipped == []


def test_load_scores_accepts_boundary_scores(tmp_path):
    path = write_scores_file(tmp_path, "이름,점수\n최저점,0\n최고점,100\n")

    kept, skipped = load_scores(path)

    assert kept == [("최저점", 0), ("최고점", 100)]
    assert skipped == []


def test_load_scores_skips_invalid_rows_with_reasons(tmp_path):
    path = write_scores_file(
        tmp_path,
        "이름,점수\n"
        "열이,세 개,있음\n"
        "빈점수,\n"
        "문자점수,점수\n"
        "낮은점수,-1\n"
        "높은점수,101\n"
        ",80\n",
    )

    kept, skipped = load_scores(path)

    assert kept == []
    assert skipped == [
        (2, "열이,세 개,있음", "열 개수가 2가 아님"),
        (3, "빈점수,", "점수가 비어 있음"),
        (4, "문자점수,점수", "점수가 정수가 아님"),
        (5, "낮은점수,-1", "점수가 0~100 밖"),
        (6, "높은점수,101", "점수가 0~100 밖"),
        (7, ",80", "이름이 비어 있음"),
    ]


def test_load_scores_skips_empty_lines_without_recording(tmp_path):
    path = write_scores_file(tmp_path, "이름,점수\n\n유효한이름,70\n")

    kept, skipped = load_scores(path)

    assert kept == [("유효한이름", 70)]
    assert skipped == []


def test_load_scores_returns_empty_lists_for_header_only(tmp_path):
    path = write_scores_file(tmp_path, "이름,점수\n")

    assert load_scores(path) == ([], [])


def test_load_scores_raises_file_not_found_for_missing_file(tmp_path):
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(missing_path)
