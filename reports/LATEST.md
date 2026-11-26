# AI Paper Digest — 2026-11-26

- 한국어 PDF 본문 요약 완료: **1편**
- arXiv candidates retrieved: **150**
- Scores represent **keyword relevance only**, not research quality.
- 완료된 한국어 PDF 본문 요약만 표시합니다. 실패·미완료 결과는 저장하지 않습니다.

## 1. TASK Memory: Beyond Text-Only Memory with Activation Steering and Knowledge Editing against Memory Hallucination

- arXiv: https://arxiv.org/abs/2611.34762
- Published (UTC): 2026-11-25T17:30:37Z
- Topics: RAG, LLM
- Keyword relevance: 30/100
- Authors: Jinkun Zhao, Wenjun Wu
- Summary source: fulltext_llm_ko
- PDF pages: 22

제공된 논문 본문 메모리를
 바탕으로 작성한 구체적인 Markdown 요약입니다. 모든 내용은 제공된 메모리에 근거하며, 본문에 확인되지 않은 내용은 기재하지 않았습니다.

---

## 연구 목적
* LLM 에이전트가 외부 메모리에 점점 더 의존하고 있음에도 불구하고, 검색된 올바른 메모리가 프롬프트에 들어가더라도 모델의 파라미터(가중치)에 내재된 지식과의 충돌로 인해 **사용 시점 메모리 환각(use-time memory hallucinations)**이 발생하는 원인을 규명하고 이를 해결하는 것 [p.1, p.2].
* 5개 오픈 모델(Qwen3-8B/14B, Llama-3.1-8B, Phi-4, Gemma-3-27B)에서 나타나는 세 가지 환각 유형을 분석하고, 텍스트 전용 메모리의 한계를 극복하는 새로운 아키텍처를 제안함 [p.1, p.2, p.3].

## 핵심 아이디어 및 방법
* **TASK Memory 아키텍처:** 텍스트 단독 메모리를 넘어 세 가지 요소를 하나의 모델 내 주소(in-model address)로 공유하여 결합함 [p.1, p.2, p.3]:
  1. **Text note ($T$):** 콘텐츠를 보유하며 버전 관리되는 노트 [p.1, p.2, p.3].
  2. **Knowledge edit ($E$, $\Delta W_m$):** 주제 키를 통해 주소를 제공하고 다중 홉(multi-hop) 구성을 지원하는 지역적이며 제거 가능한(removable) 지식 편집 (ROME 스타일의 닫힌형태 저랭크 패치) [p.1, p.2, p.3, p.6, p.7].
  3. **Activation-Steering vectors ($S$, $v^+, v^-$):** 모델이 메모리를 채택할지($v^+$) 혹은 파라메트릭 답변을 유지할지($v^-$) 결정하는 한 쌍의 활성화 조향 벡터 [p.1, p.2, p.3].
* **읽기 규칙 및 3개의 게이트:** BM25 또는 의미 검색 후보에 대해 부분 순방향 패스와 게이트($g_m$)를 계산하여 텍스트 표시, 패치 로드, 조향 벡터 추가 여부를 제어함 [p.6, p.7].
* **자동 세대 교체 (Automatic Supersession):** 팩트 ID를 사용하지 않고 주소와 에이전트의 판단기를 결합하여, 새로운 UPDATE 발생 시 구버전의 $T, E, S$를 함께 은퇴(retire)시킴 [p.6, p.7, p.11].

## 실험 및 주요 결과
* **데이터셋:** CounterFact, zsRE, MQuAKE (예: MQuAKE-CF-3k), LoCoMo, LongMemEval, AppWorld [p.1, p.3, p.8, p.9, p.12, p.20, p.21].
* **환각 감소 효과:** 
  * `T + S`는 베이스라인 `T` 대비 CounterFact(300개)에서 Composite 기준 **+10.80** 향상(0.811 대비 0.919)을 기록함 [p.9].
  * $T$에서 $T+S$로 이동할 때 오래된 사실(stale fact)로의 회귀가 통계적으로 유의미하게 감소함 (예: CF Llama-3.1-8B에서 **-46.3 pp**) [p.18].
* **규모 확장 및 조합 성능:** 주소 검증과 게이트가 적용된 전체 구성(`Addr. T + gated E + S`)은 3,000개의 메모리 라이브러리 규모에서 99.0%의 현재 값 정확도를 달성함 [p.11].
* **자유 형식 대화 메모리 (LoCoMo):** Semantic-address 기반 `T + S` (TASK)가 Qwen3-8B judge 기준 **34.2**, Qwen3-14B judge 기준 **31.0**, GLM-5.3 judge 기준 **39.3**의 정확도를 기록하며 300토큰 이하 방법 중 가장 우수한 성능을 보임 [p.13].
* **구버전 갱신 효과:** 구버전을 갱신하지 않는 것보다 Qwen3-8B에서 **48.7 pp**, Llama-3.1-8B에서 **54.7 pp** 향상됨 [p.11].

## 한계 및 주의점
* **동일 주체 라이브러리(Same-subject library, H1) 문제:** 동일한 주체를 공유하는 여러 관계가 하나의 라이브러리를 사용할 때, 주소 전용 대체(address-only supersession)가 동일 주체 라이브러리 내 메모리의 **47%**를 잘못 은퇴(retire)시키는 문제가 발생함 [p.20].
* **브리지 엔티티 부재 시 제약:** 브리지 엔티티가 질문에 포함되어 있지 않을 때 쌍으로 이루어진 패치 방식($v^-$ 등)이 오히려 방해가 될 수 있어, 다중 홉 구성에서는 `$v^+$-only` 읽기 규칙을 별도로 적용해야 함 [p.11].
* 본문에 명시되지 않은 하드웨어 리소스 소모량이나 학습 시간 등의 상세 자원 소모 지표는 본문에서 확인되지 않음.

## AI 엔지니어 관점에서 볼 점
* **파라미터-메모리 충돌 해결의 새로운 패러다임:** 단순 RAG(텍스트 메모리) 방식만으로는 LLM 가중치에 박힌 기존 지식(stale fact)을 이기지 못해 발생하는 '유형 I·II·III 환각'을, 텍스트 검색에 국소적 가중치 편집($E$)과 활성화 조향($S$)을 결합함으로써 효과적으로 제어할 수 있음을 입증함 [p.1, p.2, p.3].
* **모듈형 아키텍처 및 런타임 제어:** 에이전트 시스템 구현 시, 단일 훅과 부분 순방향 패스를 통해 동결된(frozen) 대형 모델을 재학습 없이 런타임에 제어할 수 있는 실용적인 구조를 제공함 [p.13].
* **버전 관리 자동화의 필요성:** 다중 팩트/다중 버전 환경에서 팩트 ID 의존 없이 주소와 에이전트 판단을 결합한 자동 은퇴(supersession) 로직이 버전 혼동 환각 방지에 핵심적인 역할을 하므로, 메모리 라이브러리 설계 시 반영해야 함 [p.6, p.7, p.11].

> **한문장 핵심 정리:** TASK Memory는 텍스트 메모리에 지식 편집과 활성화 조향 벡터를 결합하여 사용 시점의 메모리 환각을 방지하고 다중 홉 구성을 지원하는 인모델 메모리 제어 프레임워크입니다 [p.1, p.2, p.3].
