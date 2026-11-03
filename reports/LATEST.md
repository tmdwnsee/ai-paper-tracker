# AI Paper Digest — 2026-11-03

- Newly archived papers: **23**
- arXiv candidates retrieved: **150**
- Scores represent **keyword relevance only**, not research quality.
- PDF-based summaries are labelled fulltext_llm_ko; other records are pending or legacy excerpts.

## 1. Pixel-UMI: Learning Environment-Aware Whole-Body Manipulation from Sensorized Human Demonstrations

- arXiv: https://arxiv.org/abs/2611.03647
- Published (UTC): 2026-11-02T18:59:32Z
- Topics: RAG
- Keyword relevance: 15/100
- Authors: Jason Jingzhou Liu, Tony Tao, Deepak Pathak, Ruslan Salakhutdinov
- Summary source: fulltext_llm_ko
- PDF pages: 15

제공된 논문 텍스트 내용을 바탕으로 작성한 구체적인 Markdown 요약입니다.

---

## 연구 목적
* 모바일 매니퓰레이션(mobile manipulation)에서 널리 쓰이는 센서화된 인간 시연 데이터 수집 방법은 운전자가 많은 자유도를 조율해야 하고 환경마다 로봇을 배치해야 하는 어려움이 있음 [p.1].
* 인간과 로봇 간의 운동학적/신체적 차이(kinematic differences)로 인해 잔여 포즈 오차가 발생하며, 이로 인해 인간 시연과 로봇 관측 사이에 시점 불일치(viewpoint mismatch)가 발생함 [p.1, p.2].
* 힘/촉각 센서가 없는 센서화된 인간 데이터 수집은 상호작용 힘을 기록하지 못하므로, 상태 기반 UMI 감독만으로는 접촉이 많은(contact-rich) 조작 작업을 수행하기 어려움 [p.2].

## 핵심 아이디어 및 방법
* **Pixel-UMI 파이프라인**: 센서화된 인간 시연으로부터 환경 인식형(environment-aware) 전신 정책을 학습하는 파이프라인 [p.1].
* **EAR (Environment-Aware Retargeting)**: 
  * 에피소드의 깊이 시퀀스로부터 정적 장면 기하학 구조를 재구성하고, 동적 객체를 분리함 [p.2].
  * 환경 인식형 기하학적 패브릭을 사용하여 시연된 동작을 오프라인에서 재타겟팅함으로써 본체 관절 경로 및 베이스 명령을 생성하고 충돌을 회피하도록 로봇 자세를 해결함 [p.2].
  * 실제 로봇의 응답 지연을 보정하기 위해 캘리브레이션된 관절 추적 지연을 사용해 슈도 액션(pseudo-action)을 할당함 [p.3, p.5].
* **REAM (Retargeting-Error-Aware Masking)**: 
  * 재타겟팅 포즈 오차를 백분위수 기반의 시각적 불일치 기하학적 대용물로 사용하여 카메라 마스킹에 활용함 [p.2, p.6].
  * 오차가 더 높은 뷰는 훈련 중 토큰이 제외될 가능성을 높여, 로봇이 정확히 재현하기 어려운 카메라 뷰에 대한 의존도를 줄임 [p.1, p.2].
* **온정책 교정 (On-Policy Correction via DAgger)**: 
  * 접촉이 많은 작업에서의 성능을 향상시키기 위해 DAgger를 통한 온정책 인간 교정 데이터를 수집함 [p.1, p.2].
  * 정책은 사전 학습된 DINOv3 ViT-B/16 시각적 백본과 플로우 매칭 액션 디코더를 사용함 [p.7].

## 실험 및 주요 결과
* 총 5가지 도전적인 모바일 매니퓰레이션 과제(Arrange Mouse, Pack Tennis Canister, Fold Box, Hang Jacket, Retrieve Drink 등)를 대상으로 평가함 [p.1, p.3, p.7, p.11].
* 5개 작업에서 평균 **87.0%**의 평균 작업 진척도(average task progress)를 달성함 [p.13].
* 접촉이 많은 작업의 경우, 온폴리시 보정(DAgger)을 두 차례 거치면서 평균 작업 진척도가 **6.82%에서 79.77%**로 크게 증가함 [p.13].
* 손목 전용 조건은 *Arrange Mouse*에서 20%의 태스크 진행률을 기록한 반면, 모든 카메라를 사용하는 EAR 전용은 82.5%를 기록함 [p.11]. 보정(calibration)은 평균 태스크 진행률을 24.05% 포인트 증가시킴 [p.11].

