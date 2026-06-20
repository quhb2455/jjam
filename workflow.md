# Paper Agent Harness Workflow 정리

## 프로젝트 목표

이 프로젝트는 AI 논문을 입력으로 받아 구현에 필요한 정보를 추출하고, 구현 계획, Tool/Skill 계획, 검증 결과, Reviewer 평가, 최종 보고서를 생성하는 Codex 기반 Agent Harness MVP이다.

초기 목표는 복잡한 멀티 에이전트 시스템이 아니라, 단일 실행 흐름을 가진 하네스를 먼저 만들고 이후 OCR parser, test runner, code generation adapter를 교체 가능하게 붙이는 것이다. 현재는 실제 PDF 텍스트 추출과 선택적 LLM 논문 분석까지 연결되어 있다.

## 현재 실행 방식

현재 사용자는 CLI로 실행한다.

```bash
uv run paper-agent run --paper examples/sample_paper.md --out runs/sample_run
```

PDF 입력도 같은 명령 구조로 실행한다.

```bash
uv run paper-agent run --paper test_paper.pdf --out runs/pdf_run
```

LLM 기반 논문 분석이 필요하면 `.env`에 LLM 설정을 기록하고 `--llm-provider openai-compatible`을 지정한다. 기본값은 휴리스틱 분석이므로 `.env`가 있어도 명시적으로 LLM provider를 켜지 않으면 외부 호출을 하지 않는다.

```bash
PAPER_AGENT_LLM_API_KEY=...
PAPER_AGENT_LLM_MODEL=YOUR_MODEL
PAPER_AGENT_LLM_BASE_URL=https://api.openai.com/v1
PAPER_AGENT_LLM_TIMEOUT_SECONDS=60
```

```bash
uv run paper-agent run \
  --paper test_paper.pdf \
  --out runs/pdf_llm_run \
  --llm-provider openai-compatible
```

다른 dotenv 파일을 쓰려면 `--env-file path/to/.env`를 지정한다.

CLI는 유지되어 있지만 내부 실행 엔진은 LangGraph 기반이다.

```text
paper-agent CLI
  -> Orchestrator facade
  -> PaperAgentGraph(StateGraph)
  -> 각 stage node 실행
  -> runs/<run_id>/ 산출물 생성
```

## LangGraph 노드 흐름

현재 graph는 `src/paper_agent/graph.py`에 정의되어 있다.

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
  -> END
