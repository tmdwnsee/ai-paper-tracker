# AI Paper Tracker

arXiv에서 **RAG, LLM, AI Agent** 관련 신규 논문을 수집하고, 중복 제거·키워드 분류·**PDF 본문 전체를 바탕으로 한 한국어 요약** 후 GitHub에 리포트를 자동 반영하는 프로젝트입니다.

## 작동 방식

`arXiv API → 신규 논문 식별 → PDF 다운로드 → 페이지별 텍스트 추출 → 구간별 한국어 메모 → 종합 한국어 요약 → JSON / Markdown → GitHub Actions 커밋`

- **자동 실행**: 매일 **오전 9시, Asia/Seoul** (GitHub Actions 예약 실행)
- **신규 논문이 없으면 파일을 수정하지 않습니다.** 의미 없는 커밋을 만들지 않습니다.
- **중복 기준**: arXiv 논문 ID (버전 번호 제외)
- **본문 요약**: `GEMINI_API_KEY`가 있어야 PDF 본문을 구간별로 분석하고 한국어로 요약합니다. 키가 없으면 신규 논문만 수집하고 요약은 대기 상태로 둡니다. 기존 초록 발췌 기록도 요약 대상으로 다시 처리합니다.
- **상태 보관**: `data/papers.json`에 기존 논문 기록, `reports/LATEST.md`에 가장 최근 수집 결과
- 최초 실행에는 최근 `LOOKBACK_DAYS`일 이내 논문을 신규로 간주합니다.

## 실행 방법

Python **3.11+**가 필요합니다. PDF 파싱에 PyMuPDF를 사용합니다.

```bash
python -m pip install -r requirements.txt
python -m src.tracker
python -m unittest discover -s tests -v
```

환경변수:

| 변수 | 기본값 | 용도 |
| --- | --- | --- |
| `LOOKBACK_DAYS` | `7` | 검색 대상 발행일 범위 |
| `MAX_RESULTS` | `150` | API에서 가져올 논문 최대 수 |
| `MAX_NEW_PER_RUN` | `1` | 실행당 저장할 신규 논문 최대 수 |
| `GEMINI_API_KEY` | 없음 | 있으면 LLM 요약 활성화 |
| `GEMINI_MODEL` | `gemini-2.5-flash-lite` | 요약 모델 |
| `MAX_FULLTEXT_PER_RUN` | `1` | 매 실행당 PDF 본문 한국어 요약 최대 건수 (무료 할당량 관리) |
| `MAX_PAPER_CHUNKS` | `12` | 논문당 최대 분석 구간 수 |
| `ARXIV_USER_AGENT` | `AIPaperTracker/1.0 (research metadata collection)` | API 요청 식별 |

## GitHub 저장소 설정

1. **Public** 저장소 `ai-paper-tracker` 생성 후 이 프로젝트의 **내용물**을 기본 브랜치(`main`)에 업로드합니다.
2. GitHub 저장소의 **Settings → Actions → General → Workflow permissions**에서 `Read and write permissions` 허용 여부를 확인합니다. 워크플로에 `contents: write`도 선언되어 있습니다.
3. 선택: **Settings → Secrets and variables → Actions → New repository secret**에서 `GEMINI_API_KEY`를 추가합니다. Google AI Studio 무료 등급에서 사용할 키를 등록하세요. 무료 할당량을 넘기면 요약은 중단됩니다. 유료 결제를 활성화하면 요금이 발생할 수 있습니다. 비밀키를 파일에 넣거나 커밋하지 마세요.
4. **Actions → Daily AI Paper Tracker → Run workflow**로 수동 실행 후 결과 확인.
5. 이후 `Asia/Seoul` 오전 9시에 예약 실행됩니다. GitHub 예약 작업은 지연·누락될 수 있으며, 장기간 활동이 없는 공개 저장소에서는 비활성화될 수 있습니다.

### GitHub 잔디 관련

기본 설정의 `github-actions[bot]` 커밋은 **사용자 개인 기여 잔디를 보장하지 않습니다**. 자동화된 데이터 갱신과 본인이 직접 구현한 개발 활동은 구분하는 것이 좋습니다. 필요 시 커밋 작성자 및 기여 집계 조건을 GitHub 공식 문서에서 확인하세요.

## 파일 구성

```text
.github/workflows/daily.yml  # 예약 실행, 테스트, 자동 커밋
src/tracker.py               # arXiv 수집, 분석, 저장
src/fulltext.py              # PDF 본문 추출 및 한국어 단계별 요약
requirements.txt             # PDF 추출 의존성
tests/test_tracker.py        # 파서·중복 처리 테스트
data/papers.json             # 수집된 논문
reports/LATEST.md            # 최근 업데이트
reports/YYYY-MM-DD.md        # 신규 논문이 있던 날의 리포트
```

## 설계상 한계

- arXiv 제출일 및 검색 정렬에 따른 후보 목록을 수집하므로 arXiv의 모든 관련 논문을 완전하게 수집한다고 보장하지 않습니다.
- 키워드 기반 관련도 점수는 학술적 중요도나 논문의 품질을 나타내지 않습니다.
- PDF의 텍스트를 모든 페이지에서 추출해 구간별로 분석하지만, 수식·표·이미지·스캔 PDF의 정확한 해석은 보장되지 않습니다.
- PDF 추출 실패·구간 수 제한 초과·API 오류 시 **본문 요약 성공으로 표시하지 않습니다**.
- 생성된 요약은 LLM 결과로 별도 사실 검증이 필요합니다.
- 기본 설정은 요약 최대 1건/실행이며, 논문 길이에 따라 무료 할당량을 초과할 수 있습니다. GitHub Actions 수동 실행을 반복하면 하루 제한을 초과할 수 있습니다.
- 수집된 제목과 초록은 원문 출처에 귀속됩니다. 상세 내용은 각 arXiv 링크에서 확인하세요.

## 참고

- [arXiv API 매뉴얼](https://info.arxiv.org/help/api/user-manual.html)
- [GitHub Actions schedule 문서](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)

## 무료 Gemini API 키

1. [Google AI Studio](https://aistudio.google.com/app/apikey)에서 키를 생성합니다. 무료 할당량 및 모델 가용성은 계정과 국가에 따라 다릅니다.
2. 저장소 **Settings → Secrets and variables → Actions**에 이름 `GEMINI_API_KEY`로 키를 등록합니다.
3. 기존 `OPENAI_API_KEY`는 이 워크플로에서 사용하지 않습니다. 필요 없으면 GitHub Secrets에서 직접 삭제할 수 있습니다.
4. Actions에서 수동 실행한 뒤 `reports/LATEST.md`와 로그의 `Full-text Korean summary:` 문구를 확인합니다.

무료 등급 이용 시 콘텐츠가 제공업체의 제품 개선에 사용될 수 있으므로 공개 arXiv 논문만 처리하세요. 무료 할당량을 초과하면 자동으로 유료 모델로 전환하지 않습니다.