## 한계 및 주의점
* **지연 보정된 행동 할당의 한계**: 대략적인 명령어 레이블은 제공하지만 시연된 동작의 기저에 있는 접촉 의존적 행동(contact-dependent actions)을 복원할 수 없음 [p.13].
* **재대상화 품질의 한계**: 단일 헤드 장착 깊이 카메라를 사용한 재구성은 가려지거나 관측되지 않은 표면을 불완전하게 남기며, 정적 장면 공식화는 움직이는 장애물을 처리하는 데 한계를 둠 [p.13].

## AI 엔지니어 관점에서 볼 점
* 인간 시연과 로봇의 물리적 차이(운동학적 격차 및 시점 불일치)가 모방 학습의 전이 성능을 떨어뜨릴 수 있으므로, EAR(환경 인지 리타겟팅)과 REAM(오차 인지 마스킹) 같은 기하학적 후처리 및 가시성 제어 기법이 실물 로봇 배포 시 매우 유효하다는 점을 보여줌 [p.1, p.2, p.3].
* 순수 시연 데이터 학습의 한계(접촉 중심 작업의 정체)를 극복하기 위해 DAgger 기반의 온정책 보정(on-policy correction)을 결합하는 파이프라인 설계가 복잡한 조작 작업 성공률 향상에 핵심적임을 시사함 [p.1, p.6, p.13].

---
*핵심 정리:* Pixel-UMI는 센서화된 인간 시연의 환경 인식형 리타겟팅, 오차 인지 카메라 마스킹, 그리고 온정책 보정(DAgger)을 결합하여 인간-로봇 간의 신체 및 시점 격차를 극복하고 고도화된 전신 모바일 조작 정책을 학습하는 파이프라인이다 [p.1, p.2].

## 2. From Natural Language to Exact Cover: A Neuro-Symbolic Approach to Zebra Puzzles

- arXiv: https://arxiv.org/abs/2611.03641
- Published (UTC): 2026-11-02T18:58:21Z
- Topics: LLM
- Keyword relevance: 30/100
- Authors: Paulius Skaisgiris, Thomas Pammer, Veronika Semmelrock, Mykyta Ielanskyi, Maximilian Heisinger, Erich Kobler
- Summary source: abstract excerpt
- PDF pages: not processed

Chain-of-Thought (CoT) generation has substantially improved the performance of Large Language Models (LLMs) on complex reasoning tasks, including code generation, data analysis, and exam-style question answering. Despite these advances, purely neural LLMs continue to struggle with elementary logical reasoning problems and lack the determinism, sou…

## 3. WebHarbor: Docking Real Websites for Evolving GUI Agent Environments

- arXiv: https://arxiv.org/abs/2611.03634
- Published (UTC): 2026-11-02T18:57:36Z
- Topics: RAG
- Keyword relevance: 15/100
- Authors: Zhaoyang Wang, Qianhui Wu, Boyu Gou, Demi Wang, Jiacheng Zhang, Peichun Hua, Qize Li, Shi Qiu
- Summary source: abstract excerpt
- PDF pages: not processed

GUI web agents require realistic and interactive environments that remain stable during both evaluation and training. Live website evaluation suffers from changing content, access restrictions, and limited coverage of authenticated workflows, while existing synthetic environments for training often lack functional depth and visual fidelity. We prop…

## 4. Strategist: Evolving Reasoning with Agents

- arXiv: https://arxiv.org/abs/2611.03618
- Published (UTC): 2026-11-02T18:51:04Z
- Topics: RAG, LLM, Agent
- Keyword relevance: 30/100
- Authors: Taiming Lu, Qi Xu, Zhigang Hua, Zhuang Liu
- Summary source: abstract excerpt
- PDF pages: not processed

A model is only half of an AI agent system. The other half is the inference strategy: the reasoning procedure that turns model calls into a response. Today that second half is written by hand, and the experience of building one strategy never carries to the next. We introduce Strategist, a meta-agent that evolves inference strategies across tasks.…

## 5. Tracing the Scientific Discovery Capacity of LLMs to Their Training Data

