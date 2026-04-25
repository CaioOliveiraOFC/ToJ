# orchestrator/tools/file_tools.py

import os
from pathlib import Path
from google.adk.tools import FunctionTool

BASE_DIR = Path(__file__).parent.parent.parent  # ~/ToJ/

# Mapeamento de domínio por agente
DOMAIN_MAP = {
    "Architect": [
        "game.py",
        "toj_source/game_logic.py",
        "toj_source/map.py",
        "toj_source/save_manager.py",
        "toj_source/classes.py",
    ],
    "DataDesigner": [
        "toj_source/items.py",
        "toj_source/armor.py",
        "toj_source/skills.py",
        "toj_source/spell.py",
        "toj_source/shop.py",
        "toj_source/math_operations.py",
    ],
    "UXNarrative": [
        "toj_source/toj_menu.py",
        "toj_source/interactions.py",
        "toj_source/guesser.py",
    ],
}

def _check_permission(agent_name: str, filepath: str) -> bool:
    """Verifica se o agente tem permissão de escrita no arquivo."""
    allowed = DOMAIN_MAP.get(agent_name, [])
    return any(filepath.endswith(f) or f in filepath for f in allowed)


def read_file(filepath: str) -> dict:
    """
    Lê o conteúdo de um arquivo do projeto ToJ.
    Qualquer agente pode ler qualquer arquivo.

    Args:
        filepath: Caminho relativo ao projeto (ex: 'toj_source/map.py')

    Returns:
        dict com 'content' (str) ou 'error' (str)
    """
    full_path = BASE_DIR / filepath
    if not full_path.exists():
        return {"error": f"Arquivo '{filepath}' não encontrado."}
    try:
        return {"content": full_path.read_text(encoding="utf-8")}
    except Exception as e:
        return {"error": str(e)}


def write_file(agent_name: str, filepath: str, content: str) -> dict:
    """
    Escreve conteúdo em um arquivo do projeto.
    Só funciona se o arquivo estiver no domínio do agente.

    Args:
        agent_name: Nome do agente (ex: 'Architect')
        filepath: Caminho relativo ao projeto
        content: Conteúdo completo a escrever

    Returns:
        dict com 'success' (bool) e 'message' (str)
    """
    if not _check_permission(agent_name, filepath):
        return {
            "success": False,
            "message": f"❌ PERMISSÃO NEGADA: {agent_name} não pode escrever em '{filepath}'."
        }
    full_path = BASE_DIR / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        full_path.write_text(content, encoding="utf-8")
        return {"success": True, "message": f"✅ '{filepath}' atualizado com sucesso."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def list_domain_files(agent_name: str) -> dict:
    """
    Lista os arquivos que pertencem ao domínio do agente.

    Args:
        agent_name: Nome do agente

    Returns:
        dict com 'files' (list)
    """
    files = DOMAIN_MAP.get(agent_name, [])
    return {"files": files, "agent": agent_name}


# Registrar como FunctionTools para o ADK
read_file_tool = FunctionTool(func=read_file)
write_file_tool = FunctionTool(func=write_file)
list_domain_tool = FunctionTool(func=list_domain_files)

def read_latest_report() -> dict:
    """
    Lê o conteúdo do relatório de simulação mais recente na pasta 'reports/'.
    Pega as 500 primeiras linhas (para contexto e stats iniciais) e as 1000 últimas (para logs de crash/fim).
    """
    reports_dir = BASE_DIR / "reports"
    if not reports_dir.exists():
        return {"error": "Pasta 'reports/' não encontrada."}
    
    files = list(reports_dir.glob("sim_report_*.txt"))
    if not files:
        return {"error": "Nenhum relatório encontrado na pasta 'reports/'."}
        
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    
    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if len(lines) <= 1500:
            content = "".join(lines)
        else:
            content = "".join(lines[:500]) + "\n\n... [MIOLO OMITIDO DEVIDO AO TAMANHO] ...\n\n" + "".join(lines[-1000:])
            
        return {"content": content, "filename": latest_file.name}
    except Exception as e:
        return {"error": str(e)}

read_latest_report_tool = FunctionTool(func=read_latest_report)