```

각 노드는 `PaperAgentState`를 입력으로 받고, 새 state 조각을 반환한다. 산출물 파일 목록은 state의 `files`에 누적된다.

## 주요 파일 역할

- `src/paper_agent/cli.py`: CLI 진입점이다.
- `src/paper_agent/orchestrator.py`: 기존 API 호환을 위한 facade이다. 실제 실행은 `PaperAgentGraph`에 위임한다.
- `src/paper_agent/graph.py`: LangGraph `StateGraph` 정의와 node 실행 로직이다.
- `src/paper_agent/schemas.py`: 단계 사이에서 전달되는 dataclass schema이다.
- `src/paper_agent/paper_analysis.py`: 논문 입력을 읽고 분석 결과를 만든다. PDF는 `pypdf`로 실제 텍스트를 추출하고, 분석은 기본 휴리스틱 또는 OpenAI-compatible LLM client로 수행한다.
- `src/paper_agent/planning.py`: 분석 결과를 구현 계획으로 변환한다.
- `src/paper_agent/tool_registry.py`: 기본 Tool 후보와 추가 Tool 검토 원칙을 기록한다.
- `src/paper_agent/skill_registry.py`: 기본 Skill 정의를 제공한다.
- `src/paper_agent/code_implementation.py`: 현재는 실제 논문별 코드를 생성하지 않고 prototype notes와 assumptions를 쓴다.
- `src/paper_agent/validation.py`: 필수 산출물이 존재하고 비어 있지 않은지 확인한다.
- `src/paper_agent/reviewer.py`: Reviewer Sub-agent 역할을 하는 결정적 평가 모듈이다.
- `src/paper_agent/reporting.py`: 최종 보고서를 작성한다.
- `src/paper_agent/readme_writer.py`: run별 README를 작성한다.

## 생성 산출물

실행 후 출력 디렉터리에 다음 파일이 생성된다.

- `paper_summary.md`
- `implementation_spec.md`
- `implementation_plan.md`
- `tooling_plan.md`
- `prototype_implementation.md`
- `assumptions.md`
- `validation_result.md`
- `review_report.md`
- `paper_code_alignment_matrix.md`
- `revision_plan.md`
- `final_report.md`
- `README.generated.md`

## 지금까지의 중요한 결정

1. CLI는 유지한다.
   - 사용자 경험을 깨지 않기 위해 `paper-agent run ...` 명령은 그대로 둔다.
   - 내부 Orchestrator만 LangGraph 실행 그래프로 교체했다.

2. LangGraph는 orchestration을 담당한다.
   - 단계 순서, state 전달, revision decision 같은 workflow 제어를 담당한다.
   - 현재는 선형 graph에 가깝지만, 나중에 validation/reviewer 결과에 따라 수정 루프를 추가할 수 있다.

3. LLM 호출은 명시적으로 켰을 때만 수행한다.
   - 기본 실행은 결정적 휴리스틱 분석이다.
   - `--llm-provider openai-compatible`을 지정하면 `.env` 또는 CLI 옵션에서 API 키, 모델, base URL, timeout을 읽어 chat completions API를 호출한다.
   - LLM 분석 결과는 기존 `PaperAnalysisResult` schema로 파싱되어 뒤 단계 계약을 유지한다.

4. PDF parser는 실제 텍스트 추출까지 연동했다.
   - `pypdf`를 사용해 extractable text를 페이지 단위로 읽는다.
   - 스캔 이미지형 PDF는 아직 OCR 대상이며, 이 경우 별도 OCR Tool 또는 parser adapter가 필요하다.

5. `.env`는 로컬 LLM 설정 파일이다.
   - `.env`는 `.gitignore`에 포함되어 실제 secret을 커밋하지 않는다.
   - `PAPER_AGENT_LLM_API_KEY`, `PAPER_AGENT_LLM_MODEL`, `PAPER_AGENT_LLM_BASE_URL`, `PAPER_AGENT_LLM_TIMEOUT_SECONDS`를 지원한다.
   - 이미 셸 환경변수에 값이 있으면 그 값을 우선하고, `.env`는 비어 있는 값만 보완한다.

6. 실제 논문별 Python 코드 생성은 아직 하지 않는다.
   - 논문에 없는 구현을 임의로 주장하지 않기 위해 현재는 `prototype_implementation.md`와 `assumptions.md`를 생성한다.

## 테스트 방법

```bash
uv run pytest
```

현재 기대 결과는 다음과 같다.

```text
9 passed
```

샘플 CLI smoke test는 다음과 같이 실행한다.

```bash
uv run paper-agent run --paper examples/sample_paper.md --out runs/sample_run
```

## 다음에 이어서 구현하기 좋은 항목

1. `PaperAgentState`에 단계별 status와 error 정보를 추가한다.
2. `decide_revision` 노드를 conditional edge로 확장해 validation 실패 시 구현 또는 계획 단계로 되돌린다.
3. LLM 분석 client를 provider별 adapter 구조로 분리한다.
4. 스캔 PDF 처리를 위한 OCR parser adapter를 추가한다.
5. `code_implementation.py`를 실제 코드 생성 단계와 안전한 patch/apply 단계로 분리한다.
6. Reviewer 결과에 점수 rubric을 추가한다.
7. 설정 파일을 도입해 model provider, parser backend, test command를 분리한다.

## 주의 사항

- 논문에 명시되지 않은 내용을 구현했다고 주장하지 않는다.
- 실패한 테스트나 검증 결과를 숨기지 않는다.
- 불필요하게 Tool을 새로 만들지 않는다.
- 멀티 에이전트 구조는 필요한 시점까지 도입하지 않는다.
- README와 최종 보고서 없이 완료로 간주하지 않는다.