- arXiv: https://arxiv.org/abs/2611.03617
- Published (UTC): 2026-11-02T18:50:54Z
- Topics: LLM
- Keyword relevance: 40/100
- Authors: Arda Uzunoglu, Mahler Revsine, Michael Schatz, Benjamin Van Durme, Mehrdad Farajtabar, Daniel Khashabi, Eric Nalisnick
- Summary source: abstract excerpt
- PDF pages: not processed

Large language models (LLMs) show growing promise for scientific discovery, yet basic questions remain about what enables reliable discovery. How can we trace the scientific discovery capacity of LLMs to their training data? We study this question as one of missing probability mass and develop a theoretical account in which monofacts-the facts obse…

## 6. DiabAgent: Toward Agentic Physiological Control

- arXiv: https://arxiv.org/abs/2611.03601
- Published (UTC): 2026-11-02T18:41:02Z
- Topics: LLM, Agent
- Keyword relevance: 25/100
- Authors: Chengxi Li, Shaoxuan Li, Deyao Hong, Qingle Liu, Yi Huang, Puheng Bian, Minzhi Xu, Lanyue Zhang
- Summary source: abstract excerpt
- PDF pages: not processed

As pretraining scales, medical language models have advanced rapidly in clinical question answering. Their ability to achieve effective physiological control through sustained intervention still lacks systematic quantitative evaluation. Type 1 diabetes provides a concrete setting: impaired insulin secretion creates dependence on exogenous insulin,…

## 7. Four Bridges: Measuring Deception Propensity in a Multi-Agent Game

- arXiv: https://arxiv.org/abs/2611.03600
- Published (UTC): 2026-11-02T18:40:47Z
- Topics: Agent
- Keyword relevance: 40/100
- Authors: Raphael Casey, Michael Simeone, Alberto Tosato, Florian Ernst, Kemal El Moujahid, James Tamplin, Tommaso Tosato
- Summary source: abstract excerpt
- PDF pages: not processed

AI agents are increasingly deployed in settings where they interact and coordinate with other agents, yet honesty is mostly measured in single-turn, single-agent benchmarks that pressure the model to deceive. We study deception that emerges in multi-agent interaction without any instruction to deceive. We introduce Kradle, a platform for evaluating…

## 8. FedReady: Bounded Agents for Federation Formation

- arXiv: https://arxiv.org/abs/2611.03586
- Published (UTC): 2026-11-02T18:32:43Z
- Topics: LLM
- Keyword relevance: 15/100
- Authors: Ziyue Xu, Holger R. Roth, Chester Chen, Peter Cnudde
- Summary source: abstract excerpt
- PDF pages: not processed

Federated learning (FL) runtimes standardize aggregation and deployment, but each new study still requires federation formation: selecting task-eligible sites and preparing their local data and task code for federated training or analysis. This preparation recurs when the target changes, while raw records and site-private mappings are excluded from…

## 9. VeriHarm-Bench: Measuring Harmful Success in LLM Coding Agents Verifiably

- arXiv: https://arxiv.org/abs/2611.03575
- Published (UTC): 2026-11-02T18:27:55Z
- Topics: RAG, LLM
- Keyword relevance: 55/100
- Authors: Wei-Lin Chen, Zhepei Wei, Xinyu Zhu, Yu-Min Tseng, Tzu-Han Lin, Yu Meng
- Summary source: abstract excerpt
- PDF pages: not processed

Large language model (LLM) coding agents increasingly operate with shell access, allowing them to write scripts, move files, alter permissions, and modify system configurations. However, an agent may achieve a user's goal while causing unintended harm, such as deleting unrelated files, weakening access controls, or corrupting data, in response to b…

## 10. MCP Tool Poisoning in Agentic AI Frameworks: A Cross-Framework Measurement Study

- arXiv: https://arxiv.org/abs/2611.03555
- Published (UTC): 2026-11-02T18:17:08Z
- Topics: LLM, Agent
- Keyword relevance: 25/100
- Authors: Farooq Shaikh, Biagio Montaruli
- Summary source: abstract excerpt
- PDF pages: not processed

The Model Context Protocol (MCP) lets agentic AI frameworks connect language models to external tool providers, but it carries attacker-controlled content (tool descriptions, schema fields, and response data) into model context without validation. Prior benchmarks measure model compliance with poisoned instructions without confirming real execution…

