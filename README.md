# AI Paper Tracker

arXiv에서 **RAG, LLM, AI Agent** 관련 신규 논문을 수집하고, 중복 제거·키워드 분류·요약 후 GitHub에 리포트를 자동 반영하는 프로젝트입니다.

## 작동 방식

`arXiv API → Atom XML 파싱 → 관련도 분류 → 신규 논문 식별 → (선택) LLM 요약 → JSON / Markdown → GitHub Actions 커밋`

- **자동 실행**: 매일 **오전 9시, Asia/Seoul** (GitHub Actions 예약 실행)
- **신규 논문이 없으면 파일을 수정하지 않습니다.** 의미 없는 커밋을 만들지 않습니다.
- **중복 기준**: arXiv 논문 ID (버전 번호 제외)
- **LLM 요약은 선택**: `OPENAI_API_KEY`가 없으면 초록 기반 발췌 요약으로 동작
- **상태 보관**: `data/papers.json`에 기존 논문 기록, `reports/LATEST.md`에 가장 최근 수집 결과
- 최초 실행에는 최근 `LOOKBACK_DAYS`일 이내 논문을 신규로 간주합니다.

## 실행 방법

Python **3.11+**가 필요합니다. 외부 Python 패키지 없이 실행됩니다.

```bash
python -m src.tracker
python -m unittest discover -s tests -v
```

환경변수:

| 변수 | 기본값 | 용도 |
| --- | --- | --- |
| `LOOKBACK_DAYS` | `7` | 검색 대상 발행일 범위 |
| `MAX_RESULTS` | `150` | API에서 가져올 논문 최대 수 |
| `MAX_NEW_PER_RUN` | `15` | 실행당 저장할 신규 논문 최대 수 |
| `OPENAI_API_KEY` | 없음 | 있으면 LLM 요약 활성화 |
| `OPENAI_MODEL` | `gpt-4o-mini` | 요약 모델 |
| `ARXIV_USER_AGENT` | `AIPaperTracker/1.0 (research metadata collection)` | API 요청 식별 |

## GitHub 저장소 설정

1. **Public** 저장소 `ai-paper-tracker` 생성 후 이 프로젝트의 **내용물**을 기본 브랜치(`main`)에 업로드합니다.
2. GitHub 저장소의 **Settings → Actions → General → Workflow permissions**에서 `Read and write permissions` 허용 여부를 확인합니다. 워크플로에 `contents: write`도 선언되어 있습니다.
3. 선택: **Settings → Secrets and variables → Actions → New repository secret**에서 `OPENAI_API_KEY`를 추가합니다. API 사용량은 과금될 수 있습니다. 비밀키를 파일에 넣거나 커밋하지 마세요.
4. **Actions → Daily AI Paper Tracker → Run workflow**로 수동 실행 후 결과 확인.
5. 이후 `Asia/Seoul` 오전 9시에 예약 실행됩니다. GitHub 예약 작업은 지연·누락될 수 있으며, 장기간 활동이 없는 공개 저장소에서는 비활성화될 수 있습니다.

### GitHub 잔디 관련

기본 설정의 `github-actions[bot]` 커밋은 **사용자 개인 기여 잔디를 보장하지 않습니다**. 자동화된 데이터 갱신과 본인이 직접 구현한 개발 활동은 구분하는 것이 좋습니다. 필요 시 커밋 작성자 및 기여 집계 조건을 GitHub 공식 문서에서 확인하세요.

## 파일 구성

```text
.github/workflows/daily.yml  # 예약 실행, 테스트, 자동 커밋
src/tracker.py               # arXiv 수집, 분석, 저장
tests/test_tracker.py        # 파서·중복 처리 테스트
data/papers.json             # 수집된 논문
reports/LATEST.md            # 최근 업데이트
reports/YYYY-MM-DD.md        # 신규 논문이 있던 날의 리포트
```

## 설계상 한계

- arXiv 제출일 및 검색 정렬에 따른 후보 목록을 수집하므로 arXiv의 모든 관련 논문을 완전하게 수집한다고 보장하지 않습니다.
- 키워드 기반 관련도 점수는 학술적 중요도나 논문의 품질을 나타내지 않습니다.
- LLM 요약은 초록만 사용하며, 원문 전체를 읽고 검증한 결과가 아닙니다.
- 수집된 제목과 초록은 원문 출처에 귀속됩니다. 상세 내용은 각 arXiv 링크에서 확인하세요.

## 참고

- [arXiv API 매뉴얼](https://info.arxiv.org/help/api/user-manual.html)
- [GitHub Actions schedule 문서](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
