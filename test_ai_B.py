import pytest

from test_ai_A import load_scores


def create_scores_file(tmp_path, content):
    path = tmp_path / "scores.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_missing_file_propagates_file_not_found_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "not-found.csv")


def test_first_line_is_header_and_invalid_column_count_is_reported(tmp_path):
    path = create_scores_file(tmp_path, "이름,점수\n김철수,90,추가정보\n")

    kept, skipped = load_scores(path)

    assert kept == []
    assert skipped == [(2, "김철수,90,추가정보", "열 개수가 2가 아님")]


def test_scores_outside_zero_to_hundred_are_skipped(tmp_path):
    path = create_scores_file(tmp_path, "이름,점수\n음수,-1\n초과,101\n")

    kept, skipped = load_scores(path)

    assert kept == []
    assert skipped == [
        (2, "음수,-1", "점수가 0~100 밖"),
        (3, "초과,101", "점수가 0~100 밖"),
    ]


def test_missing_name_or_score_is_reported(tmp_path):
    path = create_scores_file(tmp_path, "이름,점수\n,80\n이름,\n")

    kept, skipped = load_scores(path)

    assert kept == []
    assert skipped == [
        (2, ",80", "이름이 비어 있음"),
        (3, "이름,", "점수가 비어 있음"),
    ]


def test_duplicate_names_are_kept_without_removal(tmp_path):
    path = create_scores_file(tmp_path, "이름,점수\n동명이인,70\n동명이인,80\n")

    kept, skipped = load_scores(path)

    assert kept == [("동명이인", 70), ("동명이인", 80)]
    assert skipped == []


def test_report_contains_valid_rows_and_skipped_row_details(tmp_path):
    path = create_scores_file(tmp_path, "이름,점수\n유효한사람,100\n잘못된사람,101\n")

    kept, skipped = load_scores(path)

    assert kept == [("유효한사람", 100)]
    assert skipped == [(3, "잘못된사람,101", "점수가 0~100 밖")]