## 11. Can LLM Agents Be Forward-Deployed Engineers? Requirement Discovery and Delivery for Enterprise Text-to-SQL

- arXiv: https://arxiv.org/abs/2611.03551
- Published (UTC): 2026-11-02T18:13:38Z
- Topics: LLM
- Keyword relevance: 25/100
- Authors: Marianne Menglin Liu, Rongguang Wang, Zheng Wang, Yewen Wang, Leonid Boytsov, Tao Sheng, Sujith Ravi, Dan Roth
- Summary source: abstract excerpt
- PDF pages: not processed

LLM coding agents can increasingly automate model post-training, but whether they can act as forward-deployed engineer (FDE) agents, discovering customer requirements and turning them into deployment decisions, remains unclear. We study this on a real enterprise text-to-SQL engagement: a simulated customer, grounded in the real use case's requireme…

## 12. An Agentic Framework for Automated Power System Studies and Grid Connection Assessment

- arXiv: https://arxiv.org/abs/2611.03534
- Published (UTC): 2026-11-02T18:00:52Z
- Topics: RAG, Agent
- Keyword relevance: 40/100
- Authors: MaoXun Huang, Kshitij Kapoor, Eli Louise
- Summary source: abstract excerpt
- PDF pages: not processed

Connecting new generation and demand to the grid depends on two scarce skills: checking applications against a large, changing body of regulation, and running the network studies that decide where and how a project connects. We present Grid Agents, an AI system that brings both together, and the methodology we use to evaluate it. The Grid Ontology…

## 13. Contrastive Adapter Training and Consensus Knowledge Distillation for Multi-Source-Free Domain Adaptation in Skin Cancer Diagnosis

- arXiv: https://arxiv.org/abs/2611.03528
- Published (UTC): 2026-11-02T17:58:16Z
- Topics: RAG
- Keyword relevance: 15/100
- Authors: Ali Abedi, Q. M. Jonathan Wu, Ning Zhang, Farhad Pourpanah
- Summary source: abstract excerpt
- PDF pages: not processed

Skin cancer diagnosis, particularly differentiating melanoma from benign nevi, is challenging due to the visual similarity between lesions. Although convolutional neural networks (CNNs) and vision transformers (ViTs) have shown promising performance, their effectiveness often deteriorates on data from heterogeneous clinical sources. Conventional do…

## 14. Grading the Unannotated: Insights from the WorkRB Skill Extraction Challenge at RecSys-HR 2026

- arXiv: https://arxiv.org/abs/2611.03525
- Published (UTC): 2026-11-02T17:57:53Z
- Topics: LLM
- Keyword relevance: 15/100
- Authors: Warre Veys, Luis Gasco, Jens-Joris Decorte
- Summary source: abstract excerpt
- PDF pages: not processed

Skill extraction benchmarks score models against a few human-annotated positives and treat every other skill in the vocabulary as equally wrong. At the scale of ESCO (13,939 skills) this binary view can reward models that rank the annotated positive high for the wrong reason, and hides semantically nonsensical predictions. The WorkRB Challenge at R…

## 15. PanoTac: A Dense Three-Axis Tactile Sensor for Robust Touch-Centric Manipulation

- arXiv: https://arxiv.org/abs/2611.03520
- Published (UTC): 2026-11-02T17:55:07Z
- Topics: RAG
- Keyword relevance: 15/100
- Authors: Binglin, Wang, Xiaole, Jiang, Zicheng Teng, Xinqi Liu, Yunzhu Li, Lerrel Pinto
- Summary source: abstract excerpt
- PDF pages: not processed

Contact-rich manipulation benefits from tactile feedback that captures both detailed contact geometry and interaction forces. When scooping grains, contact patterns help infer spoon orientation, while resistance transmitted through the grasp guides motion. To provide these complementary sensing capabilities, we present PanoTac, a low-cost, complian…

## 16. The SIMPLE Law for Energy Cost of LLM Inference

- arXiv: https://arxiv.org/abs/2611.03330
- Published (UTC): 2026-11-02T15:51:46Z
- Topics: LLM, Agent
- Keyword relevance: 40/100
- Authors: Hiari Pizzini Cavagna, Andrea Proia, Daniele Cesarini, Zeynep Kiziltan, Andrea Bartolini
- Summary source: pending_fulltext
- PDF pages: not processed

