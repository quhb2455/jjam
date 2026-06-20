# Codex Handoff 방향 전환 TODO

## 배경

현재 프로젝트는 AI 논문을 입력으로 받아 구현 목표, 구현 계획, Tool/Skill 계획, 검증 결과, Reviewer 평가, 최종 보고서를 생성하는 Codex 기반 Agent Harness MVP이다.

초기 구현 과정에서 선택적 OpenAI-compatible LLM API 호출 경로가 추가되어 있다. 하지만 새 방향성은 API 키를 가진 개발자가 직접 LLM API를 호출하는 구조가 아니라, ChatGPT Plus/Codex 사용자가 저장소를 클론한 뒤 Codex에게 프로젝트 규칙과 산출물을 따라 작업시키는 구조이다.

따라서 프로젝트의 중심을 다음처럼 전환한다.

```text
기존 방향:
paper-agent CLI가 필요 시 외부 LLM API를 직접 호출한다.

새 방향:
paper-agent CLI는 Codex가 따라갈 수 있는 명시적 산출물과 작업 지시서를 생성한다.
사용자는 생성된 산출물을 Codex에게 주고 구현, 검증, 리뷰를 진행한다.
```

## 현재까지 구현된 것

### 1. 기본 Python 패키지 구조

- `pyproject.toml` 기반 Python 패키지 구성
- `paper-agent` CLI entrypoint 정의
- `src/paper_agent/` 아래 stage별 모듈 분리
- `uv` 기반 실행 및 테스트 환경 구성

### 2. CLI 실행 흐름

- `paper-agent run --paper ... --out ...` 명령 제공
- Markdown, plain text, PDF 입력 경로 지원
- 실행 결과를 지정한 output directory에 artifact로 저장
- Python module 방식 실행도 지원

```bash
uv run paper-agent run --paper examples/sample_paper.md --out runs/sample_run
uv run python -m paper_agent.cli run --paper examples/sample_paper.md --out runs/sample_run
```

### 3. PaperReader

- `.md`, `.txt` 입력 파일 읽기 지원
- `.pdf` 입력 파일 읽기 지원
- PDF는 `pypdf`를 사용해 extractable text를 페이지 단위로 추출
- 스캔 이미지형 PDF는 아직 OCR 대상이며 현재는 지원하지 않음

### 4. PaperAnalyzer

- 기본 휴리스틱 기반 논문 분석 구현
- 제목, 요약, 핵심 기여, 구현 대상, 입력 데이터, 출력 형식, 필요한 모델/라이브러리, 평가 방법, 의사코드/수식, 미정 사항, MVP 범위, 제외 범위 추출
- 분석 결과를 `PaperAnalysisResult` schema로 전달
- `paper_summary.md`, `implementation_spec.md` 생성

### 5. 선택적 LLM 분석 경로

- `OpenAICompatibleAnalysisClient` 구현
- OpenAI-compatible chat completions API 호출 가능
- `.env` 또는 CLI 옵션으로 API key, model, base URL, timeout 설정 가능
- `--llm-provider openai-compatible` 지정 시 LLM 분석 사용

주의: 이 부분은 새 방향성과 충돌하므로 제거하거나 optional/experimental adapter로 격리해야 한다.

### 6. LangGraph 기반 실행 엔진

- `PaperAgentGraph` 구현
- `StateGraph` 기반 node 흐름 구성
- `Orchestrator`는 facade로 유지
- 현재 실행 흐름:

```text
read_paper
  -> analyze_paper
  -> plan_implementation
  -> plan_tooling
  -> implement_code
  -> validate_outputs
  -> review_alignment
  -> decide_revision
  -> write_final_report
  -> write_run_readme
```

### 7. ImplementationPlanner

- 분석 결과를 구현 계획으로 변환
- `implementation_plan.md` 생성
- 구현 대상 component, 파일 경계, stage 순서, 검증 전략, 제외 범위 기록

### 8. Skill Registry

- 기본 Skill 목록 정의
- 현재 기본 Skill:
  - `paper-analysis`
  - `implementation-planning`
  - `code-implementation`
  - `validation`
  - `paper-code-review`
  - `final-report-generation`
  - `readme-generation`

