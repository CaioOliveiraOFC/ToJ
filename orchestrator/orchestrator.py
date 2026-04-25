# orchestrator/orchestrator.py

import asyncio
from dotenv import load_dotenv
from google.adk.agents import ParallelAgent, LlmAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part

from orchestrator.agents.architect_agent import architect_agent
from orchestrator.agents.data_agent import data_agent
from orchestrator.agents.ux_agent import ux_agent

load_dotenv()

APP_NAME = "toj_studio"

# ── 1. TIME PARALELO (os 3 agentes rodam ao mesmo tempo) ──────────────────────
studio_team = ParallelAgent(
    name="StudioTeam",
    description="Time de desenvolvimento paralelo do ToJ",
    sub_agents=[architect_agent, data_agent, ux_agent],
)

# ── 2. AGENTE DE REVISÃO (roda DEPOIS do paralelo, consolida os resultados) ───
reviewer = LlmAgent(
    name="Reviewer",
    model="gemini-2.5-flash",
    instruction="""
    Você é o Diretor do estúdio ToJ. Os 3 agentes especializados concluíram suas tarefas
    e os resultados estão disponíveis no estado da sessão.
    
    Com base no que foi produzido pelo time, gere um relatório de sprint com:
    1. O que cada agente fez (Architect, DataDesigner, UXNarrative)
    2. Possíveis conflitos de interface entre os módulos
    3. Próximos passos recomendados para o próximo sprint
    """,
    output_key="sprint_report",
)

# ── 3. PIPELINE COMPLETO: Paralelo → Revisão ──────────────────────────────────
pipeline = SequentialAgent(
    name="ToJDirector",
    description="Pipeline completo: executa o time paralelo e depois revisa",
    sub_agents=[studio_team, reviewer],
)

# ── 4. RUNNER ─────────────────────────────────────────────────────────────────
session_service = InMemorySessionService()
runner = Runner(
    agent=pipeline,
    app_name=APP_NAME,
    session_service=session_service,
)


async def run_sprint(task: str, session_id: str = "sprint-01"):
    """
    Executa um sprint completo com os 3 agentes em paralelo.
    
    Args:
        task: A tarefa/objetivo do sprint (ex: "Implementar sistema de magia")
        session_id: ID da sessão para rastrear histórico
    """
    print(f"\n🚀 Iniciando Sprint | Tarefa: {task}\n{'='*60}")

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id="bigfi",
        session_id=session_id,
    )

    user_message = Content(
        role="user",
        parts=[Part(text=task)]
    )

    async for event in runner.run_async(
        user_id="bigfi",
        session_id=session_id,
        new_message=user_message,
    ):
        # Mostrar outputs dos agentes em tempo real
        if event.author and event.content:
            author = event.author
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    print(f"\n[{author}] → {part.text[:300]}...")

    # Recuperar sessão e mostrar relatório final
    final_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id="bigfi",
        session_id=session_id,
    )

    print("\n" + "="*60)
    print("📊 RELATÓRIO DO SPRINT")
    print("="*60)
    if final_session and final_session.state:
        report = final_session.state.get("sprint_report", "Sem relatório gerado.")
        print(report)

    return final_session


if __name__ == "__main__":
    # Exemplo de uso — mude a task para o que quiser trabalhar no sprint
    SPRINT_TASK = """
    Sprint 04 — Análise de Estabilidade e Game Design (Auto-Test):
    
    O Bot de simulação executou uma jogatina até o Nível 40 e gerou um log na pasta `reports/`. 
    Cada agente deve ler o relatório de teste mais recente gerado e atuar na sua área:
    
    - Architect: Verifique no arquivo `reports/sim_report_*.txt` se houve alguma exceção (Traceback) ou crash sistêmico listado. Identifique a origem no código (`game.py`, `map.py`, `classes.py`, etc) e proponha/implemente a correção.
    
    - DataDesigner: Analise as métricas do relatório ("Ações Simuladas", "Lutas", "Nível Alcançado"). Se o bot precisou de poucas ações para chegar no nível 40, os monstros estão muito fracos ou dão XP demais. Ajuste a curva de experiência e os atributos base dos inimigos.
    
    - UXNarrative: Confira se a supressão da interface ocorreu sem deixar pontas soltas na renderização. Analise também o relatório e proponha como podemos exibir as estatísticas do log final no terminal do jogo de forma mais bonita quando a simulação acabar.
    """

    asyncio.run(run_sprint(SPRINT_TASK, session_id="sprint-04"))