한국어 본문 요약 대기 중 (OPENAI_API_KEY 필요)

## 17. From Local Skills to Long-Horizon Web Tasks: Progressive Skill Exploration for LLM Web Agents

- arXiv: https://arxiv.org/abs/2611.03116
- Published (UTC): 2026-11-02T13:32:59Z
- Topics: LLM, Agent
- Keyword relevance: 40/100
- Authors: Xueyang Feng, Xiaohe Bo, Xu Chen, Quanyu Dai, Feng Wen
- Summary source: pending_fulltext
- PDF pages: not processed

한국어 본문 요약 대기 중 (OPENAI_API_KEY 필요)

## 18. PACERec: Progressive Adaptation of LLM Item Embeddings with Collaborative Evidence for Recommendation

- arXiv: https://arxiv.org/abs/2611.03068
- Published (UTC): 2026-11-02T12:55:49Z
- Topics: LLM
- Keyword relevance: 40/100
- Authors: Junzhao Huang, Xi Wu, Zihan Wang, Zijing Wang, Ming Wang, Kang Liu, Xiaocui Yang, Shi Feng
- Summary source: pending_fulltext
- PDF pages: not processed

한국어 본문 요약 대기 중 (OPENAI_API_KEY 필요)

## 19. Towards a Trustworthy and Governable Internet of Agentics: An Architectural Perspective on Protocols, Systems, and Services

- arXiv: https://arxiv.org/abs/2611.03066
- Published (UTC): 2026-11-02T12:54:14Z
- Topics: LLM, Agent
- Keyword relevance: 45/100
- Authors: Haoyi Xiong, Yi Liu, Jiang Bian, Peng Diao, Bin Zhu, Tingting Hu, Yi Wang, Sumi Helal
- Summary source: pending_fulltext
- PDF pages: not processed

한국어 본문 요약 대기 중 (OPENAI_API_KEY 필요)

## 20. BLPO: Beyond-Local Policy Optimization for Long-Horizon LLM Agents

- arXiv: https://arxiv.org/abs/2611.03005
- Published (UTC): 2026-11-02T12:10:05Z
- Topics: LLM
- Keyword relevance: 40/100
- Authors: Xuanren Chen, Chongyang Tao, Wenpeng Hu, Yong Wang, Bo Deng, Xinlei Zheng, Shuai Ma
- Summary source: pending_fulltext
- PDF pages: not processed

한국어 본문 요약 대기 중 (OPENAI_API_KEY 필요)

## 21. SpecOPD: Branch-Parallel On-Policy Distillation for Speculative Decoding

- arXiv: https://arxiv.org/abs/2611.02846
- Published (UTC): 2026-11-02T09:47:06Z
- Topics: LLM, Agent
- Keyword relevance: 30/100
- Authors: Tianyu Liu, Jun Zhang, Wenjie Huang, Yuhao Shen, Tianqi Xu, Xinyue Hao, Hongyaoxing Gu, Xuyang Liu
- Summary source: pending_fulltext
- PDF pages: not processed

한국어 본문 요약 대기 중 (OPENAI_API_KEY 필요)

## 22. Discovering hierarchical governing equations for community-structured complex network dynamics with LLM agents

- arXiv: https://arxiv.org/abs/2611.02816
- Published (UTC): 2026-11-02T09:19:22Z
- Topics: LLM
- Keyword relevance: 40/100
- Authors: Jinlei Zhang, Zixuan Zhang, Hao Qiu, Feng Chen, Jiateng Yin, Xiaoyong Yan, Xiaolei Ma, Hao Sun
- Summary source: pending_fulltext
- PDF pages: not processed

한국어 본문 요약 대기 중 (GEMINI_API_KEY 필요)

## 23. Predictive Safety Guardrails Do Not Always Make LLM Agents Safer

- arXiv: https://arxiv.org/abs/2611.02815
- Published (UTC): 2026-11-02T09:19:22Z
- Topics: LLM
- Keyword relevance: 40/100
- Authors: Weixiang Zhao, Zhihao Liu, Guancheng Li, Yanyan Zhao, Bing Qin, Ting Liu
- Summary source: pending_fulltext
- PDF pages: not processed

한국어 본문 요약 대기 중 (GEMINI_API_KEY 필요)