### 9. Tool Registry

- 기본 Tool 후보 정의
- 현재 기본 Tool 후보:
  - filesystem tool
  - git tool
  - python execution tool
  - test runner tool
  - package inspection tool
  - paper parser tool
  - report writer tool
- 추가 Tool 검토 원칙을 `tooling_plan.md`에 기록

### 10. CodeImplementer

- 현재는 실제 논문별 코드를 자동 생성하지 않음
- MVP 구현 notes와 assumptions를 artifact로 생성
- 생성 파일:
  - `prototype_implementation.md`
  - `assumptions.md`
- 논문에 없는 구현을 임의로 주장하지 않도록 설계

### 11. Validator

- 필수 artifact 존재 여부 확인
- 비어 있는 artifact 확인
- 검증 결과를 `validation_result.md`에 기록
- 실패한 검증 결과를 숨기지 않는 방향으로 구현

### 12. Reviewer Sub-agent 모듈

- 별도 멀티 에이전트 프로세스가 아니라 결정적 reviewer 모듈로 구현
- 논문 분석 결과, 구현 계획, 구현 산출물, 검증 결과를 비교
- 생성 파일:
  - `review_report.md`
  - `paper_code_alignment_matrix.md`
  - `revision_plan.md`
- MVP scaffold를 실제 논문 구현 완료로 과장하지 않도록 설계

### 13. FinalReporter

- 최종 보고서 생성
- 생성 파일:
  - `final_report.md`
- 포함 내용:
  - paper summary
  - implementation target summary
  - implemented content
  - paper-to-code mapping
  - used Skills
  - used Tools
  - evaluation results
  - differences from paper
  - excluded items
  - future work
  - execution method
  - environment setup
  - configuration notes

### 14. ReadmeWriter

- run별 README 생성
- 생성 파일:
  - `README.generated.md`
- 실행 방법, 산출물 목록, 한계 기록

### 15. 문서

- `README.md`
- `workflow.md`
- `docs/workflow.md`
- `docs/system_design.md`
- `docs/evaluation.md`
- `docs/pipeline.svg`
- `AGENTS.md`
- `PLANS.md`
- `.agents/skills/*/SKILL.md`

### 16. 테스트

- CLI smoke test
- Orchestrator artifact 생성 테스트
- PDF text extraction 테스트
- 선택적 LLM client 연결 테스트
- 현재 README 기준 기대 테스트 결과:

```text
9 passed
```

## 새 방향성

### 목표

ChatGPT Plus/Codex 사용자가 별도 OpenAI API key 없이 저장소를 클론한 뒤, Codex에게 프로젝트 규칙과 생성된 artifact를 따라 작업시키는 구조로 전환한다.

### 핵심 원칙

- 프로젝트가 외부 LLM API를 직접 호출하지 않는다.
- 기본 경로는 네트워크 호출 없이 동작한다.
- CLI는 Codex가 따라갈 수 있는 명시적 작업 지시 artifact를 생성한다.
- Codex가 판단해야 하는 부분은 숨기지 않고 별도 TODO, assumption, revision artifact에 기록한다.
- 구현 여부와 논문 주장 여부를 분리한다.
- ChatGPT Plus 구독과 API 사용은 별도라는 전제를 문서에 명확히 반영한다.

## 수정해야 하는 것

### 1. LLM API 호출 경로 제거 또는 격리

대상 파일:

- `src/paper_agent/cli.py`
- `src/paper_agent/paper_analysis.py`
- `pyproject.toml`
- `tests/test_cli.py`
- `tests/test_paper_analysis.py`
- `README.md`
- `workflow.md`
- `docs/workflow.md`

해야 할 일:

- `--llm-provider` 옵션 제거 또는 deprecated 처리
- `--llm-model`, `--llm-base-url`, `--llm-api-key-env`, `--llm-timeout-seconds` 제거 또는 experimental로 이동
- `OpenAICompatibleAnalysisClient` 제거 또는 별도 optional adapter로 격리
- 기본 dependency에서 `httpx` 제거 검토
- LLM env file 테스트 제거 또는 새 목적에 맞게 수정

이유:

- ChatGPT Plus 사용자는 API key를 자동으로 갖는 것이 아니다.
- 현재 구조는 API billing과 ChatGPT subscription을 혼동하게 만들 수 있다.
- 새 목표는 Codex interactive workflow이지 API 호출 자동화가 아니다.

### 2. Codex handoff artifact 추가

새 artifact 후보:

- `codex_task.md`

포함해야 할 내용:

- 입력 논문 경로
- output directory
- 논문 요약
- 구현 대상
- 반드시 읽어야 하는 artifact 목록
- 사용할 Skill 목록
- 사용할 Tool 목록
- 구현 단계 checklist
- 검증 단계 checklist
- Reviewer 단계 checklist
- assumptions 기록 규칙
- 완료 조건
- 금지 사항

이유:

- 사용자가 Codex에게 바로 전달할 수 있는 단일 작업 지시서가 필요하다.
- Codex가 프로젝트 규칙을 임의 해석하지 않도록 stage별 입출력 계약을 명확히 해야 한다.

### 3. `CodeImplementer` 역할 재정의

대상 파일:

- `src/paper_agent/code_implementation.py`

해야 할 일:

- 현재 `prototype_implementation.md` 중심 구조를 Codex handoff 중심으로 변경
- 실제 구현을 하지 않은 상태라면 “구현 완료”처럼 보이는 표현 제거
- `assumptions.md`에 MVP 결정과 논문 주장 차이를 명확히 기록
- `codex_task.md` 또는 별도 implementation handoff 파일 생성 책임 추가 검토

이유:

- 새 구조에서는 코드 구현의 주체가 CLI가 아니라 Codex interactive session이다.
- CLI는 구현을 위한 안전한 작업 패키지를 만들어야 한다.

### 4. `revision_plan.md`를 Codex 재작업 요청 형식으로 개선

대상 파일:

- `src/paper_agent/reviewer.py`

해야 할 일:

- revision item을 Codex에게 그대로 줄 수 있는 action item 형식으로 작성
- 각 item에 근거 artifact와 expected output을 포함
- MVP scaffold와 paper-accurate implementation의 차이를 명확히 표시

이유:

- Reviewer 결과가 다음 Codex 작업으로 자연스럽게 이어져야 한다.

### 5. README 재작성

대상 파일:

- `README.md`

해야 할 일:

- “LLM 분석 실행” 섹션 제거 또는 optional advanced section으로 이동
- 기본 사용 흐름을 다음처럼 변경:

```text
1. repository clone
2. uv sync --dev
3. paper-agent run --paper ... --out ...
4. runs/.../codex_task.md 확인
5. Codex에게 AGENTS.md와 codex_task.md를 따라 구현 요청
6. 테스트 실행
7. reviewer/revision artifact 확인
```

- ChatGPT Plus/Codex 사용자는 API key 없이 기본 workflow를 사용할 수 있음을 명시
- API platform billing과 ChatGPT subscription이 별도임을 주의 사항으로 명시

이유:

- 사용자가 프로젝트를 처음 봤을 때 기대하는 사용 방식이 바뀌어야 한다.

### 6. workflow 문서 수정

대상 파일:

- `workflow.md`
- `docs/workflow.md`
- `docs/system_design.md`

해야 할 일:

- LLM-backed run 설명 제거
- Codex handoff run 설명 추가
- “프로그램이 AI를 호출한다”가 아니라 “프로그램이 Codex 실행 지시서를 만든다”로 설명 변경
- Extension Point에서 LLM-backed analyzer는 optional/advanced로 낮춤

이유:

- 내부 개발 문서와 README가 같은 방향을 가리켜야 한다.

### 7. pipeline diagram 수정

대상 파일:

- `docs/pipeline.svg`

해야 할 일:

- External LLM 박스 제거
- OpenAI-compatible chat completions 문구 제거
- Codex handoff artifact 또는 interactive Codex execution 단계 추가

이유:

- 현재 다이어그램은 외부 LLM API 호출을 공식 구조처럼 보여준다.

### 8. 테스트 수정

대상 파일:

- `tests/test_cli.py`
- `tests/test_paper_analysis.py`
- `tests/test_orchestrator.py`

해야 할 일:

- LLM env loading 테스트 제거
- fake LLM client 테스트 제거 또는 analyzer extension test로 축소
- `codex_task.md` 생성 테스트 추가
- 기본 CLI 실행이 외부 network/API 설정 없이 완료되는지 테스트
- Orchestrator가 새 필수 artifact를 생성하는지 테스트

이유:

- 테스트가 새 제품 방향을 보호해야 한다.

### 9. sample runs 재생성

대상 디렉터리:

- `runs/sample_run/`
- `runs/sample_run_uv/`
- `runs/sample_run_langgraph/`

해야 할 일:

- 기존 LLM 관련 문구 제거
- 새 `codex_task.md` 포함
- `revision_plan.md`, `final_report.md`, `README.generated.md` 내용 갱신

이유:

- 예제 산출물이 오래된 방향을 보여주면 사용자가 혼란스러워진다.

### 10. AGENTS.md 보강

대상 파일:

- `AGENTS.md`

해야 할 일:

- Codex handoff artifact를 기본 산출물로 추가
- “프로젝트는 기본 경로에서 외부 LLM API를 호출하지 않는다” 규칙 추가
- ChatGPT/Codex interactive usage를 전제로 한 완료 조건 추가

이유:

- Codex가 저장소 규칙을 읽고 같은 방향으로 작업하도록 만들어야 한다.

## 제안하는 새 artifact 구조

```text
runs/<run_id>/
  paper_summary.md
  implementation_spec.md
  implementation_plan.md
  tooling_plan.md
  codex_task.md
  prototype_implementation.md
  assumptions.md
  validation_result.md
  review_report.md
  paper_code_alignment_matrix.md
  revision_plan.md
  final_report.md
  README.generated.md
```

## `codex_task.md` 초안 구조

```markdown
# Codex Task

## Objective

## Paper Input

## Required Context

## Implementation Targets

## Required Skills

## Required Tools

## Step-by-step Work Plan

## Assumption Rules

## Validation Commands

## Review Requirements

## Done Criteria

## Prohibited Claims
```

## 우선순위

### P0: 방향성 충돌 제거

- LLM API 호출 경로 제거 또는 격리
- README에서 LLM-backed run 기본 안내 제거
- 테스트에서 LLM env 의존 제거

### P1: Codex handoff 구조 추가

- `codex_task.md` 생성
- Orchestrator artifact 목록에 추가
- 테스트 추가
- run별 README에 Codex 사용 흐름 추가

### P2: 문서와 샘플 정리

- `workflow.md`, `docs/workflow.md`, `docs/system_design.md` 수정
- `docs/pipeline.svg` 수정
- sample run 재생성

### P3: 품질 개선

- Reviewer revision item을 Codex action format으로 개선
- Skill 문서에 expected artifact format 추가
- validation 결과에 테스트 명령과 실행 상태를 더 구체적으로 기록

## 작업 순서 제안

1. `codex_task.md` schema를 먼저 확정한다.
2. `CodeImplementer` 또는 새 writer class에서 `codex_task.md`를 생성한다.
3. Orchestrator/LangGraph artifact 목록에 `codex_task.md`를 포함한다.
4. LLM CLI 옵션과 `OpenAICompatibleAnalysisClient`를 제거 또는 격리한다.
5. 테스트를 새 artifact 기준으로 수정한다.
6. README를 새 사용자 흐름으로 재작성한다.
7. workflow 문서와 system design 문서를 갱신한다.
8. sample run을 재생성한다.
9. 전체 테스트를 실행한다.
10. 남은 LLM/API 관련 문구를 `rg`로 검색해 정리한다.

## 완료 조건

- 기본 실행 경로에서 외부 LLM API 호출이 없다.
- ChatGPT Plus/Codex 사용자가 API key 없이 README 흐름을 따라갈 수 있다.
- `paper-agent run` 실행 시 Codex에게 전달 가능한 `codex_task.md`가 생성된다.
- 모든 필수 artifact가 생성된다.
- 테스트가 통과한다.
- 문서에서 ChatGPT subscription과 API usage를 혼동시키는 표현이 제거된다.
- Reviewer와 final report가 MVP scaffold를 실제 논문 구현 완료로 과장하지 않